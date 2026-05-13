import qbittorrentapi
import requests
import logging
import time


class QbitClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.client = qbittorrentapi.Client(
            host=cfg['url'],
            username=cfg['username'],
            password=cfg['password']
        )

    def test_connection(self):
        try:
            version = self.client.app.version
            return {"status": "ok", "version": version}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_torrents(self, categories):
        # Filter completion on the server (status_filter='completed') so we don't rely on
        # float-equality against t.progress. Category is filtered in Python because
        # torrents_info() accepts a single category, not a list.
        torrents = self.client.torrents_info(status_filter='completed')
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
            if t.category in categories
        ]
        logging.info(f"Fetched {len(filtered)} torrents for categories {categories} (completed)")
        return filtered

    def delete_torrents(self, hashes, delete_data=True):
        """Delete torrents one at a time. Returns the list of hashes that were actually deleted
        (a transient failure on one hash must not be reported as success for all)."""
        deleted = []
        for h in hashes:
            try:
                self.client.torrents_delete(delete_files=delete_data, torrent_hashes=h)
                deleted.append(h)
                logging.info(f"Deleted torrent {h} (delete_data={delete_data})")
            except Exception as e:
                logging.error(f"Failed to delete torrent {h}: {e}")
            time.sleep(0.2)  # avoid hammering API
        return deleted


def radarr_test_connection(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/system/status"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {"status": "ok", "version": data.get('version')}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def sonarr_test_connection(cfg):
    url = f"{cfg['url'].rstrip('/')}/api/v3/system/status"
    headers = {"X-Api-Key": cfg['api_key']}
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {"status": "ok", "version": data.get('version')}
    except Exception as e:
        return {"status": "error", "message": str(e)}
