# LifeDesk

A personal daily productivity dashboard built with React, TypeScript, Vite, and FastAPI.

## Current scope

Milestone 1 provides a responsive welcome screen and a working backend connection check.
Tasks, notes, and database persistence are not implemented yet. SQLite, SQLAlchemy, and
Alembic migrations remain planned for Milestone 2; no database is created by this version.

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
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On subsequent starts, run only the final command from `backend`.
On macOS/Linux, substitute `.venv/bin/python` for `.\.venv\Scripts\python.exe`
and use `python3` when creating the environment if needed.

- Health endpoint: http://127.0.0.1:8000/api/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Expected health response: `{"status":"ok"}`

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
```

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
