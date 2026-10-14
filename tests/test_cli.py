import os
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRESET_FILES = {
    "Quiet-DNS-Standard.mobileconfig",
    "Quiet-DNS-Family.mobileconfig",
    "Quiet-DNS-Unfiltered.mobileconfig",
    "Quiet-DNS-Paused.mobileconfig",
}
SAMPLE_CONF = """[Interface]
PrivateKey = TEST-ONLY-NOT-A-REAL-KEY
Address = 10.2.0.2/32
DNS = 10.2.0.1

[Peer]
PublicKey = TEST-ONLY-PEER-KEY
AllowedIPs = 0.0.0.0/0
Endpoint = 192.0.2.1:51820
"""


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "quiet", *args],
                          cwd=ROOT, capture_output=True, text=True)


class CliTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def test_presets_write_four_profiles_and_the_paused_one_keeps_its_dns_settings(self):
        out = self.tmp / "dist"
        result = run("presets", "--out", str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in out.glob("*.mobileconfig")}, PRESET_FILES)
        paused = plistlib.loads((out / "Quiet-DNS-Paused.mobileconfig").read_bytes())
        self.assertEqual(paused["PayloadContent"][0]["OnDemandRules"], [{"Action": "Disconnect"}])

    def test_profile_command_builds_a_family_profile_over_tls(self):
        target = self.tmp / "custom.mobileconfig"
        result = run("profile", "-o", str(target), "--adult", "--tls")
        self.assertEqual(result.returncode, 0, result.stderr)
        dns = plistlib.loads(target.read_bytes())["PayloadContent"][0]["DNSSettings"]
        self.assertEqual(dns["DNSProtocol"], "TLS")
        self.assertEqual(dns["ServerName"], "family.adguard-dns.com")

    def test_site_option_adds_a_home_screen_icon_and_plain_profiles_have_none(self):
        with_icon = self.tmp / "with-icon.mobileconfig"
        result = run("profile", "-o", str(with_icon), "--site", "https://example.com/quiet/")
        self.assertEqual(result.returncode, 0, result.stderr)
        content = plistlib.loads(with_icon.read_bytes())["PayloadContent"]
        self.assertEqual(content[1]["URL"], "https://example.com/quiet/")
        self.assertEqual(content[1]["PayloadType"], "com.apple.webClip.managed")

        plain = self.tmp / "plain.mobileconfig"
        self.assertEqual(run("profile", "-o", str(plain)).returncode, 0)
        self.assertEqual(len(plistlib.loads(plain.read_bytes())["PayloadContent"]), 1)

    def test_site_option_refuses_a_plain_http_address(self):
        target = self.tmp / "bad.mobileconfig"
        result = run("profile", "-o", str(target), "--site", "http://example.com/quiet/")
        self.assertEqual(result.returncode, 1)
        self.assertIn("https://", result.stderr)
        self.assertFalse(target.exists())

    def test_wg_writes_a_private_file_and_refuses_to_overwrite_without_force(self):
        conf = self.tmp / "my.conf"
        conf.write_text(SAMPLE_CONF, encoding="utf-8")
        out = self.tmp / "quiet.conf"

        first = run("wg", str(conf), "-o", str(out))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertNotIn("TEST-ONLY-NOT-A-REAL-KEY", first.stdout + first.stderr)
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)

        second = run("wg", str(conf), "-o", str(out))
        self.assertEqual(second.returncode, 1)
        self.assertIn("--force", second.stderr)

        third = run("wg", str(conf), "-o", str(out), "--force")
        self.assertEqual(third.returncode, 0, third.stderr)

    def test_wg_refuses_to_write_inside_the_project(self):
        conf = self.tmp / "my.conf"
        conf.write_text(SAMPLE_CONF, encoding="utf-8")
        target = ROOT / "should-not-exist.conf"
        result = run("wg", str(conf), "-o", str(target))
        self.assertEqual(result.returncode, 1)
        self.assertFalse(target.exists())

    def test_missing_input_is_a_clean_error_not_a_traceback(self):
        result = run("wg", str(self.tmp / "absent.conf"), "-o", str(self.tmp / "out.conf"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_signed_profiles_verify_and_match_the_unsigned_bytes(self):
        if shutil.which("openssl") is None:
            self.skipTest("openssl is not installed")
        cert, key = self.tmp / "cert.pem", self.tmp / "key.pem"
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", str(key), "-out", str(cert), "-days", "1",
                        "-subj", "/CN=Quiet test signer"], check=True, capture_output=True)

        unsigned = self.tmp / "unsigned"
        signed = self.tmp / "signed"
        self.assertEqual(run("presets", "--out", str(unsigned)).returncode, 0)
        result = run("presets", "--out", str(signed),
                     "--sign", str(cert), str(key))
        self.assertEqual(result.returncode, 0, result.stderr)

        recovered = self.tmp / "recovered.plist"
        verify = subprocess.run(["openssl", "smime", "-verify", "-noverify", "-inform", "der",
                                 "-in", str(signed / "Quiet-DNS-Standard.mobileconfig"),
                                 "-out", str(recovered)], capture_output=True, text=True)
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertEqual(recovered.read_bytes(), (unsigned / "Quiet-DNS-Standard.mobileconfig").read_bytes())

    def test_a_failed_signature_leaves_no_file_behind(self):
        if shutil.which("openssl") is None:
            self.skipTest("openssl is not installed")
        out = self.tmp / "out"
        result = run("presets", "--out", str(out), "--sign",
                     str(self.tmp / "missing.pem"), str(self.tmp / "missing.key"))
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(list(out.glob("*.mobileconfig")) if out.exists() else [])


if __name__ == "__main__":
    unittest.main()
