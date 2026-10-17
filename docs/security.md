# Security and privacy

## What a profile contains

A Quiet DNS profile is a plain XML file. Nothing in it is secret. It names a resolver, optionally some IP addresses, and the text shown at install. You can read the profile before you install it: the Profile screen has a "Profile file" section, and the file opens in any text editor.

The profile never includes a WireGuard config, a private key, or your account details.

## What the website does

- It builds the profile in your browser from the toggles. It has no server-side code. It keeps only your theme and the last settings you saved, in this browser.
- It has no file upload, so there's no way to send it a config or a key. A test checks that the page has no file input.
- It loads nothing from other websites, and a test checks that too.

## Who sees your DNS lookups

When Quiet DNS is on, the resolver you chose sees the domain names your iPhone looks up. Your network provider can no longer see those names, but it can still see that your device connects to that resolver. Read the privacy policy of the provider you choose before relying on it. The provider links are in [resolvers.md](resolvers.md).

While Quiet DNS is paused, lookups are meant to go to your network's normal DNS, so your network can see the domain names again. The paused profile still contains the DNS settings. It only tells iPhone not to use them.

Turning on the failover setting sends lookups to your network's DNS if the resolver can't be reached. Those lookups are not encrypted.

## Removal

Every profile can be removed at any time. The profiles set `PayloadRemovalDisallowed` to false, so the person who installed a profile can always remove it, and Quiet doesn't lock anyone in.

## Signing

The included profiles are unsigned, so iPhone shows an "Unsigned" warning during install. You can sign them with your own certificate:

```
python3 -m quiet presets --sign cert.pem key.pem --chain chain.pem
```

Signing shows who made the profile. It doesn't make the profile safer or change what it does. Keep your private key safe. Anyone who has it can sign profiles that look like yours.

### Free signing for your own iPhone

A certificate from a trusted authority costs money. Apple's developer membership is $99 a year, and it's the usual way to get a certificate that iPhone trusts for everyone. You don't need either to sign profiles for your own iPhone. You can make a signing certificate yourself and install it as trusted on that phone:

1. On your computer, run `python3 scripts/make_signing_identity.py`. It writes `key.pem`, `cert.pem` and `trust-on-iphone.mobileconfig` to `~/quiet-signing`, outside the project. The key is never written into the project folder.
2. AirDrop `trust-on-iphone.mobileconfig` to your iPhone and open it. Then go to Settings, Downloaded Profile, and tap Install. iPhone warns that the profile isn't signed. That warning is expected for this profile.
3. Go to Settings, General, About, Certificate Trust Settings, and turn on the entry for your name, if it's listed.
4. From the project folder, sign the profiles: `python3 -m quiet presets --sign ~/quiet-signing/cert.pem ~/quiet-signing/key.pem`.

Profiles you sign then show your name as the signer on iPhones where you installed the trust profile. On any other iPhone they show "Not Verified". The certificate lasts two years by default. Keep `key.pem` private, and back it up somewhere safe. If you lose it, you can't sign new profiles that your phone trusts.

The helper is tested on a computer, not on an iPhone. The trust step on your phone is the part to check. If iPhone doesn't show the entry in Certificate Trust Settings, the profile may still install, but the signature won't show as trusted.

## Keys and secrets in this project

- `.gitignore` excludes `*.conf`, `*.pem`, `*.key`, and `dist/`.
- The WireGuard command refuses to write into the project folder.
- The tests use placeholder keys that look nothing like real ones.

## Not affiliated

Quiet is not affiliated with AdGuard, DNS4EU, Control D, Hagezi or Proton. The names are used only to say which services the profiles connect to.
