"""
PulseTrack — Monitor
Continuous monitoring loop with configurable heartbeat and alert dispatch.
"""

import time
import logging
import signal
import threading
from typing import Callable, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MonitorEvent:
    def __init__(self, event_type: str, source: str, severity: str, detail: dict):
        self.event_type = event_type
        self.source = source
        self.severity = severity  # low / medium / high / critical
        self.detail = detail
        self.timestamp = datetime.utcnow().isoformat()

    def __repr__(self):
        return f"<MonitorEvent {self.event_type} [{self.severity}] from {self.source}>"


class Monitor:
    """
    Continuous monitoring loop. Calls registered scan functions on a fixed interval,
    evaluates alert rules and dispatches notifications via configured backends.

    Usage:
        monitor = Monitor(config)
        monitor.register_scanner(my_scanner_fn)
        monitor.register_alert_handler(slack_handler)
        monitor.start()  # blocks until SIGINT/SIGTERM
    """

    def __init__(self, config: dict):
        self.config = config
        self.interval = config.get("scan_interval", 3600)
        self.heartbeat = config.get("heartbeat_interval", 60)
        self._scanners: List[Callable] = []
        self._alert_handlers: List[Callable] = []
        self._running = False
        self._lock = threading.Lock()
        self._last_scan: Optional[datetime] = None

    def register_scanner(self, fn: Callable):
        """Register a scan function to be called each cycle."""
        self._scanners.append(fn)
        logger.debug(f"Scanner registered: {fn.__name__}")

    def register_alert_handler(self, fn: Callable):
        """Register an alert dispatch function."""
        self._alert_handlers.append(fn)
        logger.debug(f"Alert handler registered: {fn.__name__}")

    def start(self):
        """Start the monitoring loop. Blocks until stopped."""
        self._running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        logger.info(f"Monitor started — scan interval: {self.interval}s, heartbeat: {self.heartbeat}s")

        while self._running:
            cycle_start = time.time()
            self._run_cycle()
            elapsed = time.time() - cycle_start
            sleep_time = max(0, self.interval - elapsed)
            logger.debug(f"Cycle complete in {elapsed:.1f}s — sleeping {sleep_time:.0f}s")
            self._sleep_interruptible(sleep_time)

        logger.info("Monitor stopped.")

    def stop(self):
        """Stop the monitoring loop gracefully."""
        self._running = False

    def _run_cycle(self):
        """Execute all registered scanners and evaluate alert rules."""
        with self._lock:
            self._last_scan = datetime.utcnow()
            events = []

            for scanner_fn in self._scanners:
                try:
                    result = scanner_fn()
                    if result:
                        events.extend(result if isinstance(result, list) else [result])
                except Exception as e:
                    logger.error(f"Scanner {scanner_fn.__name__} failed: {e}")

            for event in events:
                self._dispatch_alert(event)

    def _dispatch_alert(self, event: MonitorEvent):
        for handler in self._alert_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"Alert handler {handler.__name__} failed: {e}")

    def _sleep_interruptible(self, seconds: float):
        """Sleep in small increments so SIGINT is handled promptly."""
        end = time.time() + seconds
        while self._running and time.time() < end:
            time.sleep(min(1.0, end - time.time()))

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum} — stopping monitor")
        self._running = False
