import socket
import subprocess
import time
from pathlib import Path

import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STARTUP_TIMEOUT = 15
HEALTH_POLL_INTERVAL = 0.1


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(base_url: str) -> None:
    deadline = time.time() + STARTUP_TIMEOUT
    last_error = None
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/api/health", timeout=0.5)
            if response.status_code == 200 and response.json() == {"status": "ok"}:
                return
        except (httpx.HTTPError, httpx.TransportError) as exc:
            last_error = exc
        time.sleep(HEALTH_POLL_INTERVAL)
    raise RuntimeError(f"server did not become healthy at {base_url}: {last_error}")


@pytest.fixture
def base_url():
    port = _free_port()
    proc = subprocess.Popen(
        [
            "uvicorn",
            "backend.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        _wait_for_health(url)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


def test_index_html_contains_required_testids(base_url: str):
    response = httpx.get(f"{base_url}/")
    assert response.status_code == 200
    html = response.text
    assert 'data-testid="todo-input"' in html
    assert 'data-testid="todo-add"' in html
    assert 'data-testid="todo-list"' in html


def test_static_assets_return_200(base_url: str):
    js = httpx.get(f"{base_url}/static/app.js")
    css = httpx.get(f"{base_url}/static/style.css")
    assert js.status_code == 200
    assert css.status_code == 200


def test_todos_crud_flow(base_url: str):
    listed = httpx.get(f"{base_url}/api/todos")
    assert listed.status_code == 200
    assert listed.json() == []

    first = httpx.post(f"{base_url}/api/todos", json={"title": "buy milk"})
    assert first.status_code == 201
    first_body = first.json()
    assert first_body == {"id": 1, "title": "buy milk", "done": False}

    second = httpx.post(f"{base_url}/api/todos", json={"title": "walk dog"})
    assert second.status_code == 201
    second_body = second.json()
    assert second_body == {"id": 2, "title": "walk dog", "done": False}

    toggled = httpx.patch(
        f"{base_url}/api/todos/{first_body['id']}", json={"done": True}
    )
    assert toggled.status_code == 200
    assert toggled.json() == {"id": 1, "title": "buy milk", "done": True}

    deleted = httpx.delete(f"{base_url}/api/todos/{second_body['id']}")
    assert deleted.status_code == 204

    remaining = httpx.get(f"{base_url}/api/todos")
    assert remaining.status_code == 200
    assert remaining.json() == [{"id": 1, "title": "buy milk", "done": True}]
