# Install, change, pause and remove Quiet DNS on iPhone

Quiet DNS works through one configuration profile. It shows up as one entry, named **Quiet DNS**, in Settings. iPhone has no switch for DNS profiles, so every change goes through that entry: installing a new profile updates it, pausing sets it to a paused state, and removing it turns Quiet DNS off completely.

## Install

1. Download the profile from the website, or AirDrop the `.mobileconfig` file to your iPhone.
2. When Safari asks to download a configuration profile, tap **Allow**.
3. Open **Settings**, tap **General**, then tap **VPN & Device Management**. **Quiet DNS** is listed there.
4. Tap **Install**, enter your passcode, tap **Install** again, then tap **Done**.
5. Check it worked. **Settings › General › VPN & Device Management** should list **Quiet DNS**. A Quiet DNS icon should also appear on your Home Screen. Open it from there. This is new in 2.3.0 and isn't tested on a phone yet.

If you installed Family or Unfiltered profiles from version 1, remove them first. Version 1 used different identifiers, so the new profile can't replace them.

## Check that it's working

- Load a page that normally shows many ads. Most of them should be gone.
- Open a DNS test site in Safari. Its report should show the resolver you chose, such as AdGuard DNS or DNS4EU.
- Check a local name, such as your router's address or a printer's name. If it stops resolving, see [settings.md](settings.md).

## Change a setting

Change the settings on the website, download the profile again, and install it the same way. The new profile has the same name and identity as the one on your iPhone, so it should update that entry instead of adding another. Afterwards, check that only one Quiet DNS entry is listed.

This has not been tested on a device yet. Check the entry after the first change.

## Pause (experimental)

1. On the website, turn the Quiet DNS switch off. The button changes to **Download paused profile**.
2. Download it and install it the same way.
3. The paused profile keeps your settings, so it's ready when you resume. It also tells iPhone not to use them, so lookups should go to your network's normal DNS.
4. Check your DNS afterwards with a DNS test site. If it still shows your resolver, remove the profile (see below).

## Resume

Turn the Quiet DNS switch back on, download the profile, and install it. It replaces the paused entry with the active one.

## Remove (always works)

1. Open **Settings › General › VPN & Device Management**.
2. Tap **Quiet DNS**, then **Remove Profile**.

Removing the profile turns Quiet DNS off completely, and iPhone goes back to your network's DNS.

## Troubleshooting

- **Two Quiet DNS entries are listed.** Remove both, then install the profile once.
- **Lookups still go through your resolver after pausing.** The paused profile may not work on your iPhone yet. Remove the profile to stop Quiet DNS.
- **No internet after installing.** Remove the profile. If the resolver is unreachable, the device can't resolve names, unless you turned on the fallback setting. Removing the profile restores your network's DNS.
- **Safari doesn't offer to install the profile.** Make sure you downloaded it from a normal web host, not a preview. Otherwise AirDrop the file from a Mac.
- **iPhone says the profile is "Not Signed".** That's expected for the included profiles, which aren't signed with a certificate. A signature changes the label only if iPhone trusts the certificate. For free signing on your own iPhone, see [security.md](security.md).
- **You installed a version 2.0 turn-off profile.** It has no DNS settings. Installing a current profile should replace it. Check that only one entry is listed.
