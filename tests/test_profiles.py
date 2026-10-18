import itertools
import plistlib
import unittest
from unittest import mock
import uuid

from quiet import profiles
from quiet.__main__ import PRESETS
from quiet.settings import RESOLVERS, Settings



def every_combination():
    for values in itertools.product([True, False], repeat=6):
        yield Settings(*values)


def build(s: Settings) -> dict:
    return profiles.build_profile(s)


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

    def test_checker_catches_a_payload_version_other_than_1(self):
        data = build(Settings())
        data["PayloadContent"][0]["PayloadVersion"] = 14083754
        self.assertTrue(any("must be 1" in p for p in profiles.check_profile(data)))

    def test_checker_catches_a_profile_that_cannot_be_removed(self):
        data = build(Settings())
        data["PayloadRemovalDisallowed"] = True
        self.assertTrue(any("PayloadRemovalDisallowed" in p for p in profiles.check_profile(data)))

    def test_checker_catches_a_host_that_is_not_a_quiet_resolver(self):
        data = build(Settings())
        data["PayloadContent"][0]["DNSSettings"]["ServerURL"] = "https://resolver.example/dns-query"
        self.assertTrue(any("not one of the Quiet DNS resolvers" in p for p in profiles.check_profile(data)))

    def test_checker_catches_an_empty_consent_text(self):
        data = build(Settings())
        data["ConsentText"]["default"] = "   "
        self.assertTrue(any("ConsentText" in p for p in profiles.check_profile(data)))


if __name__ == "__main__":
    unittest.main()


class PayloadVersionTests(unittest.TestCase):
    def test_every_profile_uses_payload_version_1(self):
        # iPhone rejects other values with "The profile version is not supported".
        for s in (Settings(), Settings(enabled=False)):
            data = profiles.build_profile(s)
            self.assertEqual(data["PayloadVersion"], 1)
            self.assertEqual(data["PayloadContent"][0]["PayloadVersion"], 1)
            self.assertEqual(profiles.check_profile(data), [])

    def test_checker_rejects_a_top_level_version_other_than_1(self):
        data = profiles.build_profile(Settings())
        data["PayloadVersion"] = 2
        self.assertTrue(any("PayloadVersion must be 1" in p for p in profiles.check_profile(data)))


class NoHomeScreenIconTests(unittest.TestCase):
    def test_a_profile_is_only_the_dns_payload_so_it_adds_no_home_screen_icon(self):
        for s in (Settings(), Settings(enabled=False), Settings(use_tls=True), Settings(block_adult=True)):
            with self.subTest(settings=s):
                content = build(s)["PayloadContent"]
                self.assertEqual([p["PayloadType"] for p in content], ["com.apple.dnsSettings.managed"])

    def test_checker_rejects_a_web_clip_added_next_to_the_dns_payload(self):
        data = build(Settings())
        data["PayloadContent"].append({"PayloadType": "com.apple.webClip.managed",
                                       "URL": "https://example.com/quiet/", "PayloadVersion": 1})
        self.assertTrue(any("exactly one payload" in p for p in profiles.check_profile(data)))


class ResolverTests(unittest.TestCase):
    def test_every_resolver_builds_and_passes_every_check_in_each_transport(self):
        for key, r in RESOLVERS.items():
            for tls, boot, enabled in itertools.product([False, True], repeat=3):
                s = Settings(resolver=key, use_tls=tls, bootstrap_ips=boot, enabled=enabled)
                with self.subTest(resolver=key, tls=tls, bootstrap=boot, enabled=enabled):
                    if tls and r["dot"] is None:
                        with self.assertRaises(profiles.ProfileError):
                            build(s)
                        continue
                    data = build(s)
                    self.assertEqual(profiles.check_profile(data), [])
                    self.assertEqual(plistlib.loads(profiles.to_bytes(data)), data)
                    dns = data["PayloadContent"][0]["DNSSettings"]
                    if tls:
                        self.assertEqual(dns["ServerName"], r["dot"])
                    else:
                        self.assertEqual(dns["ServerURL"], r["doh"])
                    if boot:
                        self.assertEqual(dns["ServerAddresses"], r["ipv4"] + r["ipv6"])

    def test_a_named_resolver_is_used_instead_of_the_toggles(self):
        dns = dns_of(Settings(resolver="unfiltered", block_ads=False, block_adult=True))
        self.assertEqual(dns["ServerURL"], RESOLVERS["unfiltered"]["doh"])

    def test_summary_and_consent_name_the_provider_and_what_it_blocks(self):
        s = Settings(resolver="unfiltered")
        self.assertEqual(profiles.summary(s), "Encrypted DNS through AdGuard DNS. It does not block ads or trackers.")
        self.assertIn("encrypted connection to AdGuard DNS, which does not block ads or trackers.",
                      profiles.consent_text(s))
        self.assertIn("but AdGuard DNS can.", profiles.consent_text(s))

    def test_bootstrap_addresses_from_another_filter_are_caught(self):
        data = build(Settings(resolver="family"))
        data["PayloadContent"][0]["DNSSettings"]["ServerAddresses"] = RESOLVERS["unfiltered"]["ipv4"]
        self.assertTrue(any("do not belong" in p for p in profiles.check_profile(data)))

    def test_a_filter_without_dns_over_tls_refuses_it_rather_than_guessing(self):
        no_tls = dict(RESOLVERS["default"], dot=None)
        with mock.patch.dict(RESOLVERS, {"no-tls": no_tls}):
            with self.assertRaises(profiles.ProfileError):
                build(Settings(resolver="no-tls", use_tls=True))

    def test_checker_catches_a_dns_over_tls_host_that_is_not_a_resolver(self):
        data = build(Settings(use_tls=True))
        data["PayloadContent"][0]["DNSSettings"]["ServerName"] = "dns.example"
        self.assertTrue(any("not one of the Quiet DNS resolvers" in p for p in profiles.check_profile(data)))
