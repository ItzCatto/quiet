import itertools
import plistlib
import unittest
import uuid

from quiet import profiles
from quiet.__main__ import PRESETS
from quiet.settings import RESOLVERS, Settings

VERSION = 1700000000


def every_combination():
    for values in itertools.product([True, False], repeat=6):
        yield Settings(*values)


def build(s: Settings) -> dict:
    return profiles.build_profile(s, VERSION)


def dns_of(s: Settings) -> dict:
    return build(s)["PayloadContent"][0]["DNSSettings"]


class ProfileTests(unittest.TestCase):
    def test_presets_pass_every_check(self):
        for name, s in PRESETS:
            with self.subTest(preset=name):
                self.assertEqual(profiles.check_profile(build(s)), [])

    def test_every_combination_passes_every_check(self):
        for s in every_combination():
            with self.subTest(settings=s):
                self.assertEqual(profiles.check_profile(build(s)), [])

    def test_all_profiles_share_one_slot(self):
        slots = {(build(s)["PayloadIdentifier"], build(s)["PayloadUUID"]) for _, s in PRESETS}
        self.assertEqual(slots, {(profiles.PROFILE_ID, profiles.PROFILE_UUID)})

    def test_slot_uuids_are_valid(self):
        uuid.UUID(profiles.PROFILE_UUID)
        uuid.UUID(profiles.DNS_UUID)

    def test_paused_profile_keeps_the_dns_settings_and_disconnects_them(self):
        payload = build(Settings(enabled=False))["PayloadContent"][0]
        self.assertEqual(payload["OnDemandRules"], [{"Action": "Disconnect"}])
        self.assertIn("DNSSettings", payload)

    def test_active_profile_has_no_pause_rule(self):
        self.assertNotIn("OnDemandRules", build(Settings())["PayloadContent"][0])

    def test_every_setting_keeps_one_display_name_and_identity(self):
        for s in every_combination():
            with self.subTest(settings=s):
                data = build(s)
                self.assertEqual(data["PayloadDisplayName"], profiles.DISPLAY_NAME)
                self.assertEqual(data["PayloadIdentifier"], profiles.PROFILE_ID)
                self.assertEqual(data["PayloadContent"][0]["PayloadIdentifier"], profiles.DNS_ID)

    def test_checker_catches_a_changed_pause_rule(self):
        data = build(Settings(enabled=False))
        data["PayloadContent"][0]["OnDemandRules"] = [{"Action": "Connect"}]
        self.assertTrue(any("OnDemandRules" in p for p in profiles.check_profile(data)))

    def test_standard_profile_uses_the_default_resolver(self):
        dns = dns_of(Settings())
        self.assertEqual(dns["DNSProtocol"], "HTTPS")
        self.assertEqual(dns["ServerURL"], RESOLVERS["default"]["doh"])
        self.assertNotIn("AllowFailover", dns)

    def test_family_setting_switches_resolver(self):
        dns = dns_of(Settings(block_ads=False, block_adult=True))
        self.assertEqual(dns["ServerURL"], RESOLVERS["family"]["doh"])

    def test_unfiltered_setting_switches_resolver(self):
        dns = dns_of(Settings(block_ads=False))
        self.assertEqual(dns["ServerURL"], RESOLVERS["unfiltered"]["doh"])

    def test_dns_over_tls_uses_server_name_not_url(self):
        dns = dns_of(Settings(use_tls=True))
        self.assertEqual(dns["DNSProtocol"], "TLS")
        self.assertEqual(dns["ServerName"], RESOLVERS["default"]["dot"])
        self.assertNotIn("ServerURL", dns)

    def test_bootstrap_setting_adds_and_removes_addresses(self):
        expected = RESOLVERS["default"]["ipv4"] + RESOLVERS["default"]["ipv6"]
        self.assertEqual(dns_of(Settings(bootstrap_ips=True))["ServerAddresses"], expected)
        self.assertNotIn("ServerAddresses", dns_of(Settings(bootstrap_ips=False)))

    def test_failover_key_is_written_only_when_enabled(self):
        self.assertNotIn("AllowFailover", dns_of(Settings()))
        self.assertIs(dns_of(Settings(failover=True))["AllowFailover"], True)

    def test_consent_warns_about_unencrypted_fallback_only_with_failover(self):
        self.assertIn("not encrypted", profiles.consent_text(Settings(failover=True)))
        self.assertNotIn("not encrypted", profiles.consent_text(Settings()))

    def test_consent_describes_the_filter_that_is_actually_used(self):
        self.assertIn("does not block ads", profiles.consent_text(Settings(block_ads=False)))
        self.assertIn("adult websites", profiles.consent_text(Settings(block_adult=True)))

    def test_profiles_survive_a_plist_round_trip(self):
        for s in every_combination():
            with self.subTest(settings=s):
                data = build(s)
                self.assertEqual(plistlib.loads(profiles.to_bytes(data)), data)

    def test_checker_catches_bootstrap_addresses_from_another_resolver(self):
        data = build(Settings(block_adult=True))
        data["PayloadContent"][0]["DNSSettings"]["ServerAddresses"] = RESOLVERS["default"]["ipv4"]
        self.assertTrue(any("do not belong" in p for p in profiles.check_profile(data)))

    def test_checker_catches_version_mismatch(self):
        data = build(Settings())
        data["PayloadContent"][0]["PayloadVersion"] = 1
        self.assertTrue(any("differ" in p for p in profiles.check_profile(data)))

    def test_checker_catches_a_profile_that_cannot_be_removed(self):
        data = build(Settings())
        data["PayloadRemovalDisallowed"] = True
        self.assertTrue(any("PayloadRemovalDisallowed" in p for p in profiles.check_profile(data)))

    def test_checker_catches_a_host_that_is_not_adguard(self):
        data = build(Settings())
        data["PayloadContent"][0]["DNSSettings"]["ServerURL"] = "https://resolver.example/dns-query"
        self.assertTrue(any("not an AdGuard DNS host" in p for p in profiles.check_profile(data)))

    def test_checker_catches_an_empty_consent_text(self):
        data = build(Settings())
        data["ConsentText"]["default"] = "   "
        self.assertTrue(any("ConsentText" in p for p in profiles.check_profile(data)))


if __name__ == "__main__":
    unittest.main()
