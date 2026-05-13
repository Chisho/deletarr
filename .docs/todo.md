# TODO — Deletarr Open Tasks & Bugs

Only NOT DONE items. For completed tasks and fixed bugs, see `.docs/todo_done.md`.

> **Convention:** New entries are always added **at the end** of their type section.
> The tally at the bottom of each section is the count of **open** items in that section only — re-derive it after any add/move.
> To pick the next ID, scan both `todo.md` and `todo_done.md` for the highest existing ID in that section and add 1 (so IDs stay stable when items move between files).

---

## Priority Legend

- **High** — needs attention soon (broken behavior, blocking work, security exposure, data-loss risk)
- **Medium** — should be done, but not urgent
- **Low** — nice to have, polish, minor improvements

Entries are grouped by **type**:

- **TASK** — generic work item
- **BUG** — defect to fix
- **CR** — scoped change request / feature
- **DOCS** — documentation work

---

## BUG

### BUG-4 [High] — qBit `get_torrents` returns `[]` on error; failed run looks identical to "nothing to do"
**Action:** In [deletarr/clients.py:24-43](deletarr/clients.py#L24-L43), raise on connection / auth failure instead of returning `[]`. In [deletarr/main.py](deletarr/main.py), catch and abort the run with `success: False` and a clear error.
**Why:** Today an unreachable qBittorrent silently produces a "0 candidates" run that looks healthy.

### BUG-9 [Medium] — `DryRun.jsx` crashes when a service is disabled
**Action:** In [frontend/src/pages/DryRun.jsx:143](frontend/src/pages/DryRun.jsx#L143) and any other reads of `results.summary.Radarr` / `results.summary.Sonarr`, use optional chaining (`results.summary.Sonarr?.length ?? 0`).
**Why:** Disabled services are absent from the backend summary, so the page throws on render.

### BUG-10 [Medium] — `progress == 1.0` float-equality filter is fragile
**Action:** In [deletarr/clients.py:37](deletarr/clients.py#L37), replace the Python-side `progress == 1.0` filter with `status_filter='completed'` passed directly to `torrents_info()`.
**Why:** Float equality on `progress` can drop legitimately-completed torrents reported as `0.9999...`.

### BUG-11 [Medium] — SPA catch-all returns 200 for `/api/...` typos and is path-traversable
**Action:** In [deletarr/api.py:179-188](deletarr/api.py#L179-L188):
- If `full_path.startswith("api/")`, raise `HTTPException(404)` so unknown API routes don't return `index.html`.
- Resolve the requested path with `os.path.realpath` and verify it stays under `FRONTEND_DIST` via `os.path.commonpath` before serving.
**Why:** Today `GET /api/whatever` quietly returns the SPA HTML; and the unguarded `FileResponse(os.path.join(...))` allows directory traversal.

### BUG-12 [Medium] — `load_config` calls `sys.exit(1)` from a library function
**Action:** In [deletarr/config.py:12](deletarr/config.py#L12), raise a `ConfigError` (define if needed) instead of `sys.exit`. CLI entrypoint in `main.py` catches and exits; API handlers in `api.py` return 500 with the message.
**Why:** `sys.exit` inside a FastAPI handler aborts the worker process.

### BUG-13 [Low] — `Settings.jsx` mutates a shallow-cloned config object
**Action:** In [frontend/src/pages/Settings.jsx:71-80](frontend/src/pages/Settings.jsx#L71), replace the shallow spread + walk with `structuredClone(config)` before mutating the path.
**Why:** Saves work today because of the top-level reference swap, but this is a latent footgun the next time anyone touches state shape.

**Tally:** 6

## TASK

### TASK-3 [High] — Add a concurrency lock and CSRF gate to `/api/run`
**Action:** In [deletarr/api.py:143-165](deletarr/api.py#L143-L165):
- Wrap `run_deletarr` calls in a module-level `threading.Lock` (or `asyncio.Lock` if the handler becomes async); return HTTP 409 if busy.
- Require the client to echo a token returned by the prior `/api/dry-run` response.
- Tighten the CORS config at [deletarr/api.py:43-49](deletarr/api.py#L43-L49) — pin `allow_origins` to known dev origins; `allow_origins=["*"]` + `allow_credentials=True` is browser-rejected anyway.
**Why:** Today an unauthenticated POST from any origin on the LAN can trigger a destructive run, and two concurrent calls double-delete via the threadpool.

### TASK-4 [Medium] — Replace `window.confirm` with a typed-confirmation modal for real delete
**Action:** In [frontend/src/pages/DryRun.jsx:41](frontend/src/pages/DryRun.jsx#L41), replace the native confirm with a modal that:
- Shows per-service counts and total reclaimable size.
- Requires the user to type `DELETE N ITEMS` to enable the confirm button.
- Differentiates clearly from the dry-run path.
**Why:** A single native confirm is the only gate before destructive work.

### TASK-5 [Medium] — Remove dead code
**Action:** Delete (or wire in if intentional) the following per the "no dead code" rule:
- [deletarr/clients.py:54-91](deletarr/clients.py#L54-L91) `radarr_get_movies`, `sonarr_get_series`.
- [deletarr/utils.py:8-26](deletarr/utils.py#L8-L26) unused media-file helpers and `normalize_path`.
- [deletarr/utils.py:63-65](deletarr/utils.py#L63-L65) unreachable second `except` block.
- [deletarr/api.py:61-67](deletarr/api.py#L61-L67) empty deprecated `@app.on_event` handlers.
- [frontend/src/components/Console.jsx:2](frontend/src/components/Console.jsx#L2) unused `Minimize2`/`Maximize2` imports.
- `axios` in [frontend/package.json](frontend/package.json) (codebase uses `fetch` everywhere).
- [deletarr/processor.py:8-11](deletarr/processor.py#L8-L11) and [:44-47](deletarr/processor.py#L44-L47) duplicate variable assignments.

### TASK-6 [Medium] — Per-torrent decision logging at INFO level
**Action:** In [deletarr/processor.py](deletarr/processor.py), after each decision, log one structured line:
- `[Radarr] KEEP 'name' (3/12 files hardlinked)`
- `[Radarr] SKIP 'name' (seeding 4.2d < 30d)`
- `[Radarr] CANDIDATE 'name' (0 hardlinks)`
**Why:** Today the only way to answer "why was this torrent kept?" is to re-run at DEBUG.

### TASK-7 [Medium] — Hoist `Field` component out of `Settings.jsx` render body
**Action:** Move the `Field` definition at [frontend/src/pages/Settings.jsx:132](frontend/src/pages/Settings.jsx#L132) above the parent component, outside its render scope.
**Why:** Re-creating component identities each render risks losing focus on input fields when state shape grows.

### TASK-8 [Low] — Console toggle a11y + autoscroll behavior
**Action:** In [frontend/src/components/Console.jsx](frontend/src/components/Console.jsx):
- Replace the `<div onClick>` toggle (line 37) with `<button aria-expanded={isOpen}>`.
- Track whether the user has scrolled away from the bottom; only autoscroll when already at the bottom.
- Pause the 2 s polling when `!isOpen`.
**Why:** Today the toggle isn't keyboard-accessible and autoscroll fights the user.

### TASK-9 [Low] — Add `aria-current="page"` to sidebar nav items
**Action:** In [frontend/src/layout/Layout.jsx](frontend/src/layout/Layout.jsx), pass `aria-current="page"` on the active `SidebarItem`.

**Tally:** 7

## CR

### CR-1 [Medium] — Centralize frontend API calls in `frontend/src/lib/api.js`
**Action:** Create `frontend/src/lib/api.js` exporting `getConfig`, `saveConfig`, `getHealth`, `getServiceHealth`, `dryRun`, `realRun`, `getLogs`, `getLastRun`. Replace direct `fetch('/api/...')` calls in [Dashboard.jsx](frontend/src/pages/Dashboard.jsx), [DryRun.jsx](frontend/src/pages/DryRun.jsx), [Settings.jsx](frontend/src/pages/Settings.jsx). One central place for error handling and JSON parsing.

### CR-2 [Medium] — Persist last-run summary; expose `GET /api/last-run`
**Action:** In [deletarr/main.py](deletarr/main.py), after each run, write the summary to `./config/last_run.json` (atomic write via `.tmp` + `os.replace`, same pattern as `api.py:124-129`). Add `GET /api/last-run` in [deletarr/api.py](deletarr/api.py) that returns it. Use this on the Dashboard.

### CR-3 [Medium] — Backend returns `skipped` + `aborted` per service; UI renders "Why these weren't deleted"
**Action:**
- In [deletarr/processor.py](deletarr/processor.py), return a structured per-service result: `{ candidates: [...], skipped: [{name, reason: 'min_seed_days'|'no_files_listable'}], aborted: false|{reason: 'max_delete_percent_exceeded', would_delete, total}}`.
- In [frontend/src/pages/DryRun.jsx](frontend/src/pages/DryRun.jsx), render a collapsible "Why these weren't deleted" section and a destructive banner when `aborted` is set.
**Why:** Today a `max_delete_percent` abort is indistinguishable from a clean library.

### CR-4 [Medium] — Dashboard becomes the cockpit
**Action:** Replace the static health-only [Dashboard.jsx](frontend/src/pages/Dashboard.jsx) layout with:
- Last-run summary card (counts, size, mode, timestamp) sourced from CR-2.
- "Run Dry-Run Now" primary CTA → jumps to DryRun with the run already started.
- Keep the service-health row but compact it.

### CR-5 [Medium] — Pydantic-validate `POST /api/config`
**Action:** In [deletarr/api.py](deletarr/api.py), define a Pydantic model mirroring the YAML schema. Reject unknown keys, missing required fields, and out-of-range values (e.g. `max_delete_percent` 0–100, `min_seed_days >= 0`). Preserve the atomic `.tmp` + `os.replace` write.
**Why:** Today a malformed POST overwrites a working config with garbage.

### CR-6 [Low] — SSE log streaming with filter
**Action:** Add `GET /api/logs/stream` in [deletarr/api.py](deletarr/api.py) as a `text/event-stream` endpoint backed by the existing `ListHandler`. In [Console.jsx](frontend/src/components/Console.jsx), consume via `EventSource`, add a level filter (`DEBUG/INFO/WARNING/ERROR`), copy button, and per-level coloring. Drop the 2 s poll.

### CR-7 [Low] — Add `size` and `completion_on` to dry-run rows
**Action:** Plumb `size` and `completion_on` from `QbitClient.get_torrents` through `processor.process_service` into the summary; render columns in [DryRun.jsx:118-122](frontend/src/pages/DryRun.jsx#L118). Show per-service size totals.

### CR-8 [Low] — Add config keys: `exclude_tags`, `protected_trackers`, `min_ratio`
**Action:** Extend the per-service config schema and consume in [deletarr/processor.py](deletarr/processor.py):
- `exclude_tags: [keep, private]` — never delete torrents with any of these tags.
- `protected_trackers: [tracker.example.org]` — skip torrents on these trackers.
- `min_ratio: 1.0` — additional gate alongside `min_seed_days`.
Expose in Settings UI.

**Tally:** 8

## DOCS

### DOCS-2 [Medium] — Fix typos in `config.yml.sample`
**Action:** In [config_sample/config.yml.sample:10,19](config_sample/config.yml.sample#L10), the comments read `YOUR_*_USERNAME` for what is actually the service URL field. Replace with `YOUR_RADARR_URL` / `YOUR_SONARR_URL`.

**Tally:** 1
