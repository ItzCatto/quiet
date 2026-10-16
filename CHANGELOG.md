# Changelog

## 2.4.0

### Added
- **Thirteen resolvers and filters.** Besides AdGuard DNS Standard, Family and Unfiltered, you can now choose from DNS4EU (five filters) and Control D (five filters, including four Hagezi blocklist tiers). The website's Filter list shows them grouped by provider. The command line takes `--resolver KEY`, and `python3 -m quiet resolvers` lists every key.
- **Where each resolver comes from.** [docs/resolvers.md](docs/resolvers.md) gives the source of each address and filter, what each one blocks, and the date it was checked (16 October 2026). It also says what is left out and why: Mullvad's public DNS is discontinued on 2 November 2026, and account-based resolvers are left out so no account ID goes into a profile.
- **`wg --mode` takes every resolver.** The WireGuard command can point a config at any of the thirteen.
- **The weekly check covers every resolver.** It asks each resolver's HTTPS address, and its DNS over TLS address where one is published, then tries each IPv4 address the profiles include.

### Changed
- A named resolver decides what is blocked, so `--resolver` can't be combined with `--no-ads` or `--adult`. Without `--resolver`, the two AdGuard options work as before, and the presets are unchanged.
- DNS over TLS is off for the Control D filters, which publish only HTTPS addresses. The website turns the switch off for them, and the command line refuses `--tls` with them.
- The website and the docs say "the resolver you chose" where they used to name AdGuard.

### Unverified
- The sandbox used to build this release couldn't reach any resolver. The addresses were checked against each provider's published page, but whether each resolver answers, and whether DNS over TLS works for Control D, is first tested by the weekly check on GitHub.
- Nothing in this release has been tested on an iPhone.

### Tests
- 109 automated tests, up from 91. New tests check every resolver in both transports, that the website and the command line build identical profiles for each, that DNS over TLS is refused where a filter has no hostname, the resolver list, and the new command-line options.

## 2.3.0

### Added
- **A Home Screen icon in the profile.** A profile built from the website also adds a Quiet DNS icon. Installing the profile puts the icon on the Home Screen, and it opens the page you downloaded from. The icon stays when the profile is paused. The command line adds the icon with `--site URL`, which must be an https address. Not tested on a phone yet.
- **Changes since your last download.** The Profile page lists the settings that differ from the profile on your iPhone, in plain words.
- **Home Screen icon on the Profile page.** Shows whether the profile includes the icon.

### Changed
- The Install page says when the Quiet DNS icon will appear.

### Tests
- 91 automated tests, up from 80. New tests check the icon in the profile, that the browser builder matches the command line with and without the icon, that the embedded icon is the icon file, and that the command line refuses a plain http address.

## 2.2.1

### Fixed
- **"The profile version is not supported" on iPhone.** Every profile now uses PayloadVersion 1, at the top level and in the DNS payload. Apple's examples and WireGuard's documentation use 1, and iPhone rejected the Unix time we had been writing. A profile with the same PayloadIdentifier overwrites the one installed before it, so a new download still replaces the Quiet DNS entry. The command line and the website build the same profile.
- **Website builds and the command line no longer take a version option.** The version is fixed, so nothing can produce a version iPhone rejects.
- **The Settings link.** A web page can't open Settings on iPhone, so the Open Settings link has gone. After Save, the bar says where to tap.
- **Install steps.** Three steps: download the profile, open Settings, tap General, then VPN & Device Management, and install. Step text no longer splits into fragments on the page.
- **The switch name.** Screen readers announce the switch as Quiet DNS, on or off, instead of the status sentence.
- **Download links last longer.** A download link stays valid for five minutes, so a slow tap on Allow still works.
- **Browser tab titles.** Each screen sets its own title, such as "Filters – Quiet DNS".
- **Download failures.** If a download doesn't start, the page says to open it in Safari.
- **Home-screen icon.** The wave's ends had stray hooks, and the icon drew a different wave from the logo. Both now come from one path, drawn with clean rounded ends.

### Added
- **Install pictures.** The Install page has three numbered steps, with two pictures from an iPhone's Settings. The pictures have their photo details removed.
- **Help page.** Short answers to common questions: ads that still show, the "Not Signed" label, local devices, two Quiet DNS profiles, and removing Quiet DNS.
- **First-run steps.** The dashboard shows three steps until the first profile is downloaded.
- **Privacy and Help in a browser tab.** Both open from the home page without the Home Screen app.
- **A content security policy.** The page can load only its own scripts, styles, fonts and pictures. The early-start script moved to its own file to allow this.
- **Discard.** A Discard button beside Save puts the settings back to the last downloaded profile. It shows only when there is something to discard.
- **Filter comparison on Help.** The first question says what Standard, Family and Unfiltered each do.
- **Last saved and support details.** The Profile page shows when the profile was last downloaded. Copy details for support copies the version, status, server, protocol, addresses and last saved time. It holds nothing about the device.
- **Larger text.** Settings > Text size makes all the text on the site bigger. Every size on the page is in rem units, so the whole site scales.
- **Free signing for your own iPhone.** `scripts/make_signing_identity.py` makes a signing key and certificate outside the project, and a profile that installs the certificate as trusted on your iPhone. Profiles you sign then show your name as the signer on that phone. Other iPhones still show "Not Verified". Tested on a computer, not yet on an iPhone.
- **A weekly check of AdGuard DNS.** `scripts/check_resolvers.py` asks each DNS-over-HTTPS and DNS-over-TLS address for example.com, and tries each IPv4 address the profiles include. A scheduled GitHub workflow runs it every Monday, and GitHub emails the owner if a run fails.

### Changed
- **Every page redesigned again, in a dark theme.** The page is near-black with light text, and one soft mint colour means "on". The type is Schibsted Grotesk, served with the site. Light is available in Settings, and System follows the phone. There are no cards, tiles or grouped lists.
- **One switch on the dashboard.** A large switch in the middle of the dashboard shows Off and On in a track, and a knob sits under the current word. Clicking either word, or pressing Space on the focused switch, changes the setting.
- **Home page in a browser.** A plain headline, three short points about what Quiet DNS does, and a Get started button. Get started opens the Add to Home Screen steps, numbered.
- **The dashboard shows only in the installed app.** Opened from the Home Screen icon, the home screen is the dashboard: the switch, the filter choice (Standard, Family or Unfiltered) and six links to the other screens. In a browser tab, the other screens open the Add to Home Screen steps instead.
- **Simpler dashboard.** The Filters page is gone. The filter choice on the home screen is the only place to choose what is blocked, and it sets the same two settings the page had. The three setup steps sit under the filter choice, and the links are ordered by need: Install, Help, Connection, Profile, Privacy, Settings. The fine print names only AdGuard.
- **Home-screen icon and logo.** The same wave as the website logo, in mint on a near-black square. The website's icon in the browser tab uses it too.
- **Save bar.** A bar at the bottom of the installed app shows "Unsaved" when settings differ from the last downloaded profile, with a Save button. Save downloads the profile, and iPhone asks you to install it. After Save, the bar says to open Settings, tap General, then VPN & Device Management. A web page can't open Settings on iPhone, so there is no link. After Save, the bar waits for Allow, and a Continue button opens the Install page. The page can't see whether Allow was tapped, so the person's tap on Continue is the confirmation. The Download button on the Profile page only downloads. Installing the profile is still a step in Settings, and a web page cannot change the iPhone's DNS settings itself.
- **Profile keys are hidden by default.** Settings > Show profile keys shows the key name under each setting.
- **No requests to other websites.** The site no longer loads Google Fonts. Schibsted Grotesk is served from the site's own folder, with its licence, and a test checks that the page loads nothing from another website.

- **Standard is marked as recommended**, and a change says the iPhone keeps its current setting until the profile is installed.
- **Save bar.** Discard appears beside Save when there is something to discard. The page leaves more room below the content, so the bar never covers the last line at large text sizes.

### Tests
- 80 automated tests, up from 54. New tests check that the site's version matches the newest changelog entry, that larger text scales the whole site, and that the resolver check builds its query and reads replies correctly.
- 67 automated tests at the last release check. Among them, every profile uses PayloadVersion 1 and that other versions are rejected, that the page loads nothing from another website, that the bundled font ships with its licence, that the page runs under a strict policy with no inline scripts, that every picture has alt text and no photo details, that the page never links to Settings by URL, that the home-screen icons have no transparency, and that the icon and the page draw the same logo.

## 2.2.0

### Changed
- **New website design.** The site is now an iPhone-style home screen: a status widget that turns solid teal when Quiet DNS is on, and a grid of six app tiles (Filters, Connection, Profile, Install, Privacy, Settings). Each tile opens its own screen.
- **Settings screen.** Website preferences: appearance (System, Light or Dark) and whether profile keys are shown. They are remembered in the browser and don't change the profile.
- **WireGuard screen removed from the site.** The `wg` command is unchanged, and the steps are still in `docs/wireguard.md`.
- **Screens are real links.** Each tile and the Back link is a plain `#anchor`, and focus moves to the new screen's title. Screen readers announce the change.
- **Files split.** `site/` now holds `index.html`, `site.css`, `core.js` (profile builder, unchanged in behaviour) and `app.js` (screens and settings).
- **Filters and connection rows** are full-width tap targets, and each shows the iPhone profile key it changes.

### Added
- A home-screen install: a web app manifest, an iOS home-screen icon (180 px) and two larger icons, generated by `scripts/make_icons.py`.
- Tests for the home-screen assets: manifest and icon sizes, the home-screen link, and that every in-page link points at a real screen.

### Tests
- 54 automated tests, up from 50.

## 2.1.0

### Changed
- **One Quiet DNS entry.** Every profile now has the name "Quiet DNS", with the same identifier and UUID. A new download is meant to edit the entry already on the iPhone instead of adding another. Not yet confirmed on a device.
- **Pause replaces the turn-off profile.** Turning Quiet DNS off builds a paused profile. It keeps the DNS settings and adds an `OnDemandRules` rule that disconnects them, so resuming only means installing the normal profile again. Experimental and untested on a device.
- **Website redesign.** Settings are grouped into Quiet DNS, Filtering and Connection, each with a plain-language description and the iPhone profile key it changes. A profile panel shows the resolver, protocol and status, and sits beside the settings on wide screens. Install, change and pause steps are on the page.
- **Presets.** `Quiet-DNS-Off.mobileconfig` is replaced by `Quiet-DNS-Paused.mobileconfig`.
- **Browser builder.** The website builds the same paused profile as the command line, and the parity test covers all 64 combinations.

### Removed
- The "Quiet DNS (Off)" profile name and the empty turn-off profile.

### Tests
- 50 automated tests, up from 47. New tests cover the pause rule, the single identity, and the checker catching a changed pause rule.

### Upgrading from 2.0
- Profiles from 2.0 use the same identifier and UUID, so installing a 2.1 profile should replace them. Check that only one Quiet DNS entry is listed afterwards.

## 2.0.0

Rebuilt as a project. See [docs/audit.md](docs/audit.md) for the full list.

### Added
- A website with a toggle for each setting. It builds the profile in the browser.
- Settings for DNS over TLS, adult blocking with safe search, failover, and AdGuard's IP addresses.
- A turn-off profile, which is experimental. Replaced by pausing in 2.1.0.
- The `wg` command, which points a WireGuard config's DNS at AdGuard DNS.
- A command-line interface: `presets`, `profile`, and `wg`.
- Optional signing with your own certificate.
- Tests: 47 automated tests, including a check that the website and the command line build identical profiles.
- Documentation for installing on iPhone, the settings, WireGuard, and security.

### Changed
- All profiles share one identifier and UUID, so installing one replaces the other.
- The install text is generated from the settings.
- The default version is the current time, so each new build replaces the one before it.

### Fixed
- The version check could never fail.
- Bootstrap addresses weren't checked against their resolver.
- A failed build could leave stale profiles in the output folder.
- Signing changed line endings, so the signed content differed from the built content.
- Signing failures printed tracebacks and could leave partial files.
- A docstring claimed all profiles used the same DNS server.

### Upgrading from 1.x
- Standard keeps the same identifiers and UUIDs as version 1, so installing it updates the existing profile.
- Family and Unfiltered from 1.x used different identifiers. Remove them before installing a 2.0 profile.

## 1.0.0

The first generator, which built Standard, Family, and Unfiltered profiles from one script.
