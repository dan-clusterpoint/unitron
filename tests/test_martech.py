from services.martech.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
