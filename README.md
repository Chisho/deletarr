# Deletarr

This container sets up a cron scheduler that will automatically run `deletarr.py` at the scheduled interval. The script checks for missing media files in your Radarr/Sonarr libraries and deletes the corresponding qBittorrent data for these files. The qBittorrent search is category-based, so you must configure the appropriate categories in your `config.yml` file to match your Radarr/Sonarr download categories.

## Quick Setup

1. Mount the `/config` directory with your configuration file when running the container.
2. Mount your Radarr and Sonarr media library folders into the container, and update the `root_folder` paths in your `config.yml` to match these mount points.
3. Copy `config_sample/config.yml.sample` to your config directory as `config.yml`.
4. Edit the `config.yml` with your qBittorrent, Radarr, and Sonarr settings, including the correct category names and root folder paths.

**Example Docker run command:**

```bash
# Mount /config for configuration and your media folders for Radarr and Sonarr
# Adjust /path/to/movies and /path/to/tv to your actual media locations

docker run -d \
  --name=deletarr \
  -v /path/to/your/config:/config \
  -v /path/to/movies:/path/to/movies \
  -v /path/to/tv:/path/to/tv \
  --restart unless-stopped \
  deletarr
```

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