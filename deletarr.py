import os
import sys
import logging
import yaml
import qbittorrentapi
import requests
import re
import time
from typing import List, Dict, Set

# Read version for testing
def get_version():
    try:
        with open('/app/version.txt', 'r') as f:
            return f.read().strip()
    except:
        return "unknown"

# --- Load configuration ---
def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# --- Logging setup ---
def setup_logging(log_config: dict):
    log_handlers = [logging.FileHandler(log_config.get('file'))]
    log_handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(
        handlers=log_handlers,
        level=getattr(logging, log_config.get('level', 'INFO').upper()),
        format='%(asctime)s [%(levelname)s] %(message)s',
    )

# --- API interaction implementations ---
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
                    'completion_on': getattr(t, 'completion_on', None)
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

# --- Radarr/Sonarr helpers ---
def radarr_get_movies(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/movie"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        movies = resp.json()
        # Use normalized folder paths for matching
        movie_paths = set(normalize_path(m['path']) for m in movies)
        logging.info(f"Fetched {len(movie_paths)} movies from Radarr")
        return movie_paths
    except Exception as e:
        logging.error(f"Failed to fetch movies from Radarr: {e}")
        return set()

def radarr_get_movie_files(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/moviefile"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        files = resp.json()
        # Map normalized folder path to set of file names
        movie_files = {}
        for f in files:
            folder = normalize_path(os.path.dirname(f['path']))
            name = os.path.basename(f['path'])
            if folder not in movie_files:
                movie_files[folder] = set()
            movie_files[folder].add(name)
        logging.info(f"Fetched {len(files)} movie files from Radarr")
        return movie_files
    except Exception as e:
        logging.error(f"Failed to fetch movie files from Radarr: {e}")
        return {}

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

def normalize_path(path):
    # Lowercase, remove trailing slashes, normalize separators
    return os.path.normpath(path).lower().rstrip('\\/')

def parse_torrent_path(torrent):
    # Use save_path for robust matching
    return normalize_path(torrent.get('save_path', ''))

def folder_has_media_files(folder_path):
    media_exts = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.ts', '.m4v', '.mpg', '.mpeg'}
    if not os.path.isdir(folder_path):
        return False
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if os.path.splitext(f)[1].lower() in media_exts:
                return True
    return False

def get_all_media_files(root_folder):
    """Recursively collect all media file names in the given root_folder."""
    media_exts = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.ts', '.m4v', '.mpg', '.mpeg'}
    media_files = set()
    for dirpath, _, files in os.walk(root_folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in media_exts:
                media_files.add(f)
    return media_files

def get_all_media_files_lower(root_folder):
    """Recursively collect all media file names (with extension, lowercased) in the given root_folder."""
    media_exts = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.ts', '.m4v', '.mpg', '.mpeg'}
    media_files = set()
    for dirpath, _, files in os.walk(root_folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in media_exts:
                media_files.add(f.lower())
    return media_files

def has_hardlinks_to_folder(file_path, target_folder):
    """Check if a file has hardlinks pointing to the target folder (e.g., Radarr/Sonarr media folder)."""
    try:
        if not os.path.exists(file_path):
            logging.debug(f"File does not exist: {file_path}")
            return False
            
        # Get file stats
        stat_info = os.stat(file_path)
        
        # If hardlink count is 1, there are no additional hardlinks
        if stat_info.st_nlink <= 1:
            logging.debug(f"No hardlinks found for: {file_path}")
            return False
            
        # Check if any hardlinks point to the target folder
        inode = stat_info.st_ino
        device = stat_info.st_dev
        
        # Walk through target folder looking for files with same inode
        for root, dirs, files in os.walk(target_folder):
            for file_name in files:
                target_file = os.path.join(root, file_name)
                try:
                    target_stat = os.stat(target_file)
                    if target_stat.st_ino == inode and target_stat.st_dev == device:
                        logging.debug(f"Hardlink found: {file_path} -> {target_file}")
                        return True
                except (OSError, IOError):
                    continue  # Skip files we can't access
                    
        logging.debug(f"Hardlinks exist but none point to target folder: {file_path}")
        return False
        
    except (OSError, IOError) as e:
        logging.warning(f"Error checking hardlinks for {file_path}: {e}")
        return False

def get_all_media_basenames(root_folder):
    """Recursively collect all media file basenames (without extension) in the given root_folder."""
    media_exts = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.ts', '.m4v', '.mpg', '.mpeg'}
    basenames = set()
    for dirpath, _, files in os.walk(root_folder):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in media_exts:
                name = os.path.splitext(f)[0].lower()
                basenames.add(name)
    return basenames

def normalize_torrent_name(name):
    # Remove extension, lowercase, strip common separators and extra info
    name = os.path.splitext(name)[0].lower()
    # Optionally, strip year or extra info in parentheses/brackets
    name = re.sub(r'[\(\[].*[\)\]]', '', name)
    name = re.sub(r'[^a-z0-9]+', ' ', name).strip()
    return name

def process_service(service_name, service_config, qbit, dry_run):
    root_folder = service_config['root_folder']
    category = service_config['category']
    logging.info(f"[{service_name}] Processing category '{category}' with hardlink detection to: {root_folder}")

    torrents = qbit.get_torrents([category])
    logging.debug(f"[{service_name}] Torrents in category '{category}':")
    for t in torrents:
        logging.debug(f"[{service_name}]   Name: {t['name']} | Save Path: {t['save_path']}")

    base_download_folder = service_config.get('base_download_folder')
    if not base_download_folder:
        # Try to infer from the first torrent if not set
        if torrents:
            base_download_folder = normalize_path(torrents[0]['save_path'])
        else:
            base_download_folder = ''

    def get_torrent_files(torrent_hash):
        try:
            files = qbit.client.torrents_files(torrent_hash)
            logging.debug(f"[{service_name}] Number of files for torrent {torrent_hash}: {len(files)}")
            return files
        except Exception as e:
            logging.warning(f"[{service_name}] Could not get files for torrent {torrent_hash}: {e}")
            return []

    # --- Wait for minimum seeding time after completion before deleting ---
    now = int(time.time())
    min_seed_days = service_config.get('min_seed_days', 30)  # Default 30 days
    min_age_sec = min_seed_days * 24 * 60 * 60  # Convert days to seconds
    logging.info(f"[{service_name}] Minimum seeding time: {min_seed_days} days ({min_age_sec} seconds)")
    
    torrents_to_delete = []
    torrents_to_delete_names = []
    for torrent in torrents:
        logging.debug(f"[{service_name}] Checking torrent: {torrent['name']} | Hash: {torrent['hash']} | Save Path: {torrent['save_path']}")
        # Check completion time - ensure minimum seeding period has passed
        completion_on = torrent.get('completion_on')
        if completion_on is not None:
            days_since_completion = (now - int(completion_on)) / (24 * 60 * 60)
            if now - int(completion_on) < min_age_sec:
                logging.info(f"[{service_name}] Torrent '{torrent['name']}' ({torrent['hash']}) has only been seeding for {days_since_completion:.1f} days (minimum: {min_seed_days} days). Skipping deletion.")
                continue
            else:
                logging.debug(f"[{service_name}] Torrent '{torrent['name']}' has been seeding for {days_since_completion:.1f} days - eligible for deletion check.")
        else:
            logging.warning(f"[{service_name}] Torrent '{torrent['name']}' ({torrent['hash']}) has no completion time. Skipping deletion for safety.")
            continue
        torrent_files = get_torrent_files(torrent['hash'])
        logging.debug(f"[{service_name}] Number of files for '{torrent['name']}': {len(torrent_files)}")
        if not torrent_files:
            logging.warning(f"[{service_name}] No file info for torrent '{torrent['name']}' ({torrent['hash']}). Skipping deletion check.")
            continue
            
        # Check if ANY torrent files have hardlinks to the service's root folder
        has_hardlinks = False
        for f in torrent_files:
            # Build full path to torrent file
            torrent_file_path = os.path.join(torrent['save_path'], f['name'])
            
            # Check if this file has hardlinks to the service root folder
            if has_hardlinks_to_folder(torrent_file_path, root_folder):
                logging.info(f"[{service_name}] File '{f['name']}' has hardlinks to {root_folder}. Torrent '{torrent['name']}' will NOT be deleted.")
                has_hardlinks = True
                break
            else:
                logging.debug(f"[{service_name}] File '{f['name']}' has no hardlinks to {root_folder}")
        
        if not has_hardlinks:
            torrents_to_delete.append(torrent['hash'])
            torrents_to_delete_names.append(torrent['name'])
            logging.info(f"[{service_name}] No hardlinks found for torrent '{torrent['name']}' ({torrent['hash']}). Marked for deletion.")
        else:
            logging.debug(f"[{service_name}] Torrent '{torrent['name']}' has hardlinks - keeping it.")

    # --- SAFETY CHECK: max_delete_percent ---
    max_delete_percent = service_config.get('max_delete_percent', None)
    if max_delete_percent is not None and torrents:
        percent_to_delete = (len(torrents_to_delete) / len(torrents)) * 100
        if percent_to_delete > max_delete_percent:
            logging.error(f"[{service_name}] ABORTING: {percent_to_delete:.1f}% of torrents would be deleted, which exceeds max_delete_percent={max_delete_percent}. No deletions performed.")
            return

    if torrents_to_delete:
        # Sort torrent names alphabetically for better readability
        sorted_torrent_names = sorted(torrents_to_delete_names)
        
        if dry_run:
            logging.info(f"[{service_name}] Dry run: would delete {len(torrents_to_delete)} torrents and their content:")
            for torrent_name in sorted_torrent_names:
                logging.info(f"[{service_name}]   - {torrent_name}")
        else:
            qbit.delete_torrents(torrents_to_delete, delete_data=True)
            logging.info(f"[{service_name}] Deleted {len(torrents_to_delete)} torrents and their content:")
            for torrent_name in sorted_torrent_names:
                logging.info(f"[{service_name}]   - {torrent_name}")
    else:
        logging.info(f"[{service_name}] No torrents to delete.")

# --- Main logic ---
def main():
    # Default to local debug path, override with env var or use production Docker path
    default_config = './config/config.yml'
    docker_config = '/config/config.yml'
    
    config_path = os.environ.get('DELETARR_CONFIG')
    if config_path is None:
        config_path = docker_config if os.path.exists(docker_config) else default_config
    
    config = load_config(config_path)
    setup_logging(config['logging'])
    version = get_version()
    logging.info(f'Deletarr version: {version}')
    logging.info(f'Script started using config: {config_path}')

    qbit = QbitClient(config['qBittorrent'])
    dry_run = config.get('dry_run', True)

    # Process both Radarr and Sonarr (if enabled)
    for service_name in ['Radarr', 'Sonarr']:
        if service_name in config:
            service_config = config[service_name]
            # Check if service is enabled (default: true for backward compatibility)
            if service_config.get('enabled', True):
                logging.info(f'{service_name} is enabled - processing...')
                process_service(service_name, service_config, qbit, dry_run)
            else:
                logging.info(f'{service_name} is disabled - skipping...')

if __name__ == "__main__":
    main()
