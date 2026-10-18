import ipaddress
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

from quiet.settings import RESOLVERS, Settings

ROOT = Path(__file__).resolve().parent.parent


class SettingsTests(unittest.TestCase):
    def test_defaults_give_the_standard_resolver(self):
        self.assertEqual(Settings().resolver_key(), "default")

    def test_adult_blocking_uses_family_resolver_and_keeps_ad_blocking(self):
        s = Settings(block_ads=False, block_adult=True)
        self.assertEqual(s.resolver_key(), "family")

    def test_turning_off_ad_blocking_gives_unfiltered(self):
        self.assertEqual(Settings(block_ads=False).resolver_key(), "unfiltered")

    def test_a_named_resolver_decides_the_filter_and_ignores_the_two_toggles(self):
        s = Settings(resolver="unfiltered", block_ads=False, block_adult=True)
        self.assertEqual(s.resolver_key(), "unfiltered")

    def test_an_unknown_resolver_is_refused(self):
        with self.assertRaises(ValueError):
            Settings(resolver="not-a-resolver").resolver_key()

    def test_every_resolver_has_a_provider_name_and_a_description(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                for field in ("provider", "name", "file", "blocks"):
                    self.assertTrue(r[field].strip(), field)
                self.assertIsInstance(r["note"], str)

    def test_every_resolver_has_valid_bootstrap_addresses(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                self.assertEqual(len(r["ipv4"]), 2)
                self.assertIn(len(r["ipv6"]), (0, 2))
                for address in r["ipv4"]:
                    ipaddress.IPv4Address(address)
                for address in r["ipv6"]:
                    ipaddress.IPv6Address(address)

    def test_every_address_belongs_to_one_resolver_only(self):
        addresses = [a for r in RESOLVERS.values() for a in r["ipv4"] + r["ipv6"]]
        self.assertEqual(len(addresses), len(set(addresses)))

    def test_every_resolver_uses_https_and_a_dns_over_tls_hostname_matches_it(self):
        for key, r in RESOLVERS.items():
            with self.subTest(resolver=key):
                self.assertTrue(r["doh"].startswith("https://"))
                if r["dot"] is not None:
                    self.assertEqual(urlparse(r["doh"]).hostname, r["dot"])

    def test_dns_over_tls_hostnames_are_unique(self):
        hostnames = [r["dot"] for r in RESOLVERS.values() if r["dot"] is not None]
        self.assertEqual(len(hostnames), len(set(hostnames)))

    def test_https_addresses_are_unique(self):
        urls = [r["doh"] for r in RESOLVERS.values()]
        self.assertEqual(len(urls), len(set(urls)))

    def test_the_website_offers_every_resolver_and_no_other(self):
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        offered = re.findall(r'<input type="radio" name="resolver" value="([^"]+)"', html)
        self.assertEqual(sorted(offered), sorted(RESOLVERS))


if __name__ == "__main__":
    unittest.main()
