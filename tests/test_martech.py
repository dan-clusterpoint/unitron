import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "services" / "martech"))
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

import services.martech.app as martech_app

client = TestClient(martech_app.app)

@pytest.mark.asyncio
async def test_analyze_mocked():
    mock_response = [{'product': 'Google Analytics', 'confidence': 0.8, 'evidence': ['pattern:analytics.js'], 'competitor': True}]
    with patch('services.martech.app.detect', return_value=mock_response):
        resp = client.post('/analyze', json={'url': 'http://example.com'})
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['product'] == 'Google Analytics'
    assert len(data) == 1
    
