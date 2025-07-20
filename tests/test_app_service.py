import importlib
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is on sys.path when PYTHONPATH doesn't include it
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


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


def test_load_property():
    os.environ["SERVICE"] = "property"
    module = load_app()
    client = TestClient(module.app)
    r = client.get("/health")
    assert r.status_code == 200
