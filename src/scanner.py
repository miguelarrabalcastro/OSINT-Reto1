"""
PulseTrack — Scanner Engine
Core network scanning and fingerprinting module.
"""

import socket
import logging
import concurrent.futures
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ScanTarget:
    def __init__(self, name: str, cidr: str, ports: List[int], timeout: int = 45):
        self.name = name
        self.cidr = cidr
        self.ports = ports
        self.timeout = timeout
        self.scan_time: Optional[datetime] = None
        self.results: List[Dict] = []

    def __repr__(self):
        return f"<ScanTarget name={self.name!r} cidr={self.cidr!r}>"


class Scanner:
    """
    Main scanner engine. Supports parallel port scanning with configurable
    worker count and timeout. Results are stored per-target for report generation.
    """

    def __init__(self, config: dict, max_workers: int = 50):
        self.config = config
        self.max_workers = max_workers
        self._results: List[Dict] = []

    def scan_port(self, host: str, port: int, timeout: float) -> Dict:
        """Attempt a TCP connection to determine if a port is open."""
        result = {"host": host, "port": port, "status": "closed", "banner": None}
        try:
            with socket.create_connection((host, port), timeout=timeout) as sock:
                result["status"] = "open"
                try:
                    sock.sendall(b"\r\n")
                    banner = sock.recv(1024).decode("utf-8", errors="replace").strip()
                    result["banner"] = banner[:200] if banner else None
                except Exception:
                    pass
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
        return result

    def scan_target(self, target: ScanTarget) -> List[Dict]:
        """Run a full port scan against all ports defined for a target."""
        logger.info(f"Starting scan: {target.name} ({target.cidr})")
        target.scan_time = datetime.utcnow()
        results = []

        hosts = self._expand_cidr(target.cidr)
        tasks = [(h, p) for h in hosts for p in target.ports]

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.scan_port, h, p, target.timeout): (h, p)
                for h, p in tasks
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result["status"] == "open":
                        results.append(result)
                        logger.debug(f"Open: {result['host']}:{result['port']}")
                except Exception as exc:
                    h, p = futures[future]
                    logger.warning(f"Scan failed for {h}:{p} — {exc}")

        target.results = results
        self._results.extend(results)
        logger.info(f"Scan complete: {target.name} — {len(results)} open ports found")
        return results

    def _expand_cidr(self, cidr: str) -> List[str]:
        """Expand a CIDR notation to a list of IP addresses."""
        import ipaddress
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError as e:
            logger.error(f"Invalid CIDR {cidr!r}: {e}")
            return []

    def get_results(self) -> List[Dict]:
        return self._results

    def clear(self):
        self._results = []
