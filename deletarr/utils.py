import os
import logging

def normalize_path(path):
    # Lowercase, remove trailing slashes, normalize separators
    return os.path.normpath(path).lower().rstrip('\\/')

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
