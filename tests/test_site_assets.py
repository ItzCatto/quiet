"""The website's home-screen assets, and the links that point at screens and files."""

import json
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return struct.unpack(">II", data[16:24])


class SiteAssetTests(unittest.TestCase):
    def setUp(self):
        self.html = (SITE / "index.html").read_text(encoding="utf-8")

    def test_manifest_parses_and_each_icon_matches_its_declared_size(self):
        manifest = json.loads((SITE / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["display"], "standalone")
        self.assertTrue(manifest["icons"])
        for icon in manifest["icons"]:
            with self.subTest(icon=icon["src"]):
                path = SITE / icon["src"]
                self.assertTrue(path.exists(), icon["src"])
                width, height = png_size(path)
                self.assertEqual(f"{width}x{height}", icon["sizes"])

    def test_page_links_the_manifest_and_a_180_pixel_home_screen_icon(self):
        self.assertIn('href="manifest.webmanifest"', self.html)
        self.assertIn('href="icons/apple-touch-icon.png"', self.html)
        self.assertEqual(png_size(SITE / "icons" / "apple-touch-icon.png"), (180, 180))

    def test_every_in_page_link_points_at_a_real_screen(self):
        screens = set(re.findall(r'<section class="screen[^"]*" id="screen-([a-z]+)"', self.html))
        self.assertIn("home", screens)
        for name in set(re.findall(r'href="#([a-z]*)"', self.html)):
            with self.subTest(link=name):
                self.assertIn(name, screens)

    def test_every_screen_has_a_focusable_title_for_keyboard_and_screen_reader_users(self):
        screens = re.findall(r'<section class="screen[^"]*" id="screen-([a-z]+)"', self.html)
        for name in screens:
            with self.subTest(screen=name):
                self.assertIn(f'id="title-{name}" tabindex="-1"', self.html)

    def test_karla_font_is_bundled_with_its_license(self):
        # The type comes from this folder, not from a font service, so the page makes no request to another website.
        css = (SITE / "site.css").read_text(encoding="utf-8")
        self.assertIn('url("fonts/karla-latin-wght-normal.woff2")', css)
        self.assertTrue((SITE / "fonts" / "karla-latin-wght-normal.woff2").exists())
        self.assertTrue((SITE / "fonts" / "Karla-OFL.txt").exists())

    def test_page_loads_nothing_from_another_website(self):
        # The privacy screen says the site makes no requests to other websites, so fonts and scripts stay on this host.
        css = (SITE / "site.css").read_text(encoding="utf-8")
        for value in re.findall(r'\b(?:src|href)="([^"]*)"', self.html):
            with self.subTest(value=value):
                self.assertIsNone(re.match(r"https?:", value), value)
        self.assertNotIn("@import", css)
        self.assertIsNone(re.search(r"url\(\s*['\"]?https?:", css))


if __name__ == "__main__":
    unittest.main()
