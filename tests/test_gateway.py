import pytest
from fastapi.testclient import TestClient
import services.gateway.app as gateway_app
from unittest.mock import AsyncMock, patch

gateway_app.N8N_URL = "http://n8n"

client = TestClient(gateway_app.app)

@pytest.mark.asyncio
async def test_health():
    dummy = type('R', (object,), {'status_code': 200})()
    with (
        patch('httpx.AsyncClient.get', new=AsyncMock(return_value=dummy)),
        patch('services.gateway.app.PROPERTY_URL', 'http://prop'),
        patch('services.gateway.app.MARTECH_URL', 'http://martech'),
        patch('services.gateway.app.INSIGHT_AGENT_URL', 'http://insight'),
        patch('services.gateway.app.BROWSE_RUNNER_URL', 'http://browse'),
    ):
        resp = client.get('/health')
    assert resp.status_code == 200
    body = resp.json()
    assert body['status'] == 'ok'
    assert all(body['services'].values())


@pytest.mark.asyncio
async def test_jobs_start():
    dummy_resp = type('R', (object,), {'status_code': 200, 'raise_for_status': lambda self: None})()
    with (
        patch('httpx.AsyncClient.post', new=AsyncMock(return_value=dummy_resp)),
        patch('services.gateway.app.upsert_job', new=AsyncMock()),
        patch('services.gateway.app.uuid4', return_value='job123'),
    ):
        resp = client.post('/jobs/start')
    assert resp.status_code == 200
    assert resp.json()['job_id'] == 'job123'
    assert resp.json()['status'] == 'pending'


@pytest.mark.asyncio
async def test_jobs_get():
    job = {'job_id': 'job123', 'stage': 'start', 'status': 'pending', 'result_url': None}
    with patch('services.gateway.app.get_job', new=AsyncMock(return_value=job)):
        resp = client.get('/jobs/job123')
    assert resp.status_code == 200
    assert resp.json() == job


@pytest.mark.asyncio
async def test_jobs_get_missing():
    with patch('services.gateway.app.get_job', new=AsyncMock(return_value=None)):
        resp = client.get('/jobs/none')
    assert resp.status_code == 404
