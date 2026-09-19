# Milestone 2: Database and Task API

## Outcome

Implemented persistent task storage with SQLAlchemy 2.0.54 and SQLite, Alembic 1.20.0
migrations, task CRUD endpoints, validation, completion transitions, and list filters.
No frontend files changed. Notes and all other deferred features remain unimplemented.

## Verification results

- **46 tests passed, 0 failed**, 2 existing dependency deprecation warnings.
- Initial migration applied successfully: `0001_create_tasks (head)`.
- `alembic check`: `No new upgrade operations detected.`
- `pip check`: `No broken requirements found.`
- Health endpoint returned `{"status":"ok"}` both directly on port 8000 and through
  the existing frontend proxy on port 5173, including after the backend restart.
- Live POST returned 201; GET by ID and filtered list returned the saved task.
- Stopped and restarted Uvicorn (process 11348 replaced by 14376); GET returned the
  same task, ID, fields, and timestamps from the database.
- Automated tests use temporary file-backed databases built by the real migration.
  Tests also verify migration downgrade/reapply and model/schema agreement.
- No frontend build was repeated because frontend source and dependencies are unchanged.

## Live API demonstration

POST `/api/tasks` with:

```json
{
  "title": "Milestone 2 persistence demo",
  "description": "Created through the API for review",
  "due_date": "2026-09-20",
  "priority": "high"
}
```

GET `/api/tasks/1` returned the following both before and after restart:

```json
{
  "id": 1,
  "title": "Milestone 2 persistence demo",
  "description": "Created through the API for review",
  "due_date": "2026-09-20",
  "priority": "high",
  "is_completed": false,
  "completed_at": null,
  "created_at": "2026-09-19T10:39:04.6085Z",
  "updated_at": "2026-09-19T10:39:04.608504Z"
}
```

The filtered request `/api/tasks?is_completed=false&due_from=2026-09-20` also
returned this task. It remains in the local database for review.

## Files created

Paths below are relative to `C:\Users\weioo\LifeDesk`.

| File | Purpose |
| --- | --- |
| `backend/app/config.py` | Stable database path and optional environment override |
| `backend/app/database.py` | SQLite engine and per-request SQLAlchemy sessions |
| `backend/app/models.py` | Task columns, UTC timestamp defaults, database constraints |
| `backend/app/schemas.py` | Create/update validation and response serialization |
| `backend/app/routers/__init__.py` | Router package |
| `backend/app/routers/tasks.py` | CRUD, filtering, sorting, completion transitions |
| `backend/alembic.ini` | Migration configuration |
| `backend/migrations/env.py` | Migration connection and model metadata |
| `backend/migrations/script.py.mako` | Template for future migration revisions |
| `backend/migrations/versions/0001_create_tasks.py` | Initial tasks migration and downgrade |
| `backend/tests/conftest.py` | Isolated migrated SQLite fixtures and dependency override |
| `backend/tests/test_tasks.py` | 37 task API test cases |
| `backend/tests/test_database.py` | 8 persistence, path, constraint, and migration cases |
| `MILESTONE-2-REPORT.md` | This report |
| `data/lifedesk.db` | Generated local database, excluded from Git |

## Files modified

| File | Change |
| --- | --- |
| `backend/pyproject.toml` | Add SQLAlchemy and Alembic dependencies |
| `backend/app/main.py` | Register task routes; preserve health route |
| `README.md` | Migration/startup instructions, storage configuration, API rules and examples |

Installation and verification also generated/updated ignored files in `backend/.venv`,
`backend/lifedesk_backend.egg-info`, Python `__pycache__` directories, and
`backend/.pytest_cache`. Pytest created temporary databases in its normal system
temporary directory. These are dependency/runtime artifacts, not authored source files.
Milestone 1 reports are historical and were not changed.

## Important behavior

- Migrations must be run before task endpoints are used; startup does not create tables.
- Default database location is `<project>/data/lifedesk.db`, independent of the working
  directory. `LIFEDESK_DB_PATH` can select an alternate file for both API and migrations.
- Titles are trimmed and must contain 1–200 characters. Priorities are constrained
  to low/medium/high, defaulting to medium. Due dates are optional date-only values.
- PATCH only changes supplied fields. Explicit null clears description/due date;
  required fields reject null. Unknown body fields and client-supplied timestamps fail validation.
- Completion sets `completed_at`; reopening clears it. Repeated completion and empty
  PATCH preserve timestamps. Actual edits update `updated_at`.
- API timestamps include UTC timezone information; stored SQLite timestamps are UTC.
- Lists support `is_completed`, exclusive `due_before`, inclusive `due_from` and `due_to`.
  Date-filtered lists exclude undated tasks. With no filters, both statuses are returned.
- Completed-only lists sort newest completion first. Other lists sort by date,
  then High/Medium/Low priority, then ID; undated tasks appear last.

## Warnings and unresolved issues

- No application test, migration, or live API verification failures occurred.
- The two warnings are unchanged from Milestone 1: Starlette deprecates using `httpx`
  with TestClient in favor of `httpx2`, and references AnyIO's deprecated
  `anyio.abc.BlockingPortal` alias. No unrelated dependency changes or warning
  suppression were made.
- Initial workspace discovery reported access denied on the old Milestone 1
  `backend/pytest-cache-files-h_x0cyd0` directory. Relevant source files were readable;
  this stale directory was not modified. Current tests ran with normal temporary-file
  permissions and did not produce the former pytest cache warning.
- Pip advertised an optional update from 24.3.1 to 26.2.1; no global tool upgrade was made.
- Explicit Ctrl+C stops returned process exit code 1 through the command runner;
  this was the intentional server restart, not an application test failure.
- Development servers remain running for review. Production deployment and UI task
  management remain outside this milestone.

## Reference documentation consulted

- [SQLAlchemy SQLite documentation](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Alembic autogeneration and metadata](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
