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

    def test_font_is_bundled_with_its_license(self):
        # The type comes from this folder, not from a font service, so the page makes no request to another website.
        css = (SITE / "site.css").read_text(encoding="utf-8")
        self.assertIn('url("fonts/schibsted-grotesk-latin-wght-normal.woff2")', css)
        self.assertTrue((SITE / "fonts" / "schibsted-grotesk-latin-wght-normal.woff2").exists())
        self.assertTrue((SITE / "fonts" / "Schibsted-Grotesk-OFL.txt").exists())

    def test_page_loads_nothing_from_another_website(self):
        # The privacy screen says the site makes no requests to other websites, so fonts and scripts stay on this host.
        css = (SITE / "site.css").read_text(encoding="utf-8")
        for value in re.findall(r'\b(?:src|href)="([^"]*)"', self.html):
            with self.subTest(value=value):
                self.assertIsNone(re.match(r"https?:", value), value)
        self.assertNotIn("@import", css)
        self.assertIsNone(re.search(r"url\(\s*['\"]?https?:", css))

    def test_page_runs_under_a_strict_policy_with_no_inline_scripts(self):
        self.assertIn('http-equiv="Content-Security-Policy"', self.html)
        self.assertIn("default-src 'self'", self.html)
        self.assertIn("script-src 'self'", self.html)
        self.assertIsNone(re.search(r"<script(?![^>]*\bsrc=)", self.html), "inline script found")

    def test_every_picture_has_a_file_on_disk_and_alt_text(self):
        pictures = re.findall(r"<img\b[^>]*>", self.html)
        self.assertTrue(pictures)
        for tag in pictures:
            src = re.search(r'\bsrc="([^"]+)"', tag).group(1)
            alt = re.search(r'\balt="([^"]*)"', tag)
            with self.subTest(src=src):
                self.assertTrue((SITE / src).exists(), src)
                self.assertTrue(alt and alt.group(1).strip(), "missing alt text")

    def test_pictures_carry_no_photo_metadata(self):
        # Screenshots can carry dates and device details in their EXIF block, so the copies on the site have none.
        pictures = list((SITE / "tutorial").glob("*.jpg"))
        self.assertTrue(pictures)
        for path in pictures:
            with self.subTest(path=path.name):
                self.assertNotIn(b"Exif\x00\x00", path.read_bytes())

    def test_the_page_never_links_to_settings_by_url(self):
        # Safari doesn't open a Settings screen from a web link, so the page gives the steps instead.
        self.assertIsNone(re.search(r"prefs:", self.html, re.IGNORECASE))

    def test_each_screen_sets_its_own_browser_tab_title(self):
        js = (SITE / "app.js").read_text(encoding="utf-8")
        self.assertIn("document.title", js)

    def test_installed_check_runs_before_the_page_is_drawn(self):
        self.assertIn('<script src="boot.js"></script>', self.html)
        boot = (SITE / "boot.js").read_text(encoding="utf-8")
        self.assertIn('classList.add("installed")', boot)


if __name__ == "__main__":
    unittest.main()
