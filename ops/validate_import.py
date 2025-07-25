import importlib
import os

svc = os.environ.get("SERVICE", "gateway").strip()
module = f"services.{svc}.app"
importlib.import_module(module)
print(f"✅ Successfully imported {module}")
