"""Quiet DNS: builds iPhone and Mac profiles that turn on encrypted, filtered DNS.

Modules:
    settings   - the resolvers and filters, and how the toggles map to them
    profiles   - builds, checks and serializes the .mobileconfig files
    signing    - optional signing with your own certificate (openssl)
    wireguard  - points a WireGuard config's DNS at a resolver, on your computer
"""

__version__ = "2.4.0"
