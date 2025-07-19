import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient

from martech.app import app

client = TestClient(app)


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # type: ignore[override]
        if self.path == "/script.js":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"console.log('hi');")
        else:
            html = (
                "<script src='https://www.google-"
                "analytics.com/analytics.js'></script>"
                "<script src='/script.js'></script>"
            )
            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode())


def test_health():
    r = client.get('/health')
    assert r.status_code == 200


def test_ready_and_analyze():
    # spin up simple http server
    server = HTTPServer(('localhost', 0), SimpleHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        ready = client.get('/ready')
        assert ready.status_code == 200
        assert ready.json()['ready'] is True

        resp = client.post(
            '/analyze', json={'url': f'http://localhost:{port}/'}
        )
        data = resp.json()
        assert resp.status_code == 200
        assert 'Google Analytics' in data['core']
    finally:
        server.shutdown()
