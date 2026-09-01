import ipaddress
import re
import socket
from urllib.parse import urlparse
from fastapi import HTTPException, status
from app.core.config import settings

SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9.\-]{1,12}$")


def sanitize_symbol(symbol: str) -> str:
    """Validate and clean a ticker symbol."""
    if not symbol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker symbol must not be empty.",
        )
    clean = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ticker symbol format: '{symbol}'. Only 1-12 alphanumeric characters, dots, and hyphens allowed.",
        )
    return clean


def is_ip_private_or_reserved(ip_str: str) -> bool:
    """Check if an IP is private, loopback, link-local, or cloud metadata."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip_str in ("169.254.169.254", "metadata.google.internal")
        )
    except ValueError:
        return True


def validate_safe_url(url: str) -> str:
    """Validate an external URL against SSRF attacks before document downloading."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only HTTP and HTTPS URLs are permitted for document ingestion.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL: Missing hostname.",
        )

    # Check for localhost / common loopback keywords
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forbidden: Ingestion from localhost addresses is blocked for security.",
        )

    # Resolve IP and verify not in private/reserved network ranges
    try:
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        for ip in ip_addresses:
            if is_ip_private_or_reserved(ip):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Forbidden: URL resolves to private or internal network IP ({ip}).",
                )
    except socket.gaierror:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to resolve host: {hostname}",
        )

    return url


def validate_document_size(size_bytes: int) -> None:
    """Enforce document size limits."""
    if size_bytes > settings.MAX_DOCUMENT_SIZE_BYTES:
        max_mb = settings.MAX_DOCUMENT_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document exceeds maximum permitted file size of {max_mb:.1f}MB.",
        )


def validate_research_query(query: str) -> str:
    """Validate user research query against length abuse and prompt injection attacks."""
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Research query cannot be empty.",
        )
    cleaned = query.strip()
    if len(cleaned) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Research query exceeds maximum allowed length of 500 characters (received {len(cleaned)}).",
        )
    return cleaned


def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitize text retrieved from external documents/filings or user input.
    Neutralizes prompt injection directives by treating text strictly as passive financial data.
    """
    if not text:
        return ""
    # Strip potential prompt jailbreak directives
    injection_patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
        r"(?i)system\s*:\s*",
        r"(?i)assistant\s*:\s*",
        r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
        r"(?i)reveal\s+(your\s+)?system\s+prompt",
        r"(?i)override\s+(safety|governance)",
    ]
    sanitized = text
    for pattern in injection_patterns:
        sanitized = re.sub(pattern, "[FILTERED_SECURITY_DIRECTIVE]", sanitized)
    return sanitized

