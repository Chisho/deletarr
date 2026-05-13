# CLAUDE.md

## What This Project Does

Deletarr is a media-library cleanup tool. It identifies torrents in qBittorrent that are no longer hardlinked into the Radarr / Sonarr media folders (movies / TV) and deletes them — freeing seedbox storage without breaking active hardlinks. A FastAPI backend exposes a small REST API and serves a React + Vite + Tailwind web UI for configuration, manual dry-runs, and live log viewing.

Safety features baked into the pipeline:

- **Hardlink detection** — a torrent is only deleted if no file in it is still hardlinked into the Radarr / Sonarr `root_folder`.
- **`min_seed_days`** per service — skip torrents that haven't been seeding long enough since completion (default 30 days).
- **`max_delete_percent`** — abort a service run if it would delete more than the configured percentage of its candidates.
- **`dry_run`** mode — preview deletions without touching qBittorrent.

## How to Run

**Local development**

```bash
# Backend (FastAPI)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DELETARR_CONFIG=./config/config.yml uvicorn deletarr.api:app --reload --host 0.0.0.0 --port 8000

# Frontend (Vite dev server, in a second shell)
cd frontend && npm install && npm run dev

# Or both at once
./dev-server.sh
```

**CLI run (no Web UI)**

```bash
python -m deletarr.main
```

**Docker**

```bash
docker run -d --name deletarr \
  -p 8000:8000 \
  -v /path/to/config:/config \
  -v /path/to/movies:/movies \
  -v /path/to/tv:/tv \
  --restart unless-stopped \
  stefanc/deletarr:latest
```

Web UI: <http://localhost:8000>. Config file is `./config/config.yml` locally or `/config/config.yml` in the container — see `config_sample/config.yml.sample` for the schema.

## Rules (auto-loaded)

Essential rules live in `.claude/rules/rules.md` — edit there to add/remove.

## Agents

Available in `.claude/agents/`:

- **architect** *(read-only)* — system design, project structure, technical decisions
- **code-reviewer** *(read-only)* — code quality, correctness, best practices
- **frontend-developer** — React + Vite + Tailwind UI work (honors driver-mode)
- **backend-developer** — FastAPI / Python server logic, qBittorrent + Radarr/Sonarr integration (honors driver-mode)

## Context Files (load on demand)

- `.docs/architecture.md` — directory layout, module responsibilities, request / data flow
- `.docs/todo.md` — open tasks and bugs
- `.docs/todo_done.md` — completed work archive
