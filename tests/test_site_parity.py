"""The website builds its profile in the browser. This checks it builds the same profile as Python."""

import base64
import itertools
import json
import plistlib
import shutil
import subprocess
import unittest
from dataclasses import asdict
from pathlib import Path

from quiet import profiles
from quiet.settings import RESOLVERS, Settings

ROOT = Path(__file__).resolve().parent.parent
ICON = ROOT / "site" / "icons" / "apple-touch-icon.png"
SITE_URL = "https://example.com/quiet/"

# Loads the page's <script id="quiet-core"> in a sandbox. Each case gives a profile, or the error the browser raises.
NODE_PROFILES = r"""
const vm = require('vm');
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const ctx = {};
vm.createContext(ctx);
vm.runInContext(input.core, ctx);
const out = input.cases.map(c => {
  try {
    return { xml: ctx.QuietCore.profileXML(c.settings, c.siteUrl) };
  } catch (e) {
    return { error: String((e && e.message) || e) };
  }
});
process.stdout.write(JSON.stringify(out));
"""

NODE_CATALOGUE = r"""
const vm = require('vm');
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const ctx = {};
vm.createContext(ctx);
vm.runInContext(input.core, ctx);
process.stdout.write(JSON.stringify(ctx.QuietCore.RESOLVERS));
"""


def every_case() -> list[dict]:
    """Every named resolver in every transport and toggle, plus the settings with no named resolver."""
    cases = []
    for key, tls, boot, failover, enabled, site in itertools.product(
            RESOLVERS, [False, True], [False, True], [False, True], [False, True], [None, SITE_URL]):
        cases.append({"settings": asdict(Settings(enabled=enabled, use_tls=tls, bootstrap_ips=boot,
                                                  failover=failover, resolver=key)),
                      "siteUrl": site})
    for values in itertools.product([True, False], repeat=6):
        for site in (None, SITE_URL):
            cases.append({"settings": asdict(Settings(*values)), "siteUrl": site})
    return cases


def refused(s: Settings) -> bool:
    """DNS over TLS is refused for a filter that doesn't publish a hostname for it."""
    return s.use_tls and RESOLVERS[s.resolver_key()]["dot"] is None


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class SiteParityTests(unittest.TestCase):
    def setUp(self):
        self.core = (ROOT / "site" / "core.js").read_text(encoding="utf-8")
        self.site_files = [p.read_text(encoding="utf-8")
                           for p in (ROOT / "site").iterdir()
                           if p.suffix in {".html", ".js", ".css"}]

    def run_node(self, source: str, payload: dict):
        proc = subprocess.run(["node", "-e", source], input=json.dumps(payload),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_browser_builder_matches_python_for_every_combination(self):
        cases = every_case()
        results = self.run_node(NODE_PROFILES, {"core": self.core, "cases": cases})
        self.assertEqual(len(results), len(cases))

        icon = ICON.read_bytes()
        for case, result in zip(cases, results):
            s = Settings(**case["settings"])
            with self.subTest(settings=case["settings"], siteUrl=case["siteUrl"]):
                if refused(s):
                    self.assertIn("error", result)
                    with self.assertRaises(profiles.ProfileError):
                        profiles.build_profile(s, case["siteUrl"], icon if case["siteUrl"] else None)
                    continue
                self.assertNotIn("error", result, result.get("error"))
                self.assertEqual(plistlib.loads(result["xml"].encode("utf-8")),
                                 profiles.build_profile(s, case["siteUrl"], icon if case["siteUrl"] else None))

    def test_browser_resolver_table_matches_python(self):
        table = self.run_node(NODE_CATALOGUE, {"core": self.core})
        self.assertEqual(table, json.loads(json.dumps(RESOLVERS)))

    def test_home_screen_icon_in_the_browser_is_the_icon_file(self):
        encoded = base64.b64encode(ICON.read_bytes()).decode("ascii")
        self.assertIn(f'icon: "{encoded}"', self.core)

    def test_page_never_accepts_a_config_file(self):
        # The site must not take WireGuard configs or keys, so nothing secret reaches a web page.
        for text in self.site_files:
            self.assertNotIn('type="file"', text)
            self.assertNotIn("PrivateKey", text)


if __name__ == "__main__":
    unittest.main()
