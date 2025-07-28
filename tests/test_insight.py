from fastapi.testclient import TestClient

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
