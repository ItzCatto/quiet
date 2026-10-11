# Settings

Each setting maps to one part of the iPhone profile. The website shows the same mapping next to each toggle, and the command line takes the same options.

| Setting | Website toggle | Command line | What the profile does |
|---|---|---|---|
| Quiet DNS on | Quiet DNS switch | (default) / `--off` | On: includes the DNS settings. Off: builds a paused profile. It keeps the DNS settings and adds a rule (`OnDemandRules`: `Disconnect`) that tells iPhone not to use them. |
| Block ads and trackers | Block ads and trackers | (default) / `--no-ads` | Uses AdGuard's default resolver `dns.adguard-dns.com`, or the unfiltered one. |
| Block adult sites and turn on safe search | Block adult sites… | `--adult` | Uses AdGuard's family resolver `family.adguard-dns.com`. Ad and tracker blocking is always included. |
| Use DNS over TLS | Use DNS over TLS… | `--tls` | Sets `DNSProtocol` to `TLS` with `ServerName`, on port 853, instead of HTTPS. |
| AdGuard's IP addresses | Include AdGuard's IP addresses | (default) / `--no-bootstrap` | Adds `ServerAddresses`, so the device can reach the resolver before DNS switches. |
| Fallback when AdGuard is unreachable | Fall back to your network's DNS… | `--failover` | Sets `AllowFailover`. Lookups that fall back are not encrypted. iOS and macOS 26 or later. |

## Resolvers

| Resolver | Encrypted (HTTPS) | Encrypted (TLS) | Blocks |
|---|---|---|---|
| Default | `https://dns.adguard-dns.com/dns-query` | `dns.adguard-dns.com` | Ads, trackers, phishing |
| Family | `https://family.adguard-dns.com/dns-query` | `family.adguard-dns.com` | Ads, trackers, phishing, and adult websites. Safe search is turned on. |
| Unfiltered | `https://unfiltered.adguard-dns.com/dns-query` | `unfiltered.adguard-dns.com` | Nothing |

The IP addresses for each resolver come from AdGuard's public DNS page. The full list is in `quiet/settings.py`.

## Rules that apply to every combination

- Adult blocking always includes ad and tracker blocking, because AdGuard's family resolver does. The website locks the ads toggle on while adult blocking is on.
- The profile name is always **Quiet DNS**. Only the settings change, so every download updates the same entry on your iPhone.
- The install screen's text is generated from your settings, so it always describes what the profile does. A paused profile says so.
- Settings can be changed while Quiet DNS is paused. They take effect when you install the active profile again.

## Known trade-offs

**Pausing is experimental.** Pausing depends on iOS honoring the `Disconnect` rule on the DNS settings, and on a profile with the same identity replacing the one installed. Neither has been verified on a device. If lookups still go through AdGuard while paused, remove the profile.

**Local network names.** The encrypted resolver can't see your home or office network, so names such as a router's hostname or a NAS's name may stop resolving while Quiet DNS is on. Apple's on-demand rules can exclude local names. This project doesn't use them yet, because a wrong rule could quietly turn the DNS settings off, and this hasn't been tested on a device. It is the next thing to test.

**Failover.** The default keeps every lookup encrypted. If AdGuard can't be reached, lookups fail. Turning on the fallback keeps the internet working during an AdGuard outage, but those lookups go to your network's DNS without encryption or filtering.

**Port 853.** Some networks block DNS over TLS. Keep HTTPS unless you need TLS.

**Settings can't be changed in iPhone Settings.** To change a setting, download a new profile and install it. The same entry is updated.
