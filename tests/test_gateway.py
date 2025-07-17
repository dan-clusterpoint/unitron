import pytest
from fastapi.testclient import TestClient
import services.gateway.app as gateway_app

client = TestClient(gateway_app.app)

def test_health():
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok'}
