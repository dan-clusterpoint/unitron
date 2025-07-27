import importlib
import os

allowed = {"gateway", "martech", "property", "insight"}
svc = os.environ.get("SERVICE", "gateway").strip()
if svc not in allowed:
    raise SystemExit(f"Unknown service: {svc}")

module = f"services.{svc}.app"
importlib.import_module(module)
print(f"✅ Successfully imported {module}")
