import importlib
import os
import sys
from fastapi.testclient import TestClient


def load_app():
    if "app" in sys.modules:
        return importlib.reload(sys.modules["app"])
    return importlib.import_module("app")


def test_load_gateway():
    os.environ["SERVICE"] = "gateway"
    module = load_app()
    client = TestClient(module.app)
    r = client.get("/health")
    assert r.status_code == 200


def test_load_martech():
    os.environ["SERVICE"] = "martech"
    module = load_app()
    client = TestClient(module.app)
    r = client.get("/health")
    assert r.status_code == 200

