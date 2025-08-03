from __future__ import annotations
import os
import importlib

_ALLOWED = {"gateway", "martech", "property", "insight"}
svc = os.getenv("SERVICE", "gateway").strip()
if svc not in _ALLOWED:
    raise RuntimeError(f"Unknown service: {svc}")
module = importlib.import_module(f"services.{svc}.app")
app = module.app
