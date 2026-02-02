import os
import logging
import sys
from .config import load_config, setup_logging, get_version
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

def main():
    config_path = os.environ.get('DELETARR_CONFIG')
    if not config_path:
        default_config = './config/config.yml'
        docker_config = '/config/config.yml'
        config_path = docker_config if os.path.exists(docker_config) else default_config
    
    config = load_config(config_path)
    setup_logging(config['logging'])
    
    version = get_version()
    logging.info(f'Deletarr version: {version}')
    logging.info(f'Script started using config: {config_path}')

    qbit = QbitClient(config['qBittorrent'])
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

    # Print clear summary at the end
    print_summary(deletions_map, dry_run)

    # Perform actual deletions if not dry run
    if not dry_run:
        all_hashes = []
        for torrents in deletions_map.values():
            all_hashes.extend([t['hash'] for t in torrents])
        
        if all_hashes:
            logging.info(f"Performing actual deletion of {len(all_hashes)} torrents...")
            qbit.delete_torrents(all_hashes, delete_data=True)
            logging.info("Deletions completed.")
        else:
            logging.info("No deletions to perform.")

if __name__ == "__main__":
    main()
