import requests
import threading
import time
import logging
from typing import Set

logger = logging.getLogger("Sentinel.TorIntel")

#!
#! Manages active Tor Exit Node IP addresses
#! 
class TorInfo:
    TOR_BULK_EXIT_URL = "https://check.torproject.org/torbulkexitlist"

    def __init__(self, refresh_interval_hours: int = 6):
        self.exit_nodes: Set[str] = set()
        self.refresh_interval = refresh_interval_hours * 3600
        self._is_running = False

        #! for testing/offline fallback
        self.exit_nodes.update([
            "185.220.101.5",
            "185.220.102.8",
            "51.15.43.205"
        ])
        self.refresh_exit_nodes()

    #! fetch the latest active Tor Exit Node IPs
    def refresh_exit_nodes(self):
        try:
            response = requests.get(self.TOR_BULK_EXIT_URL, timeout=10)

            if response.status_code == 200:
                lines = response.text.strip().splitlines()

                #! Clean up and filter IP strings
                fresh_ips = {line.strip() for line in lines if line and not line.startswith("#")}

                if fresh_ips:
                    self.exit_nodes = fresh_ips
                    logger.info(f"[TorIntel] Successfully loaded {len(self.exit_nodes)} Tor Exit Nodes")

            else:
                logger.warning(f"[TorIntel] Failed to fetch exit list (HTTP {response.status_code}). Using cached IPs")

        except Exception as e:
            logger.error(f"[TorIntel] Error connecting to Tor directory: {e}. Fallback to local cache")

    #! True = active Tor Exit Node
    def is_tor_exit(self, ip: str) -> bool:
        return ip in self.exit_nodes

    def start_background_updater(self):
        #! background daemon that re-fetches the list
        
        if self._is_running: return

        self._is_running = True

        def _worker():
            while self._is_running:
                time.sleep(self.refresh_interval)
                self.refresh_exit_nodes()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()