from fastapi.testclient import TestClient
import base64
import pytest

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

    dummy_module = types.SimpleNamespace(
        AsyncOpenAI=lambda api_key=None: DummyClient()
    )
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    r = client.post("/generate-insights", json={"text": "  some text\n"})
    assert r.status_code == 200
    assert r.json()["insight"] == "Hello insight"


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

    dummy_module = types.SimpleNamespace(
        AsyncOpenAI=lambda api_key=None: DummyClient()
    )
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    r = client.post("/research", json={"topic": "AI"})
    assert r.status_code == 200
    assert r.json()["summary"] == "Research result"


def test_research_validation_error():
    r = client.post("/research", json={})
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

    dummy_module = types.SimpleNamespace(
        AsyncOpenAI=lambda api_key=None: DummyClient()
    )
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    r = client.post("/generate-insights", json={"text": "info"})
    assert r.status_code == 200
    data = r.json()
    assert "warnings" in data.get("meta", {})

    metrics_data = client.get("/metrics").json()
    assert metrics_data["generate-insights"]["requests"] >= 1
    assert metrics_data["data_gaps"] >= 1
