# Milestone 3: Task Dashboard

## Delivered

A responsive task-management frontend using the existing FastAPI API. The cream,
green, rounded-card visual direction is preserved. App.tsx now contains only the page
shell; dashboard state, forms, lists, and task actions have their own components.

Active tasks appear by default. A simple expandable Finished tasks section supports
reopening completed tasks without implementing the Milestone 4 navigation system.
No backend source, migrations, dependencies, notes, or other features were added.

Loading, empty, saving, error, retry, and deletion-confirmation states are implemented.
Save controls are disabled and guarded synchronously while requests are pending.
Failed saves preserve form values. Successful changes use the record returned by the
server; React state is only a display cache. No separate frontend persistence exists.

## Verification

| Check | Result |
| --- | --- |
| Frontend production build and TypeScript | Passed twice, including after final code adjustment; 34 modules built |
| Existing backend suite | 46 passed, 0 failed; 2 existing dependency warnings |
| Existing server task displayed | Milestone 2 demo loaded successfully |
| Browser creation and refresh | Created task #2; remained after full refresh |
| Browser editing and refresh | Renamed task and added due date; changes remained after full refresh |
| Description, due date, High priority | Verified together on saved task after refresh |
| Complete / reopen | Task moved to Finished tasks and back to Active tasks |
| Delete cancellation | Keep task preserved the record |
| Confirmed deletion and refresh | Test task disappeared and stayed deleted after refresh |
| Failed save | Stopped backend; error displayed and title/description remained populated |
| Failed list refresh | Error displayed; existing task and new-task draft remained visible |
| Recovery | Restarted backend; Refresh list loaded tasks successfully |
| Mobile visual inspection | 390 × 844; inspected form, error, task card, and wrapped action buttons |
| Desktop visual inspection | 1280 × 900; inspected two-column dashboard |

The existing Vite server on port 5173 was reused and applied source changes through
hot reload. The backend was running for CRUD checks, deliberately stopped for failure
checks, then started again on port 8000. Both are running for review.

The disposable browser-created task was deleted during verification. The Milestone 2
demo task was preserved. The unsaved failure-test draft was cleared by a browser reload
after its preservation and recovery were verified.

## Files created

Paths are relative to `C:\Users\weioo\LifeDesk`.

- `frontend/src/types.ts` — task types matching the API.
- `frontend/src/api/tasks.ts` — typed task requests, timeout and error handling.
- `frontend/src/components/TaskDashboard.tsx` — loading, refresh, server-returned state.
- `frontend/src/components/TaskForm.tsx` — shared create/edit form, validation and save state.
- `frontend/src/components/TaskList.tsx` — active and finished task sections, empty states.
- `frontend/src/components/TaskItem.tsx` — editing, completion/reopening, deletion confirmation.
- `MILESTONE-3-REPORT.md` — this report.

## Files modified

- `frontend/src/App.tsx` — replace foundation screen with dashboard page shell.
- `frontend/src/styles/app.css` — responsive dashboard, forms, cards and state styling.
- `README.md` — current scope and dashboard instructions.

Generated files also changed: `frontend/dist/index.html` and bundled assets, backend
pytest cache, and `data/lifedesk.db` during browser verification. No dependency lockfiles
or package manifests changed. Older build assets may remain on disk only as ignored
artifacts; the final build references the current bundle.

## Commands executed

Working directory was the project root unless noted. Source edits otherwise used
the patch tool; browser operations used the browser tool, not shell commands.

1. Inspect current frontend and API schemas and look for repository instructions:

   ```powershell
   Get-Content frontend/src/App.tsx; Get-Content frontend/src/styles/app.css; Get-Content frontend/src/api/client.ts; Get-Content frontend/package.json; Get-Content backend/app/schemas.py; rg --files -g AGENTS.md -g '!backend/pytest-cache-*'
   ```

2. Write the replacement App.tsx through a literal PowerShell here-string:

   ```powershell
   @'
   import TaskDashboard from './components/TaskDashboard';

   export default function App() {
     return (
       <main className="shell">
         <header>
           <a className="brand" href="/" aria-label="LifeDesk home">LifeDesk</a>
           <span className="version">A little space for your day</span>
         </header>
         <section className="welcome">
           <p className="eyebrow">YOUR DAILY DESK</p>
           <h1>Make room for what matters.</h1>
           <p className="intro">One place to capture your tasks and take the next step.</p>
         </section>
         <TaskDashboard />
         <footer>LifeDesk · Your personal daily desk</footer>
       </main>
     );
   }
   '@ | Set-Content -LiteralPath frontend/src/App.tsx
   ```

3. `npm run build` from `frontend` (approved build subprocess access). Internally
   invokes `npm run check`, `tsc --noEmit`, then `vite build`.
4. `.\.venv\Scripts\python.exe -m pytest` from `backend` (approved temporary database access).
5. Sent Ctrl+C to the existing backend process for the deliberate failure test.
6. `.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
   from `backend` to restore service.
7. `npm run build` from `frontend` again after keeping task forms mounted during
   list refresh and disabling new-task submission while a list load is pending.

## Warnings, diagnosed issues, and limits

- The initial patch was rejected because it tried to delete and add App.tsx in the
  same patch. No part of that patch applied. Retried as separate edits; no unrelated changes.
- Initial `rg` returned exit code 1 because no AGENTS.md matched; source reads succeeded.
- Browser automation's first date fill did not persist in the native date control.
  Entered the date using the native control, saved, and verified it after refresh.
  No backend or date-format redesign was necessary.
- The deliberately stopped backend produced expected failed-request errors. Ctrl+C
  returned exit code 1 from the process runner; restart succeeded.
- Backend tests retain the Milestone 1/2 warnings: Starlette TestClient's `httpx`
  deprecation and its use of AnyIO's deprecated BlockingPortal alias.
- No frontend build warnings or TypeScript errors.
- No new automated frontend test framework was added. Browser checks above were
  performed against the real backend. The empty-active-list state and deliberately
  slow pending-request/double-click behavior were reviewed in code but not separately
  exercised in the browser. The disabled controls and synchronous in-flight guards
  implement repeated-submission prevention.
- Responsive checks used mobile-sized browser windows, not a physical phone.
- Only saved data survives a full page reload; retaining unsaved drafts across page
  reloads is outside this milestone. After an ambiguous network timeout, check the
  refreshed server list before retrying a create request.

Stopped after Milestone 3; awaiting review before date-based views or other work.
