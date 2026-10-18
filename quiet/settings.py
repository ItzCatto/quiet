"""The settings Quiet DNS exposes, and how each one maps to the resolver iOS will use."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Public DNS resolvers that block ads, from each provider's own published pages. docs/resolvers.md lists the
# sources, what each filter blocks, and when they were last checked.
#   doh   DNS over HTTPS address.
#   dot   hostname for DNS over TLS (port 853), or None when the provider doesn't publish one.
#   ipv4, ipv6   bootstrap addresses, so the device can reach the resolver before DNS switches over.
#   name  the short name on screen; file  the name used in download file names.
#   blocks  what the filter blocks, in words used by the profile and the website. note  an extra line on the website.

RESOLVERS: dict[str, dict[str, Any]] = {
    # AdGuard DNS, from https://adguard-dns.io/en/public-dns.html
    "default": {
        "provider": "AdGuard DNS", "name": "Standard", "file": "Standard",
        "blocks": "blocks ads, trackers and phishing sites",
        "note": "Recommended for most people.",
        "doh": "https://dns.adguard-dns.com/dns-query", "dot": "dns.adguard-dns.com",
        "ipv4": ["94.140.14.14", "94.140.15.15"],
        "ipv6": ["2a10:50c0::ad1:ff", "2a10:50c0::ad2:ff"],
    },
    "family": {
        "provider": "AdGuard DNS", "name": "Family", "file": "Family",
        "blocks": "blocks ads, trackers, phishing sites and adult websites, and turns on safe search",
        "note": "",
        "doh": "https://family.adguard-dns.com/dns-query", "dot": "family.adguard-dns.com",
        "ipv4": ["94.140.14.15", "94.140.15.16"],
        "ipv6": ["2a10:50c0::bad1:ff", "2a10:50c0::bad2:ff"],
    },
    "unfiltered": {
        "provider": "AdGuard DNS", "name": "Unfiltered", "file": "Unfiltered",
        "blocks": "does not block ads or trackers",
        "note": "Lookups are still encrypted.",
        "doh": "https://unfiltered.adguard-dns.com/dns-query", "dot": "unfiltered.adguard-dns.com",
        "ipv4": ["94.140.14.140", "94.140.14.141"],
        "ipv6": ["2a10:50c0::1:ff", "2a10:50c0::2:ff"],
    },
}


@dataclass(frozen=True)
class Settings:
    """Every toggle the website and CLI expose. The defaults give the Standard profile.

    resolver, when set, is a key of RESOLVERS and decides what is blocked; block_ads and block_adult are then
    ignored. Without it, the two toggles choose one of the AdGuard DNS resolvers, as they always have.
    """

    enabled: bool = True        # False pauses Quiet DNS; the profile stays installed
    block_ads: bool = True      # block ads and trackers (AdGuard, when no resolver is named)
    block_adult: bool = False   # block adult sites and turn on safe search (AdGuard, when no resolver is named)
    use_tls: bool = False       # DNS over TLS (port 853) instead of DNS over HTTPS
    bootstrap_ips: bool = True  # include the resolver's IPs so it's reachable before DNS switches
    failover: bool = False      # if the resolver can't be reached, fall back to the network's DNS (iOS/macOS 26+)
    resolver: str | None = None  # a key of RESOLVERS: default, family or unfiltered

    def resolver_key(self) -> str:
        """Which resolver these settings use. Without a named resolver, adult blocking includes ad blocking."""
        if self.resolver is not None:
            if self.resolver not in RESOLVERS:
                raise ValueError(f"unknown resolver {self.resolver!r}")
            return self.resolver
        if self.block_adult:
            return "family"
        if self.block_ads:
            return "default"
        return "unfiltered"

    def endpoint(self) -> dict[str, Any]:
        return RESOLVERS[self.resolver_key()]
