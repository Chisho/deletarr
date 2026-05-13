# Deletarr

Deletarr is a media management tool that helps you keep your download client clean by identifying and deleting torrents that no longer have corresponding media files in your Radarr or Sonarr libraries.

Unlike traditional scripts, Deletarr features a modern **Web UI** for management, monitoring, and manual triggers.

## Key Features

- **Web Interface**: Easy setup and status monitoring.
- **Hardlink Detection**: Safely identifies if a torrent is still being used for seeding via hardlinks.
- **Dry Run Mode**: Preview deletions before they happen.
- **Radarr & Sonarr Integration**: Works with both major media managers.
- **qBittorrent Support**: Specifically designed for qBittorrent users.

## Quick Setup (Docker)

The easiest way to run Deletarr is via Docker.

1. Create a directory for your configuration.
2. Run the container:

```bash
docker run -d \
  --name=deletarr \
  -p 8000:8000 \
  -v /path/to/config:/config \
  -v /path/to/movies:/movies \
  -v /path/to/tv:/tv \
  --restart unless-stopped \
  stefanc/deletarr:latest
```

3. Access the Web UI at `http://localhost:8000`.

The image is multi-arch (`linux/amd64`, `linux/arm64`) — pulling `:latest` will resolve to the right architecture automatically.

## TrueNAS SCALE Setup

When installing as a "Custom App" in TrueNAS SCALE:
1. **Image**: `stefanc/deletarr:latest` (or pin a specific version like `:v1.3.0` if you don't want automatic updates).
2. Under **Networking**, map Container Port `8000` to a Node Port (e.g., `30080`).
3. Under **Web UI**, enter that same Node Port to enable the "WebUI" button in the Apps dashboard.

Each release re-tags `:latest` on Docker Hub, so updating from TrueNAS picks up the new image on the next pull.

## Configuration

All configuration is handled through the Web UI. Upon first run, you can set up your:
- qBittorrent connection (URL, Username, Password)
- Radarr/Sonarr API details and root folders
- Safety limits (Max delete percentage, Min seed days)

## Development and Releasing

Docker Hub publishing is handled by GitHub Actions ([.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)) — never run `docker push` locally.

- **Day-to-day commits**: just `git add . && git commit -m "..." && git push`. CI builds on every push to `main` as a sanity check but does **not** publish to Docker Hub.
- **Releasing a new version**: bump [version.txt](version.txt), then run `./push-release.sh`. It commits, tags, and pushes — CI then builds multi-arch and publishes `:vX.Y.Z`, `:X.Y`, and `:latest` to Docker Hub.

You can watch the release run with `gh run watch --workflow=docker-build.yml`.

## Disclaimer

Use with caution. While Deletarr includes safety features like dry runs and hardlink detection, it is capable of deleting data. Always perform a dry run first when changing your configuration.