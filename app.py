import os

service = os.getenv("SERVICE", "gateway")
if service == "gateway":
    from services.gateway.app import app  # type: ignore F401
elif service == "martech":
    from services.martech.app import app  # type: ignore F401
elif service == "property":
    from property.app import app  # type: ignore F401
else:
    raise ValueError(f"Unknown SERVICE: {service}")

