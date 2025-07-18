from fastapi import FastAPI

import services.property.app as property_app
import services.martech.app as martech_app
import services.insight-agent.app as insight_app
import services.browse-runner.app as browse_app

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
