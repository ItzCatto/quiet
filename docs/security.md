# Security and privacy

## What a profile contains

A Quiet DNS profile is a plain XML file. Nothing in it is secret. It names a resolver, optionally some IP addresses, and the text shown at install. You can read the profile before you install it: the Profile screen has a "Profile file" section, and the file opens in any text editor.

The profile never includes a WireGuard config, a private key, or your account details.

## What the website does

- It builds the profile in your browser from the toggles. It has no server-side code. It keeps only your theme and the last settings you saved, in this browser.
- It has no file upload, so there's no way to send it a config or a key. A test checks that the page has no file input.
- It loads nothing from other websites, and a test checks that too.

## Who sees your DNS lookups

When Quiet DNS is on, AdGuard DNS sees the domain names your iPhone looks up. Your network provider can no longer see those names, but it can still see that your device connects to AdGuard. Read AdGuard's privacy policy before relying on it.

While Quiet DNS is paused, lookups are meant to go to your network's normal DNS, so your network can see the domain names again. The paused profile still contains the DNS settings. It only tells iPhone not to use them.

Turning on the failover setting sends lookups to your network's DNS if AdGuard can't be reached. Those lookups are not encrypted.

## Removal

Every profile can be removed at any time. The profiles set `PayloadRemovalDisallowed` to false, so the person who installed a profile can always remove it, and Quiet doesn't lock anyone in.

## Signing

The included profiles are unsigned, so iPhone shows an "Unsigned" warning during install. You can sign them with your own certificate:

```
python3 -m quiet presets --sign cert.pem key.pem --chain chain.pem
```

Signing shows who made the profile. It doesn't make the profile safer or change what it does. Keep your private key safe. Anyone who has it can sign profiles that look like yours.

## Keys and secrets in this project

- `.gitignore` excludes `*.conf`, `*.pem`, `*.key`, and `dist/`.
- The WireGuard command refuses to write into the project folder.
- The tests use placeholder keys that look nothing like real ones.

## Not affiliated

Quiet is not affiliated with AdGuard or Proton. The names are used only to say which services the profiles connect to.
