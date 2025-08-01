from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
import base64
import pytest
import asyncio
import time
import types

from services.insight.app import app
import services.insight.app as insight_mod

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_ready():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"ready": True}


def test_options_respects_ui_origin(monkeypatch):
    monkeypatch.setenv("UI_ORIGIN", "http://ui.example")
    import importlib
    import services.insight.app as ins

    ins = importlib.reload(ins)
    local_client = TestClient(ins.app)
    r = local_client.options(
        "/generate-insights",
        headers={
            "Origin": "http://ui.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://ui.example"


def test_generate_insights(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": "Hello insight", "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    r = client.post("/generate-insights", json={"text": "  some text\n"})
    assert r.status_code == 200
    data = r.json()
    assert data == {"markdown": "Hello insight", "degraded": False}


def test_insight_endpoint(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": "Hello markdown", "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    payload = {"url": "https://ex.com", "martech": {}, "cms": []}
    r = client.post("/insight", json=payload)
    assert r.status_code == 200
    assert r.json() == {"markdown": "Hello markdown", "degraded": False}


def test_insight_trailing_slash(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": "Tolerant", "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    r = client.post("/insight/", json={"text": "foo"})
    assert r.status_code == 200
    assert r.json() == {"markdown": "Tolerant", "degraded": False}


def test_research(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": "Research result", "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    r = client.post("/research", json={"topic": "AI"})
    assert r.status_code == 200
    data = r.json()
    assert data == {"markdown": "Research result", "degraded": False}


def test_research_trim(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": "Trim me", "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    r = client.post("/research", json={"topic": "AI"})
    assert r.status_code == 200
    data = r.json()
    assert data == {"markdown": "Trim me", "degraded": False}


def test_research_validation_error():
    r = client.post("/research", json={})
    assert r.status_code == 400


def test_research_empty_topic():
    r = client.post("/research", json={"topic": "   "})
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_create_markdown_and_csv(monkeypatch):
    async def fake_alt(_desc: str) -> str:
        return "alt text"

    monkeypatch.setattr(
        insight_mod,
        "_generate_alt_text",
        fake_alt,
        raising=False,
    )

    report = {
        "title": "Demo",
        "summary": "short",
        "visuals": [{"url": "http://img", "description": "image"}],
        "scenarios": [{"step": 1, "action": "do"}],
    }

    md = await insight_mod.create_markdown(report)
    assert "alt text" in md
    csv_text = insight_mod.create_scenario_csv(report)
    assert "step" in csv_text and "action" in csv_text


def test_postprocess_report(monkeypatch):
    async def fake_alt(_desc: str) -> str:
        return "alt text"

    monkeypatch.setattr(
        insight_mod,
        "_generate_alt_text",
        fake_alt,
        raising=False,
    )

    payload = {
        "report": {
            "visuals": [{"url": "http://img", "description": "d"}],
            "scenarios": [{"foo": "bar"}],
        }
    }

    r = client.post("/postprocess-report", json=payload)
    assert r.status_code == 200
    downloads = r.json()["downloads"]
    md = base64.b64decode(downloads["markdown"]).decode()
    assert "alt text" in md
    csv_decoded = base64.b64decode(downloads["scenarios"]).decode()
    assert "foo" in csv_decoded


def test_metrics_and_warnings(monkeypatch):
    huge = "[Data Gap]" + "x" * (260 * 1024)
    async def fake_report(prompt: str, **_kwargs):
        return {"markdown": huge, "degraded": False}

    monkeypatch.setattr(
        insight_mod.orchestrator, "generate_report", fake_report, raising=False
    )

    r = client.post("/generate-insights", json={"text": "info"})
    assert r.status_code == 200
    data = r.json()
    assert "warnings" in data.get("meta", {})

    metrics_data = client.get("/metrics").json()
    assert metrics_data["generate-insights"]["requests"] >= 1
    assert metrics_data["data_gaps"] >= 1


def test_insight_and_personas(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        if "buyer personas" in prompt.lower():
            return {"generated_buyer_personas": {"P1": {"name": "P1"}}}
        return {
            "next_best_actions": [
                {
                    "title": "T",
                    "description": "D",
                    "action": "A",
                    "source": {"url": "https://x"},
                    "credibilityScore": 0.5,
                }
            ],
            "evidence": "I",
        }

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    before = insight_mod.metrics.get("insight-and-personas", {}).get("requests", 0)

    r = client.post(
        "/insight-and-personas",
        json={
            "url": "https://ex",
            "martech": {},
            "cms": ["WP"],
            "evidence_standards": "std",
            "credibility_scoring": "score",
            "deliverable_guidelines": "guidelines",
            "audience": "devs",
            "preferences": "none",
        },
    )
    assert r.status_code == 200
    data = r.json()
    actions = data["insight"]["actions"]
    assert isinstance(actions, list) and len(actions) == 1
    act = actions[0]
    for key in (
        "title",
        "description",
        "action",
        "source",
        "credibilityScore",
    ):
        assert key in act
    assert "url" in act["source"]
    assert data["insight"]["evidence"] == {
        "insights": actions,
        "evidence": "I",
    }
    assert data["personas"] == [{"id": "P1", "name": "P1"}]
    assert "cms_manual" not in data

    metrics_data = client.get("/metrics").json()
    assert metrics_data["insight-and-personas"]["requests"] == before + 1


def test_insight_and_personas_empty_fields(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        if "buyer personas" in prompt.lower():
            return {"generated_buyer_personas": {"P1": {"name": "P1"}}}
        return {"report": "I"}

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    r = client.post(
        "/insight-and-personas",
        json={
            "url": "https://ex",
            "martech": {},
            "cms": ["WP"],
            "evidence_standards": "",
            "credibility_scoring": "",
            "deliverable_guidelines": "",
            "audience": "",
            "preferences": "",
        },
    )
    assert r.status_code == 200
    data = r.json()


def test_insight_and_personas_action_dict(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        if "buyer personas" in prompt.lower():
            return {"generated_buyer_personas": {"P1": {"name": "P1"}}}
        return {"title": "T1", "action": "A1"}

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    r = client.post("/insight-and-personas", json={"url": "https://ex"})
    assert r.status_code == 200
    data = r.json()
    assert data["insight"]["actions"] == [{"title": "T1", "action": "A1"}]
    assert data["insight"]["evidence"] == {
        "insights": [{"title": "T1", "action": "A1"}],
        "evidence": "",
    }
    assert data["personas"] == [{"id": "P1", "name": "P1"}]


def test_insight_and_personas_next_best_action(monkeypatch):
    async def fake_report(prompt: str, **_kwargs):
        if "buyer personas" in prompt.lower():
            return {"generated_buyer_personas": {"P0": {"name": "P0"}}}
        return {
            "NextBestAction": {"title": "T1", "action": "A1"},
            "evidence": "EV",
            "Persona": {"name": "PN"},
        }

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    r = client.post(
        "/insight-and-personas",
        json={
            "url": "https://ex",
            "martech": {},
            "cms": [],
            "evidence_standards": "s",
            "credibility_scoring": "c",
            "deliverable_guidelines": "d",
            "audience": "a",
            "preferences": "p",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["insight"]["actions"] == [{"title": "T1", "action": "A1"}]
    assert data["insight"]["evidence"] == {
        "insights": [{"title": "T1", "action": "A1"}],
        "evidence": "EV",
    }
    personas = data["personas"]
    assert any(p["name"] == "P0" for p in personas)
    extracted = next(p for p in personas if p["name"] == "PN")
    assert extracted["name"] == "PN"
    for field in [
        "id",
        "role",
        "goal",
        "challenge",
        "demographics",
        "needs",
        "goals",
    ]:
        assert extracted[field] == "unknown"


def test_insight_and_personas_warnings(monkeypatch):
    huge = "[Data Gap]" + "x" * (260 * 1024)

    async def fake_report(_prompt: str, **_kw) -> dict:
        return {"data": huge}

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    before_req = insight_mod.metrics.get("insight-and-personas", {}).get("requests", 0)
    before_gap = insight_mod.metrics.get("data_gaps", 0)

    r = client.post("/insight-and-personas", json={"url": "http://e"})
    assert r.status_code == 200
    result = r.json()
    assert result["insight"] == {"actions": [], "evidence": {"data": huge}}
    assert result["personas"] == [
        {
            "id": "company",
            "name": "e",
            "role": "unknown",
            "goal": "unknown",
            "challenge": "unknown",
            "demographics": "unknown",
            "needs": "unknown",
            "goals": "unknown",
        },
        {
            "id": "tech",
            "name": "unknown",
            "role": "unknown",
            "goal": "unknown",
            "challenge": "unknown",
            "demographics": "unknown",
            "needs": "unknown",
            "goals": "unknown",
        },
    ]
    assert "cms_manual" not in result
    assert "warnings" in result.get("meta", {})

    metrics_data = client.get("/metrics").json()
    assert metrics_data["insight-and-personas"]["requests"] == before_req + 1
    assert metrics_data["data_gaps"] >= before_gap + 1


def test_insight_and_personas_empty_personas(monkeypatch):
    async def fake_report(prompt: str, **_kw):
        if "buyer personas" in prompt.lower():
            return {}
        return {"summary": "I"}

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    r = client.post(
        "/insight-and-personas",
        json={"url": "https://ex", "martech": {"js": ["React"]}, "cms": ["WP"]},
    )
    assert r.status_code == 200
    result = r.json()
    assert result["personas"] == [
        {
            "id": "company",
            "name": "ex",
            "role": "unknown",
            "goal": "unknown",
            "challenge": "unknown",
            "demographics": "unknown",
            "needs": "unknown",
            "goals": "unknown",
        },
        {
            "id": "tech",
            "name": "React, WP",
            "role": "unknown",
            "goal": "unknown",
            "challenge": "unknown",
            "demographics": "unknown",
            "needs": "unknown",
            "goals": "unknown",
        },
    ]


def test_insight_personas_concurrent(monkeypatch):
    sleep_dur = 0.05

    async def fake_report(prompt: str, **_kw):
        await asyncio.sleep(sleep_dur)
        if "buyer personas" in prompt.lower():
            return {"personas": ["P"]}
        return {"insight": "I"}

    monkeypatch.setattr(
        insight_mod.orchestrator,
        "generate_report",
        fake_report,
    )

    start = time.perf_counter()
    r = client.post("/insight-and-personas", json={"url": "http://x"})
    duration = time.perf_counter() - start
    assert r.status_code == 200
    assert duration < sleep_dur * 1.5


@pytest.mark.asyncio
async def test_generate_report_concurrent(monkeypatch):
    sleep_dur = 0.05

    class DummyResp:
        def __init__(self) -> None:
            content = "hi"
            message_obj = type("obj", (), {"content": content, "finish_reason": "stop"})()
            self.choices = [type("obj", (), {"message": message_obj, "finish_reason": "stop"})()]

    async def fake_create(**_kwargs):
        await asyncio.sleep(sleep_dur)
        return DummyResp()

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(
        insight_mod.orchestrator,
        "openai",
        dummy_module,
        raising=False,
    )
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    start = time.perf_counter()
    await asyncio.gather(
        insight_mod.orchestrator.generate_report("A"),
        insight_mod.orchestrator.generate_report("B"),
    )
    duration = time.perf_counter() - start
    assert duration < sleep_dur * 1.5


def test_insight_and_personas_invalid_field():
    r = client.post(
        "/insight-and-personas",
        json={"url": "http://x", "evidence_standards": {}}
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_generate_report_json(monkeypatch):
    class DummyResp:
        def __init__(self) -> None:
            self.json_snippet = """```json
{"markdown": "bar"}
```"""
            message_obj = type("obj", (), {"content": self.json_snippet, "finish_reason": "stop"})()
            self.choices = [type("obj", (), {"message": message_obj, "finish_reason": "stop"})()]

    async def fake_create(**_kwargs):
        return DummyResp()

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    result = await insight_mod.orchestrator.generate_report("prompt")
    expected = "```json\n{\"markdown\": \"bar\"}\n```"
    assert result["markdown"] == expected
    assert result["degraded"] is True



@pytest.mark.asyncio
async def test_generate_report_fenced_markdown(monkeypatch):
    class DummyResp:
        def __init__(self) -> None:
            content = """```markdown\n# Title\nBody text\n```"""
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    async def fake_create(**_kwargs):
        return DummyResp()

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    result = await insight_mod.orchestrator.generate_report("prompt")
    assert result == {"markdown": "# Title\nBody text", "degraded": False}


@pytest.mark.asyncio
async def test_generate_report_short_text(monkeypatch):
    class DummyResp:
        def __init__(self) -> None:
            message_obj = type("obj", (), {"content": "hi"})()
            self.choices = [type("obj", (), {"message": message_obj, "finish_reason": "stop"})()]

    async def fake_create(**_kwargs):
        return DummyResp()

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    result = await insight_mod.orchestrator.generate_report("prompt")
    assert result["markdown"] == "hi"
    assert result["degraded"] is True


@pytest.mark.asyncio
async def test_call_openai_streaming(monkeypatch):
    class Event:
        def __init__(self, content: str | None, finish: str | None = None) -> None:
            delta = {} if content is None else {"content": content}
            self.choices = [type("obj", (), {"delta": delta, "finish_reason": finish})()]

    async def fake_stream(**_kwargs):
        async def generator():
            yield Event("foo")
            yield Event("bar", "stop")

        return generator()

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_stream)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    content, finish, degraded = await insight_mod.orchestrator.call_openai_with_retry(
        [], stream=True
    )
    assert content == "foobar"
    assert finish == "stop"
    assert degraded is False
