import asyncio
import time
import httpx
from fastapi.testclient import TestClient
import services.gateway.app as gateway_app

client = TestClient(gateway_app.app)


def _set_mock_transport(monkeypatch, handler: httpx.MockTransport) -> None:
    class DummyClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=handler, *args, **kwargs)

    monkeypatch.setattr(gateway_app.httpx, "AsyncClient", DummyClient)
    gateway_app.app.state.client = DummyClient()


def test_insight_waits_for_25_seconds(monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(25)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    _set_mock_transport(monkeypatch, transport)

    start = time.perf_counter()
    r = client.post("/insight", json={"text": "hi"})
    duration = time.perf_counter() - start

    assert r.status_code == 200
    assert r.json() == {"result": {"ok": True}, "degraded": False}
    assert duration >= 25
