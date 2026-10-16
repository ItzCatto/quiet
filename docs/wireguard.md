# WireGuard integration

The `wg` command takes your own WireGuard config and writes a copy whose DNS points at a Quiet DNS resolver you choose. Everything else in the config stays the same. The tunnel itself is unchanged.

## Use it

Run this on your own computer, with your own config file:

```
python3 -m quiet wg ~/Downloads/your-tunnel.conf -o ~/Desktop/quiet-tunnel.conf
```

Choose a mode with `--mode`:

- `default` (the default): AdGuard DNS Standard, which blocks ads, trackers and phishing sites.
- `family`: AdGuard DNS Family, which also blocks adult sites and turns on safe search.
- `unfiltered`: AdGuard DNS Unfiltered, encrypted, with no filtering.
- Any other key from `python3 -m quiet resolvers`, such as `dns4eu-noads` or `controld-hagezi-pro`. [resolvers.md](resolvers.md) says what each one blocks.

The command prints the old DNS and the new DNS. It never prints the private key. The output file is readable only by your user account.

Then import the new file into the WireGuard app on your iPhone or Mac, the same way you added the original tunnel. I haven't tested the import, so check that the tunnel connects and that your DNS points at the resolver you chose.

## What it changes

It replaces the `DNS =` line in the `[Interface]` section with the chosen resolver's IPv4 and IPv6 addresses, and places that line directly after `Address =`. The DNS4EU filters publish IPv4 addresses only, so their line has IPv4 addresses alone. A config without a DNS line gets one. Keys are matched without regard to case, and comments are kept.

WireGuard's DNS setting takes IP addresses (and search domains), not DNS-over-HTTPS URLs, so the tunnel uses plain DNS to the resolver's IP addresses. That traffic is encrypted by the tunnel itself, not by DNS over HTTPS.

## Limits

- The original DNS in many providers' configs is the provider's own resolver. For Proton, this is `10.2.0.1`. Depending on your plan, that resolver can apply the provider's own filtering. Replacing it stops that filtering, so check whether you rely on it.
- Don't use the WireGuard tunnel and the Quiet DNS profile together without testing first. I haven't verified how iOS chooses between a tunnel's DNS and an installed DNS profile.
- The command refuses to write inside the project folder, so configs can't end up in the repository.

## Keep your config private

A WireGuard config contains a private key. Anyone with that file can use the tunnel as you. So:

- Never upload it to the website, put it in the repository, or send it in a chat.
- Keep the output file somewhere private. The command sets it to `600`, meaning only your account can read it.
- If a config was ever shared, generate a new key in your provider's dashboard and make a new config.
