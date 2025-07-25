import os
import importlib
from fastapi.testclient import TestClient


def _load_app(service: str):
    os.environ["SERVICE"] = service
    mod = importlib.import_module("app")
    return importlib.reload(mod).app


def test_root_app_gateway():
    app = _load_app("gateway")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200


def test_root_app_martech():
    app = _load_app("martech")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200


def test_root_app_property():
    app = _load_app("property")
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
