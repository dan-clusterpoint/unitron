from fastapi.testclient import TestClient

from main import app as main_app


def test_load_main():
    client = TestClient(main_app)
    r = client.get("/health")
    assert r.status_code == 200
