"""
PulseTrack — Shared Utilities
"""

import hashlib
import hmac
import base64
import ipaddress
import logging
import re
import socket
from typing import Optional, List
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def validate_cidr(cidr: str) -> bool:
    """Return True if the string is a valid IPv4 CIDR notation."""
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except ValueError:
        return False


def validate_port_list(ports) -> List[int]:
    """Validate and normalise a list of port numbers."""
    result = []
    for p in ports:
        p = int(p)
        if not (1 <= p <= 65535):
            raise ValueError(f"Port out of range: {p}")
        result.append(p)
    return sorted(set(result))


def resolve_hostname(hostname: str, timeout: float = 3.0) -> Optional[str]:
    """Resolve a hostname to its first IPv4 address, or None on failure."""
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(timeout)
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None
    finally:
        socket.setdefaulttimeout(old_timeout)


def sign_payload(payload: bytes, secret: str) -> str:
    """HMAC-SHA256 sign a payload. Returns hex digest."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_signature(payload: bytes, secret: str, signature: str) -> bool:
    """Constant-time HMAC verification."""
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)


def b64_encode(data: str) -> str:
    return base64.b64encode(data.encode()).decode()


def b64_decode(data: str) -> str:
    return base64.b64decode(data.encode()).decode()


def sanitize_filename(name: str) -> str:
    """Remove characters unsafe for file names."""
    return re.sub(r"[^\w\-.]", "_", name)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def format_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def chunk_list(lst: list, size: int):
    """Split a list into chunks of at most `size` elements."""
    for i in range(0, len(lst), size):
        yield lst[i : i + size]
