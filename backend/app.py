from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI()

todos: dict[int, dict] = {}
next_id: int = 1


class TodoCreate(BaseModel):
    title: str


class TodoPatch(BaseModel):
    title: str | None = None
    done: bool | None = None


def reset_store() -> None:
    global next_id
    todos.clear()
    next_id = 1


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/todos")
def list_todos() -> list[dict]:
    return list(todos.values())


@app.post("/api/todos", status_code=201)
def create_todo(body: TodoCreate) -> dict:
    global next_id
    title = body.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="title must be non-empty")
    todo = {"id": next_id, "title": title, "done": False}
    todos[next_id] = todo
    next_id += 1
    return todo


@app.patch("/api/todos/{todo_id}")
def patch_todo(todo_id: int, body: TodoPatch) -> dict:
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Not Found")
    if body.title is not None:
        todo["title"] = body.title.strip()
    if body.done is not None:
        todo["done"] = body.done
    return todo


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Not Found")
    del todos[todo_id]


@app.get("/")
def index():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(index_file)


if FRONTEND_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
