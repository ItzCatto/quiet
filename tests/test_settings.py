import ipaddress
import unittest
from urllib.parse import urlparse

from quiet.settings import RESOLVERS, Settings


class SettingsTests(unittest.TestCase):
    def test_defaults_give_the_standard_resolver(self):
        self.assertEqual(Settings().resolver_key(), "default")

    def test_adult_blocking_uses_family_resolver_and_keeps_ad_blocking(self):
        s = Settings(block_ads=False, block_adult=True)
        self.assertEqual(s.resolver_key(), "family")

    def test_turning_off_ad_blocking_gives_unfiltered(self):
        self.assertEqual(Settings(block_ads=False).resolver_key(), "unfiltered")

    def test_resolvers_have_two_addresses_per_family(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                self.assertEqual(len(r["ipv4"]), 2)
                self.assertEqual(len(r["ipv6"]), 2)

    def test_resolver_addresses_are_valid(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                for address in r["ipv4"]:
                    ipaddress.IPv4Address(address)
                for address in r["ipv6"]:
                    ipaddress.IPv6Address(address)

    def test_hostnames_match_their_urls(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                self.assertEqual(urlparse(r["doh"]).hostname, r["dot"])

    def test_each_resolver_has_its_own_hostname(self):
        hostnames = [r["dot"] for r in RESOLVERS.values()]
        self.assertEqual(len(hostnames), len(set(hostnames)))


if __name__ == "__main__":
    unittest.main()
