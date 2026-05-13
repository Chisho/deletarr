---
description: Essential rules — always loaded
---
# Generic Rules

## Driver-Mode (Operating Mode)

Track the current driver-mode for this conversation. Two values:

- **`backseat`** (default) — operate normally: use `Edit`, `Write`, `NotebookEdit` to make changes directly; let the user review afterwards.
- **`mainseat`** — do NOT call `Edit`, `Write`, or `NotebookEdit`. Walk the user through changes in plain language and provide ready-to-paste snippets the user applies themselves.

Mode is set conversationally:

- Every new conversation starts in **backseat** (the default).
- `/dev_mainseat` flips this conversation to mainseat.
- `/dev_backseat` reverts to backseat.

When launching a code-modifying subagent (e.g. frontend-developer, backend-developer) while in **mainseat**, include the directive *"Operate in mainseat mode — provide ready-to-paste snippets, do not call Edit/Write."* in the subagent's task description so the subagent inherits the mode. Read-only subagents (architect, code-reviewer) don't need this — they can't edit anyway.

## Pre-Production — No Legacy

This project is in active development with no production-stable contract or migrating users. Therefore:

- **No backward compatibility code.** If a schema, API, or format changes, update all consumers. No fallback paths for old formats.
- **No deprecated patterns or "legacy" labels.** If something is replaced, delete the old version entirely.
- **No stale documentation.** Context files must reflect the current implementation, not historical states. Remove outdated references immediately.
- **No dead code.** Unused functions, imports, and types must be deleted, not commented out or left "for later."

## Workflow

Follow this explicit sequence for every task:

**1. Explore**
Load relevant `.docs/` files, then read the codebase sections that will be affected.

**2. Plan**
Present a clear implementation plan for user review before writing any code.

**3. Implement**
Start work only after the plan is approved.

**4. Test**
There is no automated test suite yet. Validate as follows:

- **Backend changes** — run `python -m deletarr.main` against a real config with `dry_run: true`, or hit `GET /api/dry-run` while the API is running, and verify the summary is sensible. For changes to the deletion path, always exercise the dry-run path before the real-delete path.
- **Frontend changes** — run `cd frontend && npm run build` to catch syntax / import errors, then `npm run dev` and manually exercise the affected screens (Dashboard, DryRun, Settings).
- **Docker changes** — build locally with `docker build -t deletarr:test .` before pushing.

If you introduce non-trivial logic, add tests under a new `tests/` directory (pytest for backend, the frontend's existing toolchain for UI).

**5. Housekeeping**
Update relevant `.docs/` docs if something meaningful changed. Move the task from `todo.md` to `todo_done.md`. If a new system or concept was introduced that doesn't fit an existing doc, ask the user if it's worth creating a new `.docs/` file. When a doc is added or removed, update both the `.docs/` folder and the Context Files list in `CLAUDE.md` to stay in sync. **If project scope, stack, or run instructions change, update `CLAUDE.md` ("What This Project Does" / "How to Run") to match — it's a hand-written doc and won't drift in sync on its own.**

## Missing Setup Data (`{{TODO}}` markers)

When the user makes a request, check whether `.docs/` files contain `{{TODO: ...}}` markers in sections the request depends on (tech stack, deployment target, project scope, key systems, etc.). If a relevant TODO is unfilled, **stop and tell the user which TODO is in the way** — name the file, the section, and what's missing. Do not guess or invent values.

## No Hardcoded User Paths

Use `~` or `$HOME`, never absolute paths with username.

## Agents

Use specialized agents (`.claude/agents/`) for domain-specific tasks. Agents can run in foreground or background. Always tell the user which agent you are invoking and why before launching it.

- **architect** *(read-only)* — call before designing new features, restructuring modules, or deciding where new code should live. Returns options with trade-offs and an implementation plan; the main session applies the result.
- **code-reviewer** *(read-only)* — call after non-trivial edits to surface correctness, quality, and security issues. Reviews `git diff`, not the whole tree.
- **frontend-developer** — call for UI work in `frontend/` (React 19, Vite 7, Tailwind 4). Honors driver-mode (pass the mainseat directive when the conversation is in mainseat).
- **backend-developer** — call for FastAPI endpoints, qBittorrent / Radarr / Sonarr integration, deletion-pipeline logic, or YAML config schema changes. Honors driver-mode.

---

# Project-Specific Rules

Deletarr deletes data — torrents and the files behind them. Treat the deletion path with care:

- **Default to dry-run when validating changes.** When modifying logic in [deletarr/main.py](deletarr/main.py), [deletarr/processor.py](deletarr/processor.py), or `QbitClient.delete_torrents` in [deletarr/clients.py](deletarr/clients.py), validate with `dry_run: true` in `config/config.yml` (or `GET /api/dry-run`) before exercising the real-delete path.
- **Preserve the safety checks.** `min_seed_days` and `max_delete_percent` exist to make accidental mass-deletion impossible. Don't remove them, don't lower their defaults, and don't add code paths that bypass them.
- **Hardlink semantics are load-bearing.** [deletarr/utils.py:has_hardlinks_to_folder](deletarr/utils.py#L28) is how Deletarr decides a torrent file is no longer needed by Radarr / Sonarr. A regression there can cause real data loss — read carefully and prefer adding tests over speculative refactors.
- **Config writes must stay atomic.** [deletarr/api.py](deletarr/api.py) writes config to a `.tmp` file and `os.replace`s it. Preserve that pattern for any new endpoint that mutates `config.yml` — a half-written config can break the next run.
