"""
PulseTrack — Scanner unit tests
"""

import pytest
from unittest.mock import patch, MagicMock
from src.scanner import Scanner, ScanTarget


@pytest.fixture
def basic_config():
    return {"scan_interval": 3600, "max_workers": 10}


@pytest.fixture
def sample_target():
    return ScanTarget(name="test_target", cidr="192.168.1.0/30", ports=[80, 443])


def test_expand_cidr_valid(basic_config):
    scanner = Scanner(basic_config)
    hosts = scanner._expand_cidr("10.0.0.0/30")
    assert len(hosts) == 2
    assert "10.0.0.1" in hosts
    assert "10.0.0.2" in hosts


def test_expand_cidr_single_host(basic_config):
    scanner = Scanner(basic_config)
    hosts = scanner._expand_cidr("10.0.0.1/32")
    assert hosts == ["10.0.0.1"]


def test_expand_cidr_invalid(basic_config):
    scanner = Scanner(basic_config)
    hosts = scanner._expand_cidr("not_a_cidr")
    assert hosts == []


def test_scan_port_closed(basic_config):
    scanner = Scanner(basic_config)
    # Port 1 is almost certainly closed
    result = scanner.scan_port("127.0.0.1", 1, timeout=0.5)
    assert result["status"] == "closed"
    assert result["host"] == "127.0.0.1"
    assert result["port"] == 1


def test_scan_port_open(basic_config):
    """Requires a local HTTP server on port 8765 — skip if not available."""
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 8765), timeout=0.5)
        s.close()
    except OSError:
        pytest.skip("No local server on port 8765")

    scanner = Scanner(basic_config)
    result = scanner.scan_port("127.0.0.1", 8765, timeout=1.0)
    assert result["status"] == "open"


def test_scanner_clear(basic_config, sample_target):
    scanner = Scanner(basic_config)
    scanner._results = [{"host": "x", "port": 80, "status": "open", "banner": None}]
    scanner.clear()
    assert scanner.get_results() == []
