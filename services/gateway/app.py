from fastapi import FastAPI
from starlette.responses import JSONResponse
from services.shared.utils import ping

app = FastAPI()


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok'})


@app.get('/ready')
async def ready():
    return JSONResponse({'ready': ping()})
