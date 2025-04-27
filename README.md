# Deletarr

A Python-based utility for automatically cleaning up completed torrents from qBittorrent that are no longer present in your Radarr/Sonarr media libraries.

## Quick Setup

1. Mount the `/config` directory with your configuration file when running the container
2. Copy `config_sample/config.yml.sample` to your config directory as `config.yml`
3. Edit the config.yml with your qBittorrent, Radarr, and Sonarr settings

## Configuration

The application requires a `config.yml` file in the mounted `/config` directory. You can use the provided sample at `config_sample/config.yml.sample` as a reference. The configuration file needs:

- qBittorrent connection details
- Radarr/Sonarr API settings
- Root folder paths for your media libraries
- Category names that match your Radarr/Sonarr download categories in qBittorrent

### Example Config Structure:
```yaml
qBittorrent:
  url: "http://localhost:8080/"
  username: "admin"
  password: "adminpass"

Radarr:
  url: "http://localhost:7878/"
  api_key: "your-api-key"
  category: "radarr"
  root_folder: "/path/to/movies"

Sonarr:
  url: "http://localhost:8989/"
  api_key: "your-api-key"
  category: "tv-sonarr"
  root_folder: "/path/to/tv"
```

## Usage

### Using Docker:

```bash
docker run -d \
  --name=deletarr \
  -v /path/to/your/config:/config \
  --restart unless-stopped \
  deletarr
```

### Environment Variables

- `DELETARR_CONFIG`: Path to config file (default: `/config/config.yml`)

## How It Works

1. Connects to qBittorrent and gets a list of completed torrents in configured Radarr/Sonarr categories
2. Scans the media root folders for existing files
3. Identifies torrents whose files are no longer present in the media folders
4. Deletes the identified torrents from qBittorrent (with data if configured)

## Features

- Scheduled execution using cron syntax (configurable)
- Dry-run mode for testing
- Separate handling for movies (Radarr) and TV shows (Sonarr)
- Detailed logging with configurable levels
- Safety limit on maximum deletion percentage
- Docker support for easy deployment

## Advanced Configuration

### Logging:
```yaml
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
  file: "deletarr.log"
```

### Safety Features:
```yaml
dry_run: true  # Set to false to enable actual deletion
max_delete_percent: 30  # Abort if more than this percent would be deleted
```

### Schedule:
```yaml
schedule: "0 5 * * *"  # Runs at 5 AM daily
```