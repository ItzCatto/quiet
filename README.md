# Quiet DNS

Quiet DNS sends your DNS lookups over an encrypted connection to AdGuard DNS, with the filtering you choose. It makes iPhone and Mac profiles that set this up, and it can point a WireGuard config at the same DNS.

## What's in the project

| Path | What it is |
|---|---|
| `site/` | The website: `index.html` (markup), `site.css` (design), `core.js` (profile builder), `app.js` (screens and settings). |
| `site/manifest.webmanifest`, `site/icons/` | Home-screen metadata and icons, so the site can be added to an iPhone's home screen. |
| `scripts/make_icons.py` | Regenerates the home-screen icons. |
| `quiet/` | The Python package and command line that build profiles and WireGuard configs. |
| `tests/` | Automated tests, including a check that the website and the command line build identical profiles. |
| `dist/` | Built profiles. Generated, not committed. |
| `docs/` | Guides: iPhone install, settings, WireGuard, security, and the audit report. |
| `CHANGELOG.md` | What changed in each version. |

## Quick start

Run these from the project folder. The code is tested with Python 3.13 and needs no packages beyond the standard library. The signing command also needs `openssl`.

```
python3 -m unittest discover -s tests          # run the tests
python3 -m quiet presets                       # build the four preset profiles into dist/
python3 -m quiet profile -o my.mobileconfig --adult --tls
python3 -m quiet wg my-tunnel.conf -o ~/Desktop/quiet-tunnel.conf
```

Open `site/index.html` in a browser to use the site. To download profiles from the page, host the `site/` folder on any static web host. Some previews block file downloads.

On iPhone, open the hosted site in Safari, tap Share, then Add to Home Screen. It opens full screen with the Quiet icon.

## One entry on iPhone

Every Quiet DNS profile has the same name, identifier and UUID. A new download is meant to replace the entry already on the iPhone, so changing a setting, pausing and resuming all work on one entry. Removing it turns Quiet DNS off. This is the intended design. It hasn't been confirmed on a device yet.

## Status

**Checked here:**
- 76 automated tests pass: settings, profile structure, the pause rule, WireGuard rewriting, the command line, signing, the browser builder, the resolver check's replies, and the website's assets, icons, install pictures, bundled font and content security policy.
- The browser builder matches the Python builder for all 64 combinations of settings.
- A headless Chromium run at phone and desktop widths: every screen fits, the On and Off switch, the other switches and links work with focus moved to each screen's title, and the downloaded profiles (including the paused one) match the Python output.

**Not checked yet:**
- Installing on a real iPhone: the owner has installed the profile, and it appears under Downloaded Profile and in VPN & Device Management. Ads being blocked in Safari and other apps isn't confirmed yet. Start with [docs/install-iphone.md](docs/install-iphone.md).
- Installing on a Mac.
- The weekly AdGuard DNS check (`.github/workflows/resolver-check.yml`). It hasn't run on GitHub yet. The sandbox used to build it couldn't reach AdGuard's hostnames, so the first scheduled run is the real test. Run it by hand with `python3 scripts/check_resolvers.py` from a machine that can reach AdGuard.
- Whether a new download updates the existing entry instead of adding one.
- Pausing. The paused profile is experimental.
- Signing with a real certificate. Only a throwaway test certificate was used.
- Importing the WireGuard output into the WireGuard app.
- How iOS combines a WireGuard tunnel's DNS with an installed DNS profile.

## Limits to know about

- **There is no one-tap switch in iPhone Settings.** Quiet DNS is on while its profile is installed. Pausing uses a paused profile, and removing the profile turns Quiet DNS off completely. A real switch needs an iOS app built with Apple's DNS Settings extension, which is not part of this project.
- **Artifact previews can't deliver the profile.** The artifact allowlist for downloads does not include `.mobileconfig`, so the profile has to come from a normal web host.
- **Local network names may stop resolving** while Quiet DNS is on, because the encrypted resolver can't see your network. See [docs/settings.md](docs/settings.md).

Quiet is not affiliated with AdGuard or Proton.
