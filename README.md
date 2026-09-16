# sbx-demo-todo

A tiny classic frontend + backend Todo app, developed end-to-end by cloud
coding agents orchestrated through the sbx-browser `/v1` API.

- `backend/` — FastAPI JSON API + static file serving (Python 3.12)
- `frontend/` — vanilla HTML/JS/CSS, no build step
- `e2e/` — end-to-end tests that boot the server and exercise UI + API

See `SPEC.md` for the contract every contributor (human or agent) follows.

## Run

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --port 8000
# open http://localhost:8000
```

## Test

```bash
python -m pytest backend -q      # API unit tests
python -m pytest e2e -q          # end-to-end
```
