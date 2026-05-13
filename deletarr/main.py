import os
import logging
import sys
from .config import load_config, setup_logging, get_version, ConfigError
from .clients import QbitClient
from .processor import process_service

def print_summary(deletions_map, dry_run):
    print("\n" + "="*50)
    if dry_run:
        print("          DRY RUN - SUMMARY OF PENDING DELETIONS")
    else:
        print("                SUMMARY OF PERFORMED DELETIONS")
    print("="*50)
    
    total_deletions = 0
    for service, torrents in deletions_map.items():
        if not torrents:
            print(f"\n[{service}] No torrents to delete.")
            continue
        
        print(f"\n[{service}] {len(torrents)} torrents scheduled for deletion:")
        for t in sorted(torrents, key=lambda x: x['name']):
            print(f"  - {t['name']}")
        total_deletions += len(torrents)
    
    print("\n" + "="*50)
    if total_deletions == 0:
        print("Result: No torrents were identified for deletion.")
    else:
        status = "would be deleted" if dry_run else "have been deleted"
        print(f"Result: {total_deletions} torrents {status}.")
    print("="*50 + "\n")

def run_deletarr(config_path=None, dry_run=None):
    """
    Core function to run the process.
    dry_run override allowed for API manual runs.
    Returns the results dictionary.
    """
    if not config_path:
        config_path = os.environ.get('DELETARR_CONFIG')
        if not config_path:
            default_config = './config/config.yml'
            docker_config = '/config/config.yml'
            config_path = docker_config if os.path.exists(docker_config) else default_config

    try:
        # Load config each time to catch changes
        config = load_config(config_path)
        # If logging already setup, this might be redundant but harmless usually
        # For a long running app, we set up logging once at startup,
        # but here we might need to ensure we capture it.
        setup_logging(config['logging'])

        version = get_version()
        logging.info(f'Deletarr version: {version}')

        qbit = QbitClient(config['qBittorrent'])
        
        # Allow override, otherwise use config
        if dry_run is None:
            dry_run = config.get('dry_run', True)
        
        if dry_run:
            logging.info("Dry run is ENABLED. No actual deletions will be performed.")

        deletions_map = {}
        for service_name in ['Radarr', 'Sonarr']:
            if service_name in config:
                service_config = config[service_name]
                if service_config.get('enabled', True):
                    logging.info(f'[{service_name}] Started processing...')
                    torrents_to_delete = process_service(service_name, service_config, qbit)
                    deletions_map[service_name] = torrents_to_delete
                else:
                    logging.info(f'[{service_name}] Service is disabled. Skipping.')

        summary_parts = [f"{svc} {len(items)} candidate(s)" for svc, items in deletions_map.items()]
        logging.info("Run summary: " + (", ".join(summary_parts) if summary_parts else "no services processed"))

        # Perform actual deletions if not dry run
        deleted_hashes = []
        if not dry_run:
            all_hashes = []
            for torrents in deletions_map.values():
                all_hashes.extend([t['hash'] for t in torrents])

            if all_hashes:
                logging.info(f"Performing actual deletion of {len(all_hashes)} torrents...")
                deleted_hashes = qbit.delete_torrents(all_hashes, delete_data=True)
                failed = len(all_hashes) - len(deleted_hashes)
                if failed:
                    logging.warning(f"Deletions completed: {len(deleted_hashes)} succeeded, {failed} failed.")
                else:
                    logging.info(f"Deletions completed: {len(deleted_hashes)} succeeded.")
            else:
                logging.info("No deletions to perform.")

        return {
            "success": True,
            "summary": deletions_map,
            "dry_run": dry_run,
            "deleted_count": len(deleted_hashes) if not dry_run else 0
        }
    except ConfigError as e:
        # Config not yet loaded so logging may not be configured — print plus best-effort log.
        print(f"Deletarr: {e}")
        logging.error(str(e))
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        # Some libraries (e.g. qbittorrent-api's LoginFailed) raise with an empty message.
        # Fall back to the class name so the user gets *something* actionable.
        error_msg = str(e) or type(e).__name__
        logging.error(f"Run failed: {error_msg}")
        logging.debug("Traceback:", exc_info=True)
        return {
            "success": False,
            "error": error_msg
        }

def main():
    # CLI entry point
    results = run_deletarr()
    if not results.get('success'):
        print(f"Deletarr run failed: {results.get('error', 'unknown error')}")
        sys.exit(1)
    print_summary(results['summary'], results['dry_run'])

if __name__ == "__main__":
    main()
