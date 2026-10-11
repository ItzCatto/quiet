import unittest

from quiet import wireguard
from quiet.settings import RESOLVERS

# Test data only. These keys are placeholders, not real WireGuard keys.
SAMPLE = """[Interface]
# Key for Quiet
PrivateKey = TEST-ONLY-NOT-A-REAL-KEY
Address = 10.2.0.2/32, 2a07:b944::2:2/128
DNS = 10.2.0.1, 2a07:b944::2:1

[Peer]
# US-FREE#4
PublicKey = TEST-ONLY-PEER-KEY
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = 192.0.2.1:51820
PersistentKeepalive = 25
"""

DEFAULT_DNS = "DNS = " + ", ".join(RESOLVERS["default"]["ipv4"] + RESOLVERS["default"]["ipv6"])


class WireGuardTests(unittest.TestCase):
    def test_replaces_dns_and_keeps_everything_else(self):
        out = wireguard.retarget_dns(SAMPLE, "default")
        self.assertIn(DEFAULT_DNS, out.splitlines())
        self.assertNotIn("10.2.0.1", out)
        self.assertIn("PrivateKey = TEST-ONLY-NOT-A-REAL-KEY", out)
        self.assertIn("Endpoint = 192.0.2.1:51820", out)
        self.assertIn("# Key for Quiet", out)
        self.assertIn("[Peer]", out)

    def test_dns_line_sits_right_after_address(self):
        lines = wireguard.retarget_dns(SAMPLE, "default").splitlines()
        address_at = next(i for i, line in enumerate(lines) if line.startswith("Address"))
        self.assertEqual(lines[address_at + 1], DEFAULT_DNS)

    def test_family_mode_uses_family_addresses(self):
        out = wireguard.retarget_dns(SAMPLE, "family")
        self.assertIn(RESOLVERS["family"]["ipv4"][0], out)
        self.assertNotIn(RESOLVERS["default"]["ipv4"][0], out)

    def test_reports_the_dns_that_was_there(self):
        self.assertEqual(wireguard.current_dns(SAMPLE), ["10.2.0.1", "2a07:b944::2:1"])

    def test_adds_dns_when_the_config_has_none(self):
        no_dns = SAMPLE.replace("DNS = 10.2.0.1, 2a07:b944::2:1\n", "")
        out = wireguard.retarget_dns(no_dns, "unfiltered")
        self.assertIn("DNS = " + ", ".join(RESOLVERS["unfiltered"]["ipv4"] + RESOLVERS["unfiltered"]["ipv6"]),
                      out.splitlines())

    def test_is_idempotent(self):
        once = wireguard.retarget_dns(SAMPLE, "default")
        self.assertEqual(wireguard.retarget_dns(once, "default"), once)

    def test_keys_are_case_insensitive(self):
        lower = SAMPLE.replace("DNS = ", "dns = ")
        self.assertNotIn("10.2.0.1", wireguard.retarget_dns(lower, "default"))

    def test_rejects_unknown_mode(self):
        with self.assertRaises(wireguard.WireGuardError):
            wireguard.retarget_dns(SAMPLE, "nonsense")

    def test_rejects_config_without_a_peer(self):
        no_peer = SAMPLE.split("[Peer]")[0]
        with self.assertRaises(wireguard.WireGuardError):
            wireguard.retarget_dns(no_peer, "default")

    def test_rejects_two_interfaces(self):
        with self.assertRaises(wireguard.WireGuardError):
            wireguard.retarget_dns(SAMPLE + "\n[Interface]\nPrivateKey = X\n", "default")

    def test_rejects_config_without_a_private_key(self):
        no_key = SAMPLE.replace("PrivateKey = TEST-ONLY-NOT-A-REAL-KEY\n", "")
        with self.assertRaises(wireguard.WireGuardError):
            wireguard.retarget_dns(no_key, "default")

    def test_error_messages_never_echo_the_key(self):
        broken = SAMPLE.replace("[Peer]", "[Other]")
        with self.assertRaises(wireguard.WireGuardError) as ctx:
            wireguard.retarget_dns(broken, "default")
        self.assertNotIn("TEST-ONLY-NOT-A-REAL-KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
