import os
import logging
import time
from .utils import has_hardlinks_to_folder

def process_service(service_name, service_config, qbit):
    root_folder = service_config['root_folder']
    category = service_config['category']
    logging.info(f"[{service_name}] Processing category '{category}' with hardlink detection to: {root_folder}")

    torrents = qbit.get_torrents([category])
    
    # --- Wait for minimum seeding time after completion before deleting ---
    now = int(time.time())
    min_seed_days = service_config.get('min_seed_days', 30)
    min_age_sec = min_seed_days * 24 * 60 * 60
    
    service_torrents_to_delete = []
    
    for torrent in torrents:
        completion_on = torrent.get('completion_on')
        if completion_on is not None:
            if now - int(completion_on) < min_age_sec:
                days_since_completion = (now - int(completion_on)) / (24 * 60 * 60)
                logging.debug(f"[{service_name}] Torrent '{torrent['name']}' has only been seeding for {days_since_completion:.1f} days. Skipping.")
                continue
        else:
            logging.warning(f"[{service_name}] Torrent '{torrent['name']}' has no completion time. Skipping.")
            continue

        try:
            torrent_files = qbit.client.torrents_files(torrent['hash'])
        except Exception as e:
            logging.warning(f"[{service_name}] Could not get files for torrent '{torrent['name']}': {e}")
            continue

        has_hardlinks = False
        for f in torrent_files:
            torrent_file_path = os.path.join(torrent['save_path'], f['name'])
            if has_hardlinks_to_folder(torrent_file_path, root_folder):
                logging.debug(f"[{service_name}] File '{f['name']}' has hardlinks to {root_folder}.")
                has_hardlinks = True
                break
        
        if not has_hardlinks:
            service_torrents_to_delete.append(torrent)
            logging.debug(f"[{service_name}] No hardlinks found for '{torrent['name']}'. Marked for deletion.")

    # --- SAFETY CHECK: max_delete_percent ---
    max_delete_percent = service_config.get('max_delete_percent', None)
    if max_delete_percent is not None and torrents:
        percent_to_delete = (len(service_torrents_to_delete) / len(torrents)) * 100
        if percent_to_delete > max_delete_percent:
            logging.error(f"[{service_name}] ABORTING: {percent_to_delete:.1f}% of torrents would be deleted (max: {max_delete_percent}%).")
            return []

    return service_torrents_to_delete
