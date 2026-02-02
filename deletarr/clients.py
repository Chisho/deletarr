import qbittorrentapi
import requests
import logging
import sys
import time
from .utils import normalize_path

class QbitClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = qbittorrentapi.Client(
            host=cfg['url'],
            username=cfg['username'],
            password=cfg['password']
        )
        try:
            self.client.auth_log_in()
            logging.info("Logged in to qBittorrent")
        except Exception as e:
            logging.error(f"Failed to login to qBittorrent: {e}")
            sys.exit(1)

    def get_torrents(self, categories):
        try:
            torrents = self.client.torrents_info()
            filtered = [
                {
                    'hash': t.hash,
                    'name': t.name,
                    'category': t.category,
                    'save_path': t.save_path,
                    'completion_on': getattr(t, 'completion_on', None),
                    'progress': getattr(t, 'progress', 0)
                }
                for t in torrents
                if t.category in categories and getattr(t, 'progress', 0) == 1.0
            ]
            logging.info(f"Fetched {len(filtered)} torrents for categories {categories} (fully downloaded)")
            return filtered
        except Exception as e:
            logging.error(f"Failed to fetch torrents: {e}")
            return []

    def delete_torrents(self, hashes, delete_data=True):
        try:
            for h in hashes:
                self.client.torrents_delete(delete_files=delete_data, torrent_hashes=h)
                logging.info(f"Deleted torrent {h} (delete_data={delete_data})")
                time.sleep(0.2)  # avoid hammering API
        except Exception as e:
            logging.error(f"Failed to delete torrents: {e}")

def radarr_get_movies(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/movie"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        movies = resp.json()
        movie_paths = set(normalize_path(m['path']) for m in movies)
        logging.info(f"Fetched {len(movie_paths)} movies from Radarr")
        return movie_paths
    except Exception as e:
        logging.error(f"Failed to fetch movies from Radarr: {e}")
        return set()

def sonarr_get_series(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/series"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        series = resp.json()
        series_paths = set(normalize_path(s['path']) for s in series)
        logging.info(f"Fetched {len(series_paths)} series from Sonarr")
        return series_paths
    except Exception as e:
        logging.error(f"Failed to fetch series from Sonarr: {e}")
        return set()
