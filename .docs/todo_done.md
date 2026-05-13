# DONE — Deletarr Completed Tasks & Bugs

Only DONE items. For open tasks, see `.docs/todo.md`.

---

## TASK

### TASK-1 [High] — Stop pushing Docker images from the laptop; let CI be the only publisher
**Done:** Stripped all `docker build` / `docker push` blocks from [push-release.sh](push-release.sh) and [push-release.bat](push-release.bat); deleted `push-dev.sh` and `push-dev.bat` entirely (without the docker step they were just `git commit && git push`). [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml) is now the only publisher — push condition tightened to `startsWith(github.ref, 'refs/tags/v')` so main pushes build (sanity check) but don't publish to Docker Hub. Added buildx GHA cache (`cache-from: type=gha`, `cache-to: type=gha,mode=max`) for fast incremental rebuilds.

### TASK-2 [High] — Add HEALTHCHECK to the Docker image
**Done:** [Dockerfile](Dockerfile) now includes a `HEALTHCHECK` that polls `/api/health` via `python -c "import urllib.request; urllib.request.urlopen(...)"` — using the in-image Python rather than installing curl. Interval 30s, timeout 5s, start-period 15s, 3 retries.

## BUG

### BUG-1 [High] — `max_delete_percent` saved/read in two different places (safety check disabled)
**Done:** Moved `max_delete_percent` out of the `logging:` block and into each service block.
- [config_sample/config.yml.sample](config_sample/config.yml.sample) — added `max_delete_percent: 10` under both `Radarr:` and `Sonarr:`; removed from `logging:`.
- [frontend/src/pages/Settings.jsx](frontend/src/pages/Settings.jsx) — replaced the single General-card field with `Radarr.max_delete_percent` and `Sonarr.max_delete_percent` fields rendered alongside `Min Seed Days` in each service card.

### BUG-2 [High] — Hardlink check returns "safe to delete" on errors
**Done:** [deletarr/utils.py](deletarr/utils.py) — `has_hardlinks_to_folder` now raises a new `HardlinkCheckError` on any uncertainty (missing target folder, unstat-able source, error walking the target). Deleted the duplicate unreachable `except` block. [deletarr/processor.py](deletarr/processor.py) — added an upfront `os.path.isdir(root_folder)` check that aborts the service cleanly; per-file calls to the hardlink check are now wrapped in `try/except HardlinkCheckError` and treat uncertainty as "keep the torrent". This closes the regression where an unmounted root folder would turn every torrent into a delete candidate.

### BUG-3 [High] — `FastAPI(...)` instantiated twice; CORS middleware silently dropped
**Done:** Deleted the duplicate `app = FastAPI(...)` constructor at [deletarr/api.py:51](deletarr/api.py#L51). CORS middleware attached on line 43 now applies.

### BUG-5 [High] — `delete_torrents` over-reports success on partial failure
**Done:** [deletarr/clients.py](deletarr/clients.py) — `QbitClient.delete_torrents` now wraps each per-hash delete in its own try/except and returns the list of hashes that were actually deleted. [deletarr/main.py](deletarr/main.py) — captures the returned list, sets `deleted_hashes`/`deleted_count` from it, and logs successes vs. failures separately.

### BUG-6 [High] — `dry_run: false` shipped in sample config
**Done:** Flipped [config_sample/config.yml.sample](config_sample/config.yml.sample) to `dry_run: true`. New users following the README now get the safe default.

### BUG-7 [High] — Hardcoded `version="1.3.0"` in `api.py`
**Done:** [deletarr/api.py](deletarr/api.py) now imports `get_version` from `deletarr.config` and uses it for both the `FastAPI(version=...)` constructor and the `/api/health` response body. Single source of truth is [version.txt](version.txt).

### BUG-8 [High] — Hardcoded `version` label in Dockerfile drifts from version.txt
**Done:** [Dockerfile](Dockerfile) replaced the literal `LABEL version="1.3.0"` with `ARG VERSION=unknown` + `LABEL org.opencontainers.image.version="${VERSION}"` (OCI-standard key). CI reads `version.txt` and passes it as `--build-arg VERSION=...` to `docker/build-push-action`. Also swapped the other ad-hoc labels to OCI-standard keys (`org.opencontainers.image.description`, `org.opencontainers.image.source`).

## CR

_No completed change requests yet._

## DOCS

### DOCS-1 [High] — Document the TrueNAS update flow in README
**Done:** [README.md](README.md) — added a multi-arch note in the Quick Setup section, updated the TrueNAS SCALE section to explicitly say `:latest` works (each release re-tags it), and rewrote the "Development and Releasing" section to reflect the CI-only Docker publishing flow. (Earlier draft included a pull-policy warning for TrueNAS SCALE; removed after user clarified other containers update fine with `:latest` on their setup — the real fix was eliminating the local push race.)

### DOCS-3 [Medium] — Update `.docs/architecture.md` once BUG-1 and TASK-1 land
**Done:** [.docs/architecture.md](.docs/architecture.md) — removed the `max_delete_percent` known-discrepancy note (handled when BUG-1 landed); updated the directory layout and Deployment section to reflect the CI-only Docker publishing flow, the `ARG VERSION` injection, the `HEALTHCHECK`, the release-only tag rule, and the buildx cache. Removed references to the deleted `push-dev.sh`.
