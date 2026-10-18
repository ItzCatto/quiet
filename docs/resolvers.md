# Filters

Quiet DNS offers three filters, all from AdGuard DNS: Standard, Family and Unfiltered. This page gives the address of each one, what it blocks, and what is left out. The addresses are the ones AdGuard DNS publishes for its public DNS, which needs no account.

The key in the first column is what `wg --mode` takes.

## AdGuard DNS

| Key | Filter | What it blocks | HTTPS address | DNS over TLS |
|---|---|---|---|---|
| `default` | Standard | Ads, trackers and phishing sites | `https://dns.adguard-dns.com/dns-query` | `dns.adguard-dns.com` |
| `family` | Family | Ads, trackers, phishing sites and adult websites. Safe search is turned on. | `https://family.adguard-dns.com/dns-query` | `family.adguard-dns.com` |
| `unfiltered` | Unfiltered | Nothing | `https://unfiltered.adguard-dns.com/dns-query` | `unfiltered.adguard-dns.com` |

## Sources

- **AdGuard DNS:** [adguard-dns.io/en/public-dns.html](https://adguard-dns.io/en/public-dns.html). The addresses and hostnames are the same as in version 2.3.0. This release did not re-read the page, so the weekly check is the ongoing test.
- **Mullvad:** [mullvad.net/da/help/dns-over-https-and-dns-over-tls](https://mullvad.net/da/help/dns-over-https-and-dns-over-tls). It says: "Please note that the public encrypted DNS service will be discontinued on November 2, 2026." Mullvad is left out for that reason.

## What is left out, and why

- **Mullvad.** Its public DNS is discontinued on 2 November 2026, so a profile for it would stop working soon after this release.
- **Account-based resolvers, such as NextDNS.** They need an account ID for each profile. Quiet DNS would have to write that ID into a file you install and may share, so only resolvers that need no account are offered.

## Limits of DNS blocking

- **DNS works on names, not on what a page shows.** An ad served from the same domain as the content gets through. Ads inside YouTube videos are an example.
- **Apps that use their own DNS** instead of the iPhone's may not be affected by these settings.
- **Blocklists change.** AdGuard DNS updates its filters on its own schedule. This page describes what each filter is meant to block, not every domain it blocks today.
- **Nothing here has been tested on an iPhone.** The weekly check confirms that the resolvers answer. It does not test what they block.

## How the weekly check works

`.github/workflows/resolver-check.yml` runs `scripts/check_resolvers.py` every Monday. For each filter it asks the HTTPS address, and the DNS over TLS address, for the address of `example.com`. It also tries a connection to each IP address the profiles include. The only name it looks up is `example.com`.

A failed required check fails the run, and GitHub emails the repository owner. IPv6 failures are reported but don't fail the run, because not every network has IPv6.
