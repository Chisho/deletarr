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