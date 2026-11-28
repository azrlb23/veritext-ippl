from __future__ import annotations

import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

_BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".home", ".arpa")


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or not ip.is_global
    )


def is_safe_public_url(url: str) -> bool:
    """Return True only when url uses http(s) and resolves exclusively to public IPs."""
    if not isinstance(url, str) or not url.strip():
        return False
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False
    scheme = (parsed.scheme or "").lower()
    hostname = (parsed.hostname or "").strip().rstrip(".").lower()
    if scheme not in ("http", "https") or not hostname:
        return False
    if hostname == "localhost" or hostname.endswith(_BLOCKED_SUFFIXES):
        return False
    try:
        ipaddress.ip_address(hostname)
        return _is_public_ip(hostname)
    except ValueError:
        pass
    port = parsed.port or (443 if scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except (OSError, ValueError):
        return False
    if not infos:
        return False
    for info in infos:
        sockaddr = info[4]
        if not sockaddr or not _is_public_ip(str(sockaddr[0])):
            return False
    return True


def _collect_urls(entry: Any, urls: set[str]) -> None:
    if not isinstance(entry, dict):
        return
    for key in ("source_url", "url"):
        val = entry.get(key)
        if isinstance(val, str) and val.strip():
            urls.add(val.strip())


def extract_report_allowed_urls(report: Any) -> set[str]:
    """Collect allowlisted public source URLs referenced by an audit report."""
    urls: set[str] = set()
    for src in getattr(report, "matched_sources", None) or []:
        _collect_urls(src, urls)
    for ann in getattr(report, "heatmap_annotations", None) or []:
        _collect_urls(ann, urls)
        if isinstance(ann, dict):
            for sec in ann.get("secondary_sources") or []:
                _collect_urls(sec, urls)
    return urls
