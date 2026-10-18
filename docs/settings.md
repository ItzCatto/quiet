# Settings

Each setting maps to one part of the iPhone profile. The website shows the same mapping next to each control, and the command line takes the same options.

| Setting | Website | Command line | What the profile does |
|---|---|---|---|
| Quiet DNS on | Quiet DNS switch | (default) / `--off` | On: includes the DNS settings. Off: builds a paused profile. It keeps the DNS settings and adds a rule (`OnDemandRules`: `Disconnect`) that tells iPhone not to use them. |
| Block ads and trackers | Part of the Filter | (default) / `--no-ads` | Without options: AdGuard DNS Standard, which blocks ads and trackers. With `--no-ads`: AdGuard DNS Unfiltered. |
| Block adult sites and turn on safe search | Part of the Filter | `--adult` | AdGuard DNS Family. Ad and tracker blocking is included. |
| Use DNS over TLS | Use DNS over TLS… | `--tls` | Sets `DNSProtocol` to `TLS` with `ServerName`, on port 853, instead of HTTPS. |
| Include the resolver's IP addresses | Include the resolver's IP addresses | (default) / `--no-bootstrap` | Adds `ServerAddresses`, so the device can reach the resolver before DNS switches. |
| Fall back when the resolver is unreachable | Fall back to your network's DNS… | `--failover` | Sets `AllowFailover`. Lookups that fall back are not encrypted. iOS and macOS 26 or later. |

## Filters

There are three filters, all from AdGuard DNS. The addresses and what each one blocks are in [resolvers.md](resolvers.md).

| Key | Filter | DNS over TLS |
|---|---|---|
| `default` | Standard | Yes |
| `family` | Family | Yes |
| `unfiltered` | Unfiltered | Yes |

`wg --mode` takes these keys.

## Rules that apply to every combination

- `--adult` always uses the Family filter, which also blocks ads and trackers. So `--adult --no-ads` gives the Family filter, not Unfiltered.
- The profile name is always **Quiet DNS**. Only the settings change, so every download updates the same entry on your iPhone.
- The install screen's text is generated from your settings, so it always describes what the profile does. A paused profile says so.
- Settings can be changed while Quiet DNS is paused. They take effect when you install the active profile again.

## Known trade-offs

**Pausing is experimental.** Pausing depends on iOS honoring the `Disconnect` rule on the DNS settings, and on a profile with the same identity replacing the one installed. Neither has been verified on a device. If lookups still go through your resolver while paused, remove the profile.

**Local network names.** The encrypted resolver can't see your home or office network, so names such as a router's hostname or a NAS's name may stop resolving while Quiet DNS is on. Apple's on-demand rules can exclude local names. This project doesn't use them yet, because a wrong rule could quietly turn the DNS settings off, and this hasn't been tested on a device. It is the next thing to test.

**Failover.** The default keeps every lookup encrypted. If the resolver can't be reached, lookups fail. Turning on the fallback keeps the internet working during an outage, but those lookups go to your network's DNS without encryption or filtering.

**Port 853.** Some networks block DNS over TLS. Keep HTTPS unless you need TLS.

**DNS can't block everything.** An ad served from the same domain as the content gets through, such as an ad inside a YouTube video.

**Settings can't be changed in iPhone Settings.** To change a setting, download a new profile and install it. The same entry is updated.
