"""Rate-limit keying.

All browser traffic reaches the API through the Next.js proxy, so keying on the
socket peer would bucket every user under one IP (a single failed login would
lock out the whole site). The proxy forwards the real client IP in
X-Forwarded-For; we key on that when present, falling back to the peer address.
"""
from slowapi.util import get_remote_address
from starlette.requests import Request


def client_ip_key(request: Request) -> str:
    """Return the originating client IP, honoring a trusted X-Forwarded-For."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # First hop is the original client; the proxy appends downstream hops.
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)
