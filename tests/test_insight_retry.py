from fastapi.testclient import TestClient
import types

from services.insight.app import app
import services.insight.app as insight_mod

client = TestClient(app)


def test_retry_rate_limit(monkeypatch):
    class DummyResp:
        def __init__(self, content: str) -> None:
            message_obj = type("obj", (), {"content": content})()
            self.choices = [type("obj", (), {"message": message_obj})()]

    class RateLimitErr(Exception):
        def __init__(self) -> None:
            self.status_code = 429

    attempts = {"n": 0}

    async def fake_create(**_kwargs):
        if attempts["n"] < 2:
            attempts["n"] += 1
            raise RateLimitErr()
        return DummyResp("ok")

    class DummyChat:
        completions = type("obj", (), {"create": staticmethod(fake_create)})()

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = DummyChat

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")

    r = client.post("/generate-insights", json={"text": "hi"})
    assert r.status_code == 200
    data = r.json()
    assert data["insight"] == "ok"
    assert data["degraded"] is False
