from fastapi.testclient import TestClient
from property.app import app

client = TestClient(app)


def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}
