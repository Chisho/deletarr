# Architecture

## Directory Layout

```
.
├── deletarr/               # Python backend package
│   ├── __init__.py
│   ├── api.py              # FastAPI app: REST endpoints + static serving of the SPA
│   ├── clients.py          # QbitClient + Radarr/Sonarr HTTP helpers
│   ├── config.py           # YAML loading, logging setup, version lookup
│   ├── main.py             # `run_deletarr()` orchestration + CLI entry point
│   ├── processor.py        # Per-service deletion candidate selection (hardlink + safety)
│   └── utils.py            # Path normalization, hardlink detection
├── frontend/               # React 19 + Vite 7 + Tailwind 4 SPA
│   ├── src/
│   │   ├── App.jsx         # Top-level router (switch on activePage)
│   │   ├── main.jsx        # React entry
│   │   ├── layout/         # Layout.jsx — shell + navigation
│   │   ├── pages/          # Dashboard.jsx, DryRun.jsx, Settings.jsx
│   │   ├── components/     # Console.jsx + ui/ primitives
│   │   ├── lib/utils.js    # `cn` helper (clsx + tailwind-merge)
│   │   └── index.css       # Tailwind entry + custom layers
│   ├── package.json        # React 19, axios, lucide-react, clsx, tailwind-merge
│   ├── vite.config.js
│   └── tailwind.config.js
├── config/                 # Local runtime config (config.yml) — user-edited
├── config_sample/          # Reference schema (config.yml.sample)
├── Dockerfile              # 2-stage build: frontend (node:20-alpine) → backend (python:3.10-slim); ARG VERSION sets the OCI version label
├── entrypoint.sh           # Container entrypoint: `uvicorn deletarr.api:app`
├── dev-server.sh           # Local dev convenience: backend + frontend together
├── push-release.sh / .bat  # Release helper: git add / commit / tag / push --follow-tags. CI handles Docker publishing on tag push.
├── requirements.txt        # Backend deps
└── version.txt             # Single source of truth for app version
```

## Key Systems

### Deletion pipeline ([deletarr/main.py](deletarr/main.py))

`run_deletarr()` is the entry point for both CLI and API runs:

1. Resolves the config path: `$DELETARR_CONFIG` → `/config/config.yml` (Docker mount) → `./config/config.yml` (local).
2. Loads YAML via [deletarr/config.py:load_config](deletarr/config.py#L6) (raises `ConfigError` on failure — surfaces as `{"success": False, "error": ...}` rather than `sys.exit`), sets up logging.
3. Constructs `QbitClient` from the `qBittorrent` section.
4. For each enabled service (`Radarr`, `Sonarr`), calls [deletarr/processor.py:process_service](deletarr/processor.py#L7) which:
   - Aborts the service immediately if `root_folder` isn't a directory (e.g. unmounted) — without this, the hardlink walk would silently yield nothing and every torrent would become a candidate.
   - Fetches fully-downloaded torrents in the configured `category` from qBittorrent.
   - Filters out torrents whose `completion_on` is more recent than `min_seed_days` ago.
   - For each remaining torrent, walks its files and checks [deletarr/utils.py:has_hardlinks_to_folder](deletarr/utils.py#L28) against the service's `root_folder`. A torrent with **no** hardlinks into the media library becomes a delete candidate. If the check raises `HardlinkCheckError` (cannot determine), the torrent is kept.
   - Applies the per-service `max_delete_percent` safety check on the candidate set vs. the total. If it would exceed the threshold, the service aborts (returns `[]`).
5. If `dry_run` is false, calls `QbitClient.delete_torrents(..., delete_data=True)` which returns the list of hashes that were *actually* deleted (a single failure no longer reports the whole batch as success).
6. Returns a structured dict: `{success, summary, dry_run, deleted_count}` (or `{success: False, error}` on exception).

The CLI entry (`python -m deletarr.main`) additionally prints a human-readable summary via `print_summary()`.

### Hardlink detection ([deletarr/utils.py:has_hardlinks_to_folder](deletarr/utils.py#L28))

The load-bearing safety check. For each torrent file:

1. Verifies `target_folder` exists and is a directory; raises `HardlinkCheckError` otherwise.
2. `os.stat(file_path)`. If the source can't be stat'd, raises `HardlinkCheckError`. If `st_nlink <= 1` there are no extra hardlinks → safe to delete from the seed side, because no media manager is referencing it.
3. Otherwise walks the service's `root_folder` and matches `st_ino` + `st_dev` against the source. A match means the torrent file is still hardlinked into the media library → skip deletion. Errors walking the target raise `HardlinkCheckError`; individual unreadable files inside the walk are tolerated and skipped.

Callers must treat `HardlinkCheckError` as "do not delete this torrent". `process_service` does exactly this. A regression here can cause real data loss — never let an error path silently return `False`.

### REST API ([deletarr/api.py](deletarr/api.py))

FastAPI app exposing:

- `GET /api/health` — version + env probe.
- `GET /api/health/services` — tests qBittorrent / Radarr / Sonarr connectivity using the saved config.
- `GET /api/config` / `POST /api/config` — read + atomic-write the YAML config (temp file + `os.replace`).
- `GET /api/logs` — last 200 log lines from an in-memory `ListHandler` attached to root + uvicorn loggers.
- `GET /api/dry-run` — synchronously runs the pipeline with `dry_run=True` and returns the summary.
- `POST /api/run` — synchronously runs the pipeline with `dry_run=False` and returns the summary.
- Catch-all `GET /{full_path:path}` — serves the React SPA from `$FRONTEND_DIST` (defaults to `frontend/dist`) with SPA fallback to `index.html`. Unknown `/api/*` paths return 404 (not the SPA HTML), and the requested path is resolved with `realpath`+`commonpath` to block traversal outside the dist root.

CORS is wide-open (`allow_origins=["*"]`) to support the Vite dev server hitting a separately-hosted backend during local development.

The app is single-process and synchronous — there is no background scheduler in code; "scheduled" runs are handled externally (e.g. cron in a container that calls the API, or manual triggers from the UI).

### Frontend ([frontend/src/](frontend/src/))

React 19 SPA built with Vite 7 and styled with Tailwind 4. Three top-level pages are selected by `App.jsx` state — there is no router library:

- **Dashboard** ([frontend/src/pages/Dashboard.jsx](frontend/src/pages/Dashboard.jsx)) — health + recent activity.
- **DryRun** ([frontend/src/pages/DryRun.jsx](frontend/src/pages/DryRun.jsx)) — triggers `GET /api/dry-run` and renders the resulting deletion preview.
- **Settings** ([frontend/src/pages/Settings.jsx](frontend/src/pages/Settings.jsx)) — loads / saves `/api/config` (qBittorrent, Radarr, Sonarr, safety limits).

[frontend/src/components/Console.jsx](frontend/src/components/Console.jsx) renders the rolling log buffer from `/api/logs`. UI primitives live under `frontend/src/components/ui/`. Built artifacts in `frontend/dist/` are served by FastAPI in production.

The frontend is plain JSX (no TypeScript). State is local-component-only (`useState`); there is no global store.

### Configuration ([config/config.yml](config/config.yml))

YAML schema, mirrored in [config_sample/config.yml.sample](config_sample/config.yml.sample):

- `qBittorrent`: `{url, username, password}`
- `Radarr` / `Sonarr`: `{enabled, url, api_key, root_folder, category, min_seed_days, max_delete_percent}`
- `dry_run` (bool, defaults to `True` in code if absent; sample also ships `true` so new users can't accidentally delete)
- `logging`: `{level, file}`

`max_delete_percent` is a per-service safety limit read inside `processor.py` from the `Radarr` / `Sonarr` blocks. A value of `10` means "abort this service's run if more than 10% of category torrents would be deleted".

### Deployment

- **Docker** — two-stage build in [Dockerfile](Dockerfile): stage 1 builds the frontend with `node:20-alpine`, stage 2 copies the dist into `python:3.10-slim`, installs `requirements.txt`, and runs [entrypoint.sh](entrypoint.sh) → `uvicorn deletarr.api:app --host 0.0.0.0 --port 8000`. `ARG VERSION` is injected by CI from `version.txt` to set the `org.opencontainers.image.version` label. A `HEALTHCHECK` polls `/api/health` via the in-image Python.
- **Distribution** — published as `stefanc/deletarr:{vX.Y.Z, X.Y, latest}` on Docker Hub by [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml). `linux/amd64` only — arm64 was dropped because the only deployment target is an x86_64 TrueNAS box and QEMU-emulated arm64 builds were taking 30+ min. The workflow runs **only on `v*` tag pushes and pull requests** — direct pushes to main don't trigger CI (avoids double-running every release, since `git push --follow-tags` would otherwise fire both a branch build and a tag build for the same commit). PRs build but don't publish; tag pushes build and publish. GHA buildx cache (`type=gha`) is enabled for fast incremental rebuilds.
- **Versioning** — single source of truth in [version.txt](version.txt), read at runtime by [deletarr/config.py:get_version](deletarr/config.py#L45) and at build time as `--build-arg VERSION=...`. [push-release.sh](push-release.sh) is purely a git helper (commit + tag + `git push --follow-tags`); Docker publishing happens entirely in CI.
