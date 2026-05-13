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

_No open bugs._

**Tally:** 0

## TASK

### TASK-4 [Medium] — Replace `window.confirm` with a typed-confirmation modal for real delete
**Action:** In [frontend/src/pages/DryRun.jsx:41](frontend/src/pages/DryRun.jsx#L41), replace the native confirm with a modal that:
- Shows per-service counts and total reclaimable size.
- Requires the user to type `DELETE N ITEMS` to enable the confirm button.
- Differentiates clearly from the dry-run path.
**Why:** A single native confirm is the only gate before destructive work.

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

**Tally:** 4

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
