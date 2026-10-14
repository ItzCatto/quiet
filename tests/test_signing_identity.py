"""The free signing helper: its name rule and the trust profile it writes. No keys are created here."""

import importlib.util
import plistlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location("make_signing_identity", ROOT / "scripts" / "make_signing_identity.py")
helper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(helper)


class SigningIdentityTests(unittest.TestCase):
    def test_name_allows_plain_names(self):
        self.assertIsNotNone(helper.NAME_RULE.match("Quiet DNS personal signing"))
        self.assertIsNotNone(helper.NAME_RULE.match("Ana's phone, 2026"))

    def test_name_rejects_characters_that_break_the_certificate_subject(self):
        for bad in ("a/b", "a=b", "a\nb", "", "x" * 65):
            with self.subTest(name=bad):
                self.assertIsNone(helper.NAME_RULE.match(bad))

    def test_trust_profile_installs_the_certificate_as_a_root(self):
        der = b"\x30\x82fake-der-bytes"
        profile = plistlib.loads(helper.trust_profile(der, "Test"))
        self.assertEqual(profile["PayloadType"], "Configuration")
        self.assertFalse(profile["PayloadRemovalDisallowed"])
        root = profile["PayloadContent"][0]
        self.assertEqual(root["PayloadType"], "com.apple.security.root")
        self.assertEqual(root["PayloadContent"], der)

    def test_trust_profile_has_a_fresh_identity_each_time(self):
        first = plistlib.loads(helper.trust_profile(b"x", "Test"))
        second = plistlib.loads(helper.trust_profile(b"x", "Test"))
        self.assertNotEqual(first["PayloadUUID"], second["PayloadUUID"])


if __name__ == "__main__":
    unittest.main()
