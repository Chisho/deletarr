import os
import logging


class HardlinkCheckError(Exception):
    """Raised when the hardlink check cannot reach a definitive answer.
    Callers must treat this as 'unknown' and keep the torrent."""


def has_hardlinks_to_folder(file_path, target_folder):
    """Check if a file has hardlinks pointing to the target folder (e.g., Radarr/Sonarr media folder).

    Returns True if a hardlink is found, False if the source has no hardlinks at all.
    Raises HardlinkCheckError if the check cannot complete (missing target folder, unstat-able
    source, etc.) — callers MUST treat that as 'do not delete this torrent'.
    """
    # Target folder must exist and be a directory. Otherwise os.walk yields nothing
    # and the function would falsely report 'no hardlinks' for every torrent.
    if not os.path.isdir(target_folder):
        raise HardlinkCheckError(f"Target folder does not exist or is not a directory: {target_folder}")

    try:
        stat_info = os.stat(file_path)
    except (OSError, IOError) as e:
        raise HardlinkCheckError(f"Cannot stat source file {file_path}: {e}") from e

    # st_nlink == 1 means no hardlinks exist anywhere on this filesystem.
    if stat_info.st_nlink <= 1:
        return False

    inode = stat_info.st_ino
    device = stat_info.st_dev

    try:
        for root, dirs, files in os.walk(target_folder):
            for file_name in files:
                target_file = os.path.join(root, file_name)
                try:
                    target_stat = os.stat(target_file)
                except (OSError, IOError):
                    continue  # individual unreadable files are tolerable during the inode scan
                if target_stat.st_ino == inode and target_stat.st_dev == device:
                    logging.debug(f"Hardlink found: {file_path} -> {target_file}")
                    return True
    except (OSError, IOError) as e:
        raise HardlinkCheckError(f"Error walking target folder {target_folder}: {e}") from e

    return False
