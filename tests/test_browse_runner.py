import pathlib, importlib.util
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

service_path = pathlib.Path(__file__).resolve().parents[1] / "services" / "browse-runner" / "app.py"
spec = importlib.util.spec_from_file_location("browse_runner_app", service_path)
browse_runner_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browse_runner_app)

client = TestClient(browse_runner_app.app)

class DummyPage:
    async def goto(self, url):
        pass
    async def screenshot(self, path):
        open(path, "wb").write(b"")

class DummyBrowser:
    async def new_page(self):
        return DummyPage()
    async def close(self):
        pass

class DummyBrowserType:
    async def launch(self):
        return DummyBrowser()

class DummyPlaywright:
    chromium = DummyBrowserType()
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass

def fake_async_playwright():
    return DummyPlaywright()

@pytest.mark.asyncio
async def test_run_mocked(tmp_path):
    script = """async def main(page, screenshot_dir):\n    await page.goto('https://example.com')\n    await page.screenshot(path=str(pathlib.Path(screenshot_dir)/'test.png'))"""
    with (
        patch.object(browse_runner_app, 'async_playwright', fake_async_playwright),
        patch.object(browse_runner_app, 'SCREENSHOT_DIR', str(tmp_path))
    ):
        resp = client.post('/run', json={'script': script})
    assert resp.status_code == 200
    assert resp.json() == {'screenshots': ['test.png']}


@pytest.mark.asyncio
async def test_run_reject_import(tmp_path):
    script = "import os"
    with (
        patch.object(browse_runner_app, 'async_playwright', fake_async_playwright),
        patch.object(browse_runner_app, 'SCREENSHOT_DIR', str(tmp_path))
    ):
        resp = client.post('/run', json={'script': script})
    assert resp.status_code == 400
