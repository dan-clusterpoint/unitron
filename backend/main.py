from fastapi import FastAPI

import services.property.app as property_app
import services.martech.app as martech_app
import importlib

# Hyphenated service directories can't be imported using the normal syntax, so
# load them dynamically using ``importlib.import_module``.
insight_app = importlib.import_module("services.insight-agent.app")
browse_app = importlib.import_module("services.browse-runner.app")

app = FastAPI(title="Unitron Backend")

app.mount("/property", property_app.app)
app.mount("/martech", martech_app.app)
app.mount("/insight-agent", insight_app.app)
app.mount("/browse-runner", browse_app.app)

# Recreate gateway combined endpoints using same logic
import services.gateway.app as gateway

gateway.PROPERTY_URL = "http://localhost"  # dummy values not used
gateway.MARTECH_URL = "http://localhost"

gateway.app.mount("/property", property_app.app)
gateway.app.mount("/martech", martech_app.app)

app.mount("/", gateway.app)
