import sys, pathlib, importlib.util
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

service_path = pathlib.Path(__file__).resolve().parents[1] / "services" / "insight-agent" / "app.py"
spec = importlib.util.spec_from_file_location("insight_agent_app", service_path)
insight_agent_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(insight_agent_app)

client = TestClient(insight_agent_app.app)

@pytest.mark.asyncio
def test_generate_mocked():
    mock_resp = type('obj', (object,), {
        'choices': [type('c', (object,), {'message': type('m', (object,), {'content': 'notes'})()})]
    })()
    async_mock = AsyncMock(return_value=mock_resp)
    with (
        patch('openai.ChatCompletion.acreate', async_mock),
        patch.object(insight_agent_app.openai, 'api_key', 'x')
    ):
        resp = client.post('/generate', json={'name': 'Acme'})
    assert resp.status_code == 200
    assert resp.json() == {'notes': 'notes'}
