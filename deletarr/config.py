import yaml
import logging
import sys
import os


class ConfigError(Exception):
    """Raised when config can't be loaded or parsed.
    Caller decides how to surface this (CLI prints + exits, API returns 500)."""


def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise ConfigError(f"Error loading config at {config_path}: {e}") from e

def setup_logging(log_config: dict):
    level_str = log_config.get('level', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # If we want to ensure our handlers are there, we can add them
    # But basicConfig is safer if we just want to set format/level for simple scripts
    # For our API, we want to make sure the root level is set
    
    # Only add handlers if none exist or to the root
    if not root_logger.handlers:
        log_handlers = []
        if log_config.get('file'):
            log_handlers.append(logging.FileHandler(log_config.get('file')))
        log_handlers.append(logging.StreamHandler(sys.stdout))
        
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        for handler in log_handlers:
            handler.setFormatter(formatter)
            root_logger.addHandler(handler)
    else:
        # Just update the level if handlers already exist (like in API mode)
        root_logger.setLevel(level)
        # Also ensure existing handlers (like the capture_handler) have the right level
        for handler in root_logger.handlers:
            handler.setLevel(level)


def get_version():
    try:
        # Check standard location and then fallback to local for development
        paths = ['/app/version.txt', 'version.txt']
        for p in paths:
            if os.path.exists(p):
                with open(p, 'r') as f:
                    return f.read().strip()
        return "unknown"
    except:
        return "unknown"
