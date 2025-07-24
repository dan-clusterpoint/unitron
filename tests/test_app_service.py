from fastapi.testclient import TestClient

from services.gateway.app import app as gateway_app
from services.martech.app import app as martech_app
from property.app import app as property_app


def test_load_gateway():
    client = TestClient(gateway_app)
    r = client.get("/health")
    assert r.status_code == 200


def test_load_martech():
    client = TestClient(martech_app)
    r = client.get("/health")
    assert r.status_code == 200


def test_load_property():
    client = TestClient(property_app)
    r = client.get("/health")
    assert r.status_code == 200
