# Resolvers and filters

Quiet DNS offers thirteen choices from three providers: AdGuard DNS, DNS4EU and Control D. This page gives the source of each one, what it blocks, and what is left out. Everything here was checked on **16 October 2026** against the providers' published pages. Run `python3 -m quiet resolvers` on your computer for the same list.

The key in the first column is what `--resolver` and `wg --mode` take.

## AdGuard DNS

| Key | Filter | What it blocks | HTTPS address | DNS over TLS |
|---|---|---|---|---|
| `default` | Standard | Ads, trackers and phishing sites | `https://dns.adguard-dns.com/dns-query` | `dns.adguard-dns.com` |
| `family` | Family | Ads, trackers, phishing sites and adult websites. Safe search is turned on. | `https://family.adguard-dns.com/dns-query` | `family.adguard-dns.com` |
| `unfiltered` | Unfiltered | Nothing | `https://unfiltered.adguard-dns.com/dns-query` | `unfiltered.adguard-dns.com` |

## DNS4EU

| Key | Filter | What it blocks | HTTPS address | DNS over TLS |
|---|---|---|---|---|
| `dns4eu-protective` | Security only | Malware, phishing and command-and-control domains. Not ads or trackers. | `https://protective.joindns4.eu/dns-query` | `protective.joindns4.eu` |
| `dns4eu-child` | Child protection | Malware, phishing and content not suitable for children. Not ads or trackers. | `https://child.joindns4.eu/dns-query` | `child.joindns4.eu` |
| `dns4eu-noads` | Ads and trackers | Malware, phishing, ads and trackers | `https://noads.joindns4.eu/dns-query` | `noads.joindns4.eu` |
| `dns4eu-child-noads` | Ads, trackers and child protection | Malware, phishing, ads, trackers and content not suitable for children | `https://child-noads.joindns4.eu/dns-query` | `child-noads.joindns4.eu` |
| `dns4eu-unfiltered` | Unfiltered | No content filtering | `https://unfiltered.joindns4.eu/dns-query` | `unfiltered.joindns4.eu` |

## Control D

Control D's free DNS needs no account. Its page lists an HTTPS address for each filter and a hostname it doesn't label as DNS over TLS, so these filters are offered over HTTPS only.

| Key | Filter | What it blocks | HTTPS address | DNS over TLS |
|---|---|---|---|---|
| `controld-ads` | Ads and tracking | Ads and tracking domains | `https://freedns.controld.com/p2` | Not published |
| `controld-hagezi-normal` | Hagezi Normal | Ads, trackers and telemetry, with rare and minor restrictions | `https://freedns.controld.com/x-hagezi-normal` | Not published |
| `controld-hagezi-pro` | Hagezi Pro | More ads, trackers and crash and error reporters, with uncommon restrictions | `https://freedns.controld.com/x-hagezi-pro` | Not published |
| `controld-hagezi-proplus` | Hagezi Pro Plus | Nearly all device trackers and some referral domains. May cause some restrictions and false positives. | `https://freedns.controld.com/x-hagezi-proplus` | Not published |
| `controld-hagezi-ultimate` | Hagezi Ultimate | Every device tracker, including location and IP trackers. Some apps and sites may stop working, such as some Facebook and Messenger features. | `https://freedns.controld.com/x-hagezi-ultimate` | Not published |

The four Hagezi filters are Hagezi's blocklist tiers, offered through Control D. Hagezi's tiers are described in the sources below. The Ads and tracking filter is described by Control D only briefly, so ask Control D for its full list if you need one.

Hagezi's Light tier isn't offered, so Normal is the least strict Hagezi choice here.

## Sources

- **AdGuard DNS:** [adguard-dns.io/en/public-dns.html](https://adguard-dns.io/en/public-dns.html). The addresses and hostnames are unchanged from version 2.3.0. This release did not re-read the page, so the weekly check is the ongoing test.
- **DNS4EU:** [joindns4.eu/for-public](https://www.joindns4.eu/for-public). Its page lists the addresses for each filter. The published IPv4 addresses are the only ones it gives, so the DNS4EU filters have no IPv6 bootstrap addresses. DNS4EU applies court-ordered domain blocks to its filters, including the unfiltered one.
- **Control D:** [docs.controld.com/docs/free-dns](https://docs.controld.com/docs/free-dns). Source of the HTTPS addresses, the IP addresses, and the no-account rule.
- **Hagezi:** the blocklist project is at [github.com/hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists). The tier descriptions above come from its FAQ, read through a mirror at [hagezi-mirror.dnsbunker.org/assets/dns-blocklists/faq.html](https://hagezi-mirror.dnsbunker.org/assets/dns-blocklists/faq.html).
- **Mullvad:** [mullvad.net/da/help/dns-over-https-and-dns-over-tls](https://mullvad.net/da/help/dns-over-https-and-dns-over-tls). It says: "Please note that the public encrypted DNS service will be discontinued on November 2, 2026." Mullvad is left out for that reason.

## What is left out, and why

- **Mullvad.** Its public DNS is discontinued on 2 November 2026, so a profile for it would stop working soon after this release.
- **Account-based resolvers, such as NextDNS.** They need an account ID for each profile. Quiet DNS would have to write that ID into a file you install and may share, so only resolvers that need no account are offered.
- **Hagezi Light.** Not offered. See above.

## Limits of DNS blocking

- **DNS works on names, not on what a page shows.** An ad served from the same domain as the content gets through. Ads inside YouTube videos are an example.
- **Apps that use their own DNS** instead of the iPhone's may not be affected by these settings.
- **Blocklists change.** The providers update their lists on their own schedule. This page records what they said on the date above, not what they block today.
- **Stricter filters can break things.** Hagezi Pro Plus can cause false positives. Hagezi Ultimate can stop some apps and sites from working.
- **Nothing here has been tested on an iPhone.** The weekly check confirms that the resolvers answer. It does not test what they block.

## How the weekly check works

`.github/workflows/resolver-check.yml` runs `scripts/check_resolvers.py` every Monday. For each resolver it asks the HTTPS address, and the DNS over TLS address where one is published, for the address of `example.com`. It also tries a connection to each IP address the profiles include. The only name it looks up is `example.com`.

A failed required check fails the run, and GitHub emails the repository owner. IPv6 failures are reported but don't fail the run, because not every network has IPv6.
