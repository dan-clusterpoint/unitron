from fastapi import FastAPI
from starlette.responses import JSONResponse

app = FastAPI()


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok'})


@app.get('/ready')
async def ready():
    return JSONResponse({'ready': True})
