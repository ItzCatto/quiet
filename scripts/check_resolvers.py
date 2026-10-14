"""Checks that AdGuard DNS still answers at the addresses the Quiet DNS profiles use.

Run from the project folder:  python3 scripts/check_resolvers.py

For each filter it asks the DNS-over-HTTPS address and the DNS-over-TLS name for the address of example.com,
and it tries a connection to each IP address the profiles include. The only name it looks up is example.com.
It exits with 1 if a required check fails. IPv6 failures are reported but don't fail the run, because not
every network has IPv6.
"""

from __future__ import annotations

import base64
import socket
import ssl
import struct
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quiet.settings import RESOLVERS  # noqa: E402

TIMEOUT = 10
TEST_NAME = "example.com"


def query(name: str) -> bytes:
    """A DNS query for the IPv4 address of a name, in wire format."""
    header = struct.pack(">HHHHHH", 0, 0x0100, 1, 0, 0, 0)  # ID 0, recursion desired, one question
    labels = b"".join(bytes([len(part)]) + part.encode("ascii") for part in name.split("."))
    return header + labels + b"\x00" + struct.pack(">HH", 1, 1)  # type A, class IN


def check_reply(data: bytes) -> str | None:
    """None when the reply is a successful answer, otherwise the reason it isn't."""
    if len(data) < 12:
        return "reply too short"
    flags, _questions, answers = struct.unpack(">HHH", data[2:8])
    if not flags & 0x8000:
        return "not a reply"
    rcode = flags & 0x000F
    if rcode != 0:
        return f"error code {rcode}"
    if answers < 1:
        return "no answer"
    return None


def recv_exact(sock: ssl.SSLSocket, count: int) -> bytes:
    data = b""
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise OSError("connection closed early")
        data += chunk
    return data


def check_https(url: str) -> str | None:
    encoded = base64.urlsafe_b64encode(query(TEST_NAME)).rstrip(b"=").decode("ascii")
    request = urllib.request.Request(f"{url}?dns={encoded}", headers={"Accept": "application/dns-message"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return f"HTTP {response.status}"
            body = response.read()
    except (OSError, ValueError) as exc:
        return str(exc)
    return check_reply(body)


def check_tls(host: str) -> str | None:
    payload = query(TEST_NAME)
    try:
        with socket.create_connection((host, 853), timeout=TIMEOUT) as raw:
            with ssl.create_default_context().wrap_socket(raw, server_hostname=host) as tls:
                tls.sendall(struct.pack(">H", len(payload)) + payload)
                size = struct.unpack(">H", recv_exact(tls, 2))[0]
                body = recv_exact(tls, size)
    except (OSError, ValueError) as exc:
        return str(exc)
    return check_reply(body)


def check_address(ip: str, port: int = 443) -> str | None:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    try:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            sock.connect((ip, port))
    except OSError as exc:
        return str(exc)
    return None


def report(label: str, problem: str | None, required: bool = True) -> tuple[int, int]:
    """Prints one result. Returns (failures, warnings) for this result."""
    if problem is None:
        print(f"ok    {label}")
        return 0, 0
    print(f"{'FAIL' if required else 'warn'}  {label}: {problem}")
    return (1, 0) if required else (0, 1)


def main() -> int:
    failures = warnings = 0
    for name, resolver in RESOLVERS.items():
        print(name)
        for result in (
            report(f"  HTTPS  {resolver['doh']}", check_https(resolver["doh"])),
            report(f"  TLS    {resolver['dot']}:853", check_tls(resolver["dot"])),
        ):
            failures, warnings = failures + result[0], warnings + result[1]
        for ip in resolver["ipv4"]:
            result = report(f"  IPv4   {ip}:443", check_address(ip))
            failures, warnings = failures + result[0], warnings + result[1]
        for ip in resolver["ipv6"]:
            result = report(f"  IPv6   {ip}:443", check_address(ip), required=False)
            failures, warnings = failures + result[0], warnings + result[1]
    print(f"\n{failures} failed, {warnings} warnings")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
