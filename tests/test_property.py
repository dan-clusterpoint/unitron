import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

import services.property.app as property_app

client = TestClient(property_app.app)

@pytest.mark.asyncio
async def test_analyze_mocked():
    with (
        patch('services.property.app.whois.whois', return_value={'org': 'Example Org'}),
        patch('services.property.app.get_dns_records', new=AsyncMock(return_value=['1.2.3.4'])),
        patch('services.property.app.get_ssl_san', return_value=['www.example.com']),
        patch('services.property.app.fetch_sitemap', new=AsyncMock(return_value=['http://example.com/sitemap.xml'])),
        patch('services.property.app.fetch_internal_links', new=AsyncMock(return_value=['http://example.com/page'])),
        patch('services.property.app.save_domains', new=AsyncMock()),
    ):
        resp = client.post('/analyze', json={'domain': 'example.com'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['domain'] == 'example.com'
    assert data['confidence'] == 1.0
    assert 'whois_org' in data['evidence']
