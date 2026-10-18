# Settings

Each setting maps to one part of the iPhone profile. The website shows the same mapping next to each control, and the command line takes the same options.

| Setting | Website | Command line | What the profile does |
|---|---|---|---|
| Quiet DNS on | Quiet DNS switch | (default) / `--off` | On: includes the DNS settings. Off: builds a paused profile. It keeps the DNS settings and adds a rule (`OnDemandRules`: `Disconnect`) that tells iPhone not to use them. |
| Filter | Filter list | `--resolver KEY` | Chooses one resolver and filter from the eight in [resolvers.md](resolvers.md). Without this option, the two rows below choose one. |
| Block ads and trackers | Part of the Filter list | (default) / `--no-ads` | Without `--resolver`: AdGuard DNS Standard blocks ads and trackers. With `--no-ads`: AdGuard DNS Unfiltered. |
| Block adult sites and turn on safe search | Part of the Filter list | `--adult` | Without `--resolver`: AdGuard DNS Family. Ad and tracker blocking is included. |
| Use DNS over TLS | Use DNS over TLS… | `--tls` | Sets `DNSProtocol` to `TLS` with `ServerName`, on port 853, instead of HTTPS. Only filters that publish a DNS over TLS hostname offer it. The website turns the switch off for the others, and the command line refuses `--tls` for them. |
| Include the resolver's IP addresses | Include the resolver's IP addresses | (default) / `--no-bootstrap` | Adds `ServerAddresses`, so the device can reach the resolver before DNS switches. |
| Fall back when the resolver is unreachable | Fall back to your network's DNS… | `--failover` | Sets `AllowFailover`. Lookups that fall back are not encrypted. iOS and macOS 26 or later. |

## Resolver keys

Each key names one resolver and filter. Run `python3 -m quiet resolvers` for the addresses and what each one blocks, or see [resolvers.md](resolvers.md).

| Key | Provider and filter | DNS over TLS |
|---|---|---|
| `default` | AdGuard DNS Standard | Yes |
| `family` | AdGuard DNS Family | Yes |
| `unfiltered` | AdGuard DNS Unfiltered | Yes |
| `controld-ads` | Control D Ads and tracking | No, HTTPS only |
| `controld-hagezi-normal` | Control D Hagezi Normal | No, HTTPS only |
| `controld-hagezi-pro` | Control D Hagezi Pro | No, HTTPS only |
| `controld-hagezi-proplus` | Control D Hagezi Pro Plus | No, HTTPS only |
| `controld-hagezi-ultimate` | Control D Hagezi Ultimate | No, HTTPS only |

## Rules that apply to every combination

- A named resolver decides what is blocked. `--resolver` can't be combined with `--no-ads` or `--adult`, and the command line refuses both together.
- The profile name is always **Quiet DNS**. Only the settings change, so every download updates the same entry on your iPhone.
- The install screen's text is generated from your settings, so it always describes what the profile does. A paused profile says so.
- Settings can be changed while Quiet DNS is paused. They take effect when you install the active profile again.

## Known trade-offs

**Pausing is experimental.** Pausing depends on iOS honoring the `Disconnect` rule on the DNS settings, and on a profile with the same identity replacing the one installed. Neither has been verified on a device. If lookups still go through your resolver while paused, remove the profile.

**Local network names.** The encrypted resolver can't see your home or office network, so names such as a router's hostname or a NAS's name may stop resolving while Quiet DNS is on. Apple's on-demand rules can exclude local names. This project doesn't use them yet, because a wrong rule could quietly turn the DNS settings off, and this hasn't been tested on a device. It is the next thing to test.

**Failover.** The default keeps every lookup encrypted. If the resolver can't be reached, lookups fail. Turning on the fallback keeps the internet working during an outage, but those lookups go to your network's DNS without encryption or filtering.

**Port 853.** Some networks block DNS over TLS. Keep HTTPS unless you need TLS.

**Stricter filters can break things.** Hagezi Pro Plus can cause some false positives. Hagezi Ultimate can stop some apps and sites from working, such as some Facebook and Messenger features.

**DNS can't block everything.** An ad served from the same domain as the content gets through, such as an ad inside a YouTube video.

**Settings can't be changed in iPhone Settings.** To change a setting, download a new profile and install it. The same entry is updated.
