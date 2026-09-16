import pytest
from fastapi.testclient import TestClient

from backend.app import app, reset_store


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_todos_empty(client: TestClient):
    response = client.get("/api/todos")
    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client: TestClient):
    response = client.post("/api/todos", json={"title": "buy milk"})
    assert response.status_code == 201
    body = response.json()
    assert body == {"id": 1, "title": "buy milk", "done": False}


def test_create_todo_strips_title(client: TestClient):
    response = client.post("/api/todos", json={"title": "  trim me  "})
    assert response.status_code == 201
    assert response.json()["title"] == "trim me"


def test_create_todo_missing_title(client: TestClient):
    response = client.post("/api/todos", json={})
    assert response.status_code == 422


def test_create_todo_empty_title(client: TestClient):
    response = client.post("/api/todos", json={"title": ""})
    assert response.status_code == 422


def test_create_todo_whitespace_title(client: TestClient):
    response = client.post("/api/todos", json={"title": "   "})
    assert response.status_code == 422


def test_list_todos_insertion_order(client: TestClient):
    client.post("/api/todos", json={"title": "first"})
    client.post("/api/todos", json={"title": "second"})
    response = client.get("/api/todos")
    assert response.status_code == 200
    titles = [todo["title"] for todo in response.json()]
    assert titles == ["first", "second"]
    assert [todo["id"] for todo in response.json()] == [1, 2]


def test_patch_title(client: TestClient):
    created = client.post("/api/todos", json={"title": "old"}).json()
    response = client.patch(f"/api/todos/{created['id']}", json={"title": "new"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "new", "done": False}


def test_patch_done(client: TestClient):
    created = client.post("/api/todos", json={"title": "task"}).json()
    response = client.patch(f"/api/todos/{created['id']}", json={"done": True})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "task", "done": True}


def test_patch_title_and_done(client: TestClient):
    created = client.post("/api/todos", json={"title": "task"}).json()
    response = client.patch(
        f"/api/todos/{created['id']}", json={"title": "updated", "done": True}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "updated", "done": True}


def test_patch_unknown_id(client: TestClient):
    response = client.patch("/api/todos/999", json={"done": True})
    assert response.status_code == 404


def test_delete_todo(client: TestClient):
    created = client.post("/api/todos", json={"title": "gone"}).json()
    response = client.delete(f"/api/todos/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    listed = client.get("/api/todos")
    assert listed.json() == []


def test_delete_unknown_id(client: TestClient):
    response = client.delete("/api/todos/999")
    assert response.status_code == 404


def test_ids_do_not_reuse_after_delete(client: TestClient):
    first = client.post("/api/todos", json={"title": "a"}).json()
    client.delete(f"/api/todos/{first['id']}")
    second = client.post("/api/todos", json={"title": "b"}).json()
    assert second["id"] == 2


def test_index_without_frontend(client: TestClient):
    response = client.get("/")
    assert response.status_code == 404
