import os
import logging
import time
from .utils import has_hardlinks_to_folder, HardlinkCheckError


def process_service(service_name, service_config, qbit):
    root_folder = service_config['root_folder']
    category = service_config['category']
    logging.info(f"[{service_name}] Processing category '{category}' with hardlink detection to: {root_folder}")

    # Fail loud and skip the service if the library folder isn't mounted/accessible.
    # Without this every torrent would look 'unhardlinked' and become a delete candidate.
    if not os.path.isdir(root_folder):
        logging.error(f"[{service_name}] root_folder '{root_folder}' does not exist or is not a directory. Skipping service.")
        return []

    torrents = qbit.get_torrents([category])

    now = int(time.time())
    min_seed_days = service_config.get('min_seed_days', 30)
    min_age_sec = min_seed_days * 24 * 60 * 60

    service_torrents_to_delete = []

    for torrent in torrents:
        name = torrent['name']
        completion_on = torrent.get('completion_on')
        if completion_on is None:
            logging.info(f"[{service_name}] SKIP '{name}' (no completion time)")
            continue
        seed_days = (now - int(completion_on)) / (24 * 60 * 60)
        if now - int(completion_on) < min_age_sec:
            logging.info(f"[{service_name}] SKIP '{name}' (seeding {seed_days:.1f}d < {min_seed_days}d min)")
            continue

        try:
            torrent_files = qbit.client.torrents_files(torrent['hash'])
        except Exception as e:
            logging.info(f"[{service_name}] SKIP '{name}' (file list unavailable: {e})")
            continue

        has_hardlinks = False
        for f in torrent_files:
            torrent_file_path = os.path.join(torrent['save_path'], f['name'])
            try:
                if has_hardlinks_to_folder(torrent_file_path, root_folder):
                    has_hardlinks = True
                    break
            except HardlinkCheckError as e:
                # Uncertainty must fail safe — keep the torrent rather than risk deleting a still-linked file.
                logging.warning(f"[{service_name}] KEEP '{name}' (hardlink check inconclusive: {e})")
                has_hardlinks = True
                break

        if has_hardlinks:
            logging.info(f"[{service_name}] KEEP '{name}' (hardlinked, {seed_days:.1f}d seeded)")
        else:
            service_torrents_to_delete.append(torrent)
            logging.info(f"[{service_name}] CANDIDATE '{name}' (no hardlinks, {seed_days:.1f}d seeded)")

    # --- SAFETY CHECK: max_delete_percent ---
    max_delete_percent = service_config.get('max_delete_percent', None)
    if max_delete_percent is not None and torrents:
        percent_to_delete = (len(service_torrents_to_delete) / len(torrents)) * 100
        if percent_to_delete > max_delete_percent:
            logging.error(
                f"[{service_name}] ABORT (would delete {len(service_torrents_to_delete)}/{len(torrents)} "
                f"= {percent_to_delete:.1f}% > max_delete_percent {max_delete_percent}%)"
            )
            return []
        logging.info(f"[{service_name}] {len(service_torrents_to_delete)}/{len(torrents)} candidates ({percent_to_delete:.1f}%)")

    return service_torrents_to_delete
