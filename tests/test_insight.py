from fastapi.testclient import TestClient
import base64
import pytest
import asyncio
import time

from services.insight.app import app
import services.insight.app as insight_mod
import types

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
    class DummyResp:
        def __init__(self, content: str) -> None:
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    async def fake_create(**kwargs):
        return DummyResp("Hello insight")

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    r = client.post("/generate-insights", json={"text": "  some text\n"})
    assert r.status_code == 200
    data = r.json()
    assert data["insight"] == "Hello insight"
    assert data["degraded"] is False


def test_research(monkeypatch):
    class DummyResp:
        def __init__(self, content: str) -> None:
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    async def fake_create(**kwargs):
        return DummyResp("Research result")

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    r = client.post("/research", json={"topic": "AI"})
    assert r.status_code == 200
    data = r.json()
    assert data["summary"] == "Research result"
    assert data["degraded"] is False


def test_research_trim(monkeypatch):
    class DummyResp:
        def __init__(self, content: str) -> None:
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    async def fake_create(**kwargs):
        return DummyResp("  Trim me  \n")

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(
        AsyncOpenAI=lambda api_key=None: DummyClient(),
    )
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    r = client.post("/research", json={"topic": "AI"})
    assert r.status_code == 200
    data = r.json()
    assert data["summary"] == "Trim me"
    assert data["degraded"] is False


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

    class DummyResp:
        def __init__(self, content: str) -> None:
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    async def fake_create(**kwargs):
        return DummyResp(huge)

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

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
            "summary": "I",
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
    assert data["insight"]["evidence"] == "I"
    assert data["personas"] == [{"id": "P1", "name": "P1"}]
    assert "cms_manual" not in data
    assert data["degraded"] is False

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
    assert data["degraded"] is True


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
    assert result["personas"] == []
    assert "cms_manual" not in result
    assert result["degraded"] is True
    assert "warnings" in result.get("meta", {})

    metrics_data = client.get("/metrics").json()
    assert metrics_data["insight-and-personas"]["requests"] == before_req + 1
    assert metrics_data["data_gaps"] >= before_gap + 1


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
            message_obj = type("obj", (), {"content": "{}"})()
            self.choices = [type("obj", (), {"message": message_obj})()]

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
async def test_generate_report_json_error(monkeypatch):
    class DummyResp:
        def __init__(self) -> None:
            message_obj = type("obj", (), {"content": "not json"})()
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
    assert result == {"insight": "not json", "degraded": True}
