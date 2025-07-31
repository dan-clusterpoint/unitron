from fastapi.testclient import TestClient
import types
import httpx

from services.insight.app import app
import services.insight.app as insight_mod

client = TestClient(app)


def test_retry_rate_limit(monkeypatch):
    attempts = {"n": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] <= 2:
            return httpx.Response(429)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    transport = httpx.MockTransport(handler)

    class DummyCompletions:
        def __init__(self) -> None:
            self.client = httpx.AsyncClient(transport=transport)

        async def create(self, **_kwargs):
            resp = await self.client.post("https://test")
            if resp.status_code == 429:
                err = Exception("rate limit")
                err.status_code = 429
                raise err
            data = resp.json()["choices"][0]["message"]["content"]
            message = type("obj", (), {"content": data})()
            return type("obj", (), {"choices": [type("obj", (), {"message": message})()]})

    class DummyClient:
        def __init__(self, *a, **kw) -> None:
            self.chat = types.SimpleNamespace(completions=DummyCompletions())

    dummy_module = types.SimpleNamespace(AsyncOpenAI=lambda api_key=None: DummyClient())
    monkeypatch.setattr(insight_mod, "openai", dummy_module, raising=False)
    monkeypatch.setattr(insight_mod.orchestrator, "openai", dummy_module, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")

    r = client.post("/generate-insights", json={"text": "hi"})
    assert r.status_code == 200
    data = r.json()
    assert data["insight"] == "ok"
    assert data["degraded"] is False
    assert attempts["n"] == 3
