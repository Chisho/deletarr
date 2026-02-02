import yaml
import logging
import sys
import os

def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config at {config_path}: {e}")
        sys.exit(1)

def setup_logging(log_config: dict):
    log_handlers = []
    if log_config.get('file'):
        log_handlers.append(logging.FileHandler(log_config.get('file')))
    log_handlers.append(logging.StreamHandler(sys.stdout))
    
    logging.basicConfig(
        handlers=log_handlers,
        level=getattr(logging, log_config.get('level', 'INFO').upper()),
        format='%(asctime)s [%(levelname)s] %(message)s',
    )

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
