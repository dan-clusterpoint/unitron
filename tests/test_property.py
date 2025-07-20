from fastapi.testclient import TestClient

from property.app import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_analyze_success():
    r = client.post('/analyze', json={'domain': 'example.com'})
    assert r.status_code == 200
    data = r.json()
    assert 'example.com' in data['domains']
    assert data['confidence'] > 0


def test_analyze_failure():
    r = client.post('/analyze', json={'domain': 'nonexistentdomain.invalidtld'})
    assert r.status_code == 400
