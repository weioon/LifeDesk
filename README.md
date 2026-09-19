# LifeDesk

A personal daily productivity dashboard built with React, TypeScript, Vite, and FastAPI.

## Current scope

Milestone 2 adds persistent tasks using SQLite and SQLAlchemy, Alembic migrations,
and a tested task API. The frontend remains the Milestone 1 responsive welcome screen
with a backend connection check. Task UI and notes are not implemented yet.

## Prerequisites

- Node.js 22.12+ (tested with 22.14.0) and npm.
- Python 3.11+ (tested with 3.13.1), including the standard `venv` module.
- Internet access for initial dependency installation.

Run the backend and frontend in separate terminals. Commands below assume PowerShell
and begin in the LifeDesk project directory. Virtual environment activation is not required.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On subsequent starts, run only the final command from `backend`.
After pulling changes with new migrations, run `alembic upgrade head` using the
virtual-environment Python before starting the server. The API never creates tables
automatically; migrations own the schema.
On macOS/Linux, substitute `.venv/bin/python` for `.\.venv\Scripts\python.exe`
and use `python3` when creating the environment if needed.

- Health endpoint: http://127.0.0.1:8000/api/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Expected health response: `{"status":"ok"}`

## Database and task API

The database is stored at `data/lifedesk.db` under the project root, regardless of the
working directory. It is excluded from Git. Stop the backend before copying this file
for a simple backup. Do not delete it when updating or restarting the application.

Optionally set `$env:LIFEDESK_DB_PATH = 'data/custom.db'` before running migrations
and starting the backend. Relative paths resolve against the project root; absolute
paths are also supported. Both commands must use the same setting. Restart the server
after changing this setting. No `.env` loader is used.

| Method | Endpoint | Behavior |
| --- | --- | --- |
| GET | `/api/tasks` | List tasks; no filters returns active and completed tasks |
| POST | `/api/tasks` | Create an incomplete task; returns 201 |
| GET | `/api/tasks/{id}` | Retrieve a task |
| PATCH | `/api/tasks/{id}` | Update supplied fields only |
| DELETE | `/api/tasks/{id}` | Permanently delete; returns 204 with no body |

Missing records return 404; invalid bodies or filters return 422.
Titles are trimmed, required, and limited to 200 characters after trimming.
Priority is `low`, `medium` (default), or `high`. Description and due date are optional.
Use `YYYY-MM-DD` for due dates; past dates are allowed. Unknown body fields are rejected.
IDs and timestamps are managed by the server.

PATCH accepts `title`, `description`, `due_date`, `priority`, and `is_completed`.
Set `description` or `due_date` to `null` to clear them. Required fields cannot be
set to `null`. An empty PATCH is a no-op. Completing sets `completed_at`; reopening
clears it. Repeating completion preserves the original completion timestamp.
Timestamps are stored as UTC and returned with a UTC offset; due dates have no timezone.

List filters combine with AND:

- `is_completed=true` or `false`; omit to include both.
- `due_before=YYYY-MM-DD`: exclusive upper date boundary.
- `due_from=YYYY-MM-DD`: inclusive lower boundary.
- `due_to=YYYY-MM-DD`: inclusive upper boundary.

Any date filter excludes undated tasks. Reversed date ranges return 422. Completed
lists (`is_completed=true`) sort by most recently completed first. Other lists sort
by due date (undated last), High/Medium/Low within each date, then ID for stable ordering.
There is no pagination in this small first-version API.

Example from PowerShell while the backend is running:

```powershell
$task = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/tasks -ContentType 'application/json' -Body '{"title":"Plan tomorrow","due_date":"2026-09-20","priority":"high"}'
Invoke-RestMethod -Uri ("http://127.0.0.1:8000/api/tasks/" + $task.id)
Invoke-RestMethod 'http://127.0.0.1:8000/api/tasks?is_completed=false&due_from=2026-09-20'
```

## Frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. The page should display **Connected to LifeDesk**.
On subsequent starts, run only `npm run dev` from `frontend`.

The browser requests the relative URL `/api/health`. Vite forwards `/api` requests to
`http://127.0.0.1:8000`, so development requests are same-origin from the browser's
perspective and do not require permissive CORS settings. Both servers bind to loopback;
mobile-sized windows can be tested with browser responsive mode. Network access from
a separate mobile device is not configured.

If the connection fails, start the backend and click **Try again**. Requests time out
after eight seconds. Ports 8000 and 5173 must be available; Vite will not silently switch ports.
Use Ctrl+C in each terminal to stop the servers.

## Checks

From `backend`:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m alembic check
```

Tests use isolated temporary SQLite files, apply real Alembic migrations, and never
write to your personal database. They also verify persistence after reopening a
database, migration downgrade/upgrade, and consistency between migrations and models.

From `frontend`:

```powershell
npm run check
npm run build
```

With both servers running, verify the development proxy in PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

The build is written to `frontend/dist`. Production API routing and serving the built
frontend through FastAPI will be added in the later everyday-use milestone.
`npm run preview` is a static build preview, not the configured development proxy.
