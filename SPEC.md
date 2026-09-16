# SPEC — sbx-demo-todo

All work happens from the repository root. Python 3.12, no database, no build step.

## Backend (`backend/`)

- `backend/__init__.py` (empty), `backend/app.py` exposing a FastAPI instance named `app`.
- `backend/requirements.txt`: `fastapi`, `uvicorn`, `httpx`, `pytest`.
- Start command (from repo root): `uvicorn backend.app:app --port 8000`.
- In-memory store (a module-level list/dict); ids are incrementing integers starting at 1.
- Todo JSON shape: `{"id": int, "title": str, "done": bool}`.

| Method | Path | Request body | Response |
| --- | --- | --- | --- |
| GET | `/api/health` | — | `200 {"status": "ok"}` |
| GET | `/api/todos` | — | `200 [Todo, ...]` (insertion order) |
| POST | `/api/todos` | `{"title": str}` (non-empty after strip) | `201 Todo` ; `422` on empty/missing title |
| PATCH | `/api/todos/{id}` | `{"title"?: str, "done"?: bool}` | `200 Todo` ; `404` if unknown id |
| DELETE | `/api/todos/{id}` | — | `204` ; `404` if unknown id |

- `GET /` must serve `frontend/index.html`; other files under `frontend/` are served at `/static/<name>` (e.g. `/static/app.js`, `/static/style.css`). Mount the static directory relative to the repo root so it works when started from the root.
- Unit tests in `backend/tests/test_api.py` using `fastapi.testclient.TestClient`; cover every endpoint including 404/422 paths. Run: `python -m pytest backend -q`.

## Frontend (`frontend/`)

- `frontend/index.html`, `frontend/app.js`, `frontend/style.css`. Vanilla JS (ES modules ok), no frameworks, no bundler.
- `index.html` references `/static/app.js` and `/static/style.css`.
- On load: `GET /api/todos` and render the list.
- Features: add a todo (input + button, Enter key also adds), toggle `done` (PATCH), delete (DELETE). Re-render from the server response after each mutation.
- Required `data-testid` attributes:
  - `todo-input` — the text input
  - `todo-add` — the add button
  - `todo-list` — the `<ul>` container
  - `todo-item` — each `<li>`; also set `data-id="<id>"` and class `done` when done
  - `todo-toggle` — checkbox inside each item
  - `todo-delete` — delete button inside each item
  - `todo-count` — element showing `N items left` (not-done count)

## End-to-end (`e2e/`)

- `e2e/test_e2e.py` (pytest). Boot the real server with `uvicorn backend.app:app --port <free port>` as a subprocess, wait for `/api/health`, then:
  1. `GET /` returns 200 HTML containing `data-testid="todo-input"`, `data-testid="todo-add"`, `data-testid="todo-list"`.
  2. `GET /static/app.js` and `/static/style.css` return 200.
  3. Full CRUD flow over `/api/todos` (create two, toggle one, delete one, list reflects it).
- Must run with `python -m pytest e2e -q` from the repo root and always terminate the server (use a fixture with `finally`).

## Conventions

- Commit on a branch, never directly on `main`. Small, focused commits.
- Do not add secrets, `.env` files, or credentials. Do not commit `__pycache__/` or virtualenvs.
