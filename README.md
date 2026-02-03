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
  -p 5000:5000 \
  -v /path/to/config:/config \
  -v /path/to/movies:/movies \
  -v /path/to/tv:/tv \
  --restart unless-stopped \
  stefanc/deletarr:latest
```

3. Access the Web UI at `http://localhost:5000`.

## Configuration

All configuration is handled through the Web UI. Upon first run, you can set up your:
- qBittorrent connection (URL, Username, Password)
- Radarr/Sonarr API details and root folders
- Safety limits (Max delete percentage, Min seed days)

## Development and Pushing

The project includes utility scripts for developers:

- `./push-dev.sh`: Stages, commits, and pushes to Git, then builds and pushes a `dev` tagged Docker image.
- `./push-release.sh`: Handles versioning, Git tagging, and pushes `latest` and versioned Docker images.

## Disclaimer

Use with caution. While Deletarr includes safety features like dry runs and hardlink detection, it is capable of deleting data. Always perform a dry run first when changing your configuration.