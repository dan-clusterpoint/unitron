from fastapi.testclient import TestClient

from main import app as main_app
from services.property.app import app as property_app


def test_load_main():
    client = TestClient(main_app)
    r = client.get("/health")
    assert r.status_code == 200


def test_load_property():
    client = TestClient(property_app)
    r = client.get("/health")
    assert r.status_code == 200
