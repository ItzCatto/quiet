"""The website builds its profile in the browser. This checks it builds the same profile as Python."""

import base64
import itertools
import json
import plistlib
import re
import shutil
import subprocess
import unittest
from dataclasses import asdict
from pathlib import Path

from quiet import profiles
from quiet.settings import Settings

ROOT = Path(__file__).resolve().parent.parent
ICON = ROOT / "site" / "icons" / "apple-touch-icon.png"
SITE_URL = "https://example.com/quiet/"

# Loads the page's <script id="quiet-core"> in a sandbox and asks it for each profile.
NODE_RUNNER = r"""
const vm = require('vm');
const input = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const ctx = {};
vm.createContext(ctx);
vm.runInContext(input.core, ctx);
const out = input.cases.map(c => ctx.QuietCore.profileXML(c.settings, c.siteUrl));
process.stdout.write(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class SiteParityTests(unittest.TestCase):
    def setUp(self):
        self.core = (ROOT / "site" / "core.js").read_text(encoding="utf-8")
        self.site_files = [p.read_text(encoding="utf-8")
                           for p in (ROOT / "site").iterdir()
                           if p.suffix in {".html", ".js", ".css"}]

    def test_browser_builder_matches_python_for_every_combination(self):
        # Every combination of settings, with and without a site address (which adds the Home Screen icon).
        cases = [{"settings": asdict(Settings(*values)), "siteUrl": site}
                 for values in itertools.product([True, False], repeat=6)
                 for site in (None, SITE_URL)]
        proc = subprocess.run(["node", "-e", NODE_RUNNER],
                              input=json.dumps({"core": self.core, "cases": cases}),
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        icon = ICON.read_bytes()
        for case, xml in zip(cases, json.loads(proc.stdout)):
            s = Settings(**case["settings"])
            with self.subTest(settings=case["settings"], siteUrl=case["siteUrl"]):
                self.assertEqual(plistlib.loads(xml.encode("utf-8")),
                                 profiles.build_profile(s, case["siteUrl"], icon if case["siteUrl"] else None))

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
