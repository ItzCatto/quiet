# Audit of the v1 profile generator

This audit covers the generator from the first version of Quiet DNS, which built three profiles from one script. Each finding below was either fixed in version 2 or listed as a limit.

## Bugs found and fixed

| # | Finding | Effect | Fix |
|---|---|---|---|
| 1 | The version check compared a value with the value it was built from. | The check could never fail. | Real checks now compare the profile and payload versions, and reject mismatches. Tested. |
| 2 | Bootstrap addresses weren't checked against the resolver. | A family URL with the default IPs would pass. | The checker maps each hostname to its resolver and rejects addresses from any other. Tested. |
| 3 | A failed build left files from an earlier run in the output folder. | Stale profiles could be shipped. | Every profile is built and checked in memory first. Nothing is written unless all pass. Tested. |
| 4 | Signing used OpenSSL's text mode. | Line endings changed (LF became CRLF), so the signed content differed from what was built. Found by the new round-trip test. | `-binary` keeps the bytes exact. Tested. |
| 5 | A signing failure printed a traceback and could leave a partial file. | Confusing errors, and partial output. | Friendly errors, and the partial file is removed. Tested. |
| 6 | The docstring said all profiles set the same DNS server. | Wrong: Family and Unfiltered use different resolvers. | Corrected. |
| 7 | Standard, Family, and Unfiltered used different identifiers. | Two Quiet DNS profiles could be installed at once, with unclear precedence. | All profiles share one identifier and UUID, so installing one replaces the other. Earlier Family and Unfiltered profiles need manual removal. |
| 8 | The install text was fixed for each file. | It would be wrong if settings changed. | The text is generated from the settings. Tested. |
| 9 | No tests. | Nothing guarded the output. | Automated tests were added: 47 in version 2.0, 50 in version 2.1, plus a browser check of the website. |

## Gaps closed

- No settings could be changed without editing code. Each setting is now a toggle on the website and an option on the command line.
- No way to turn Quiet DNS off. Version 2.0 added a turn-off profile. Version 2.1 replaces it with a pause that keeps the DNS settings in the profile. The pause is experimental.
- No DNS over TLS, and no failover option. Both are now available.
- No WireGuard integration. The `wg` command is new.

## Still open

- **Not tested on an iPhone or Mac.** The profiles pass structural checks against Apple's DNS settings schema, but installing them on a device is the real test. See [install-iphone.md](install-iphone.md).
- **The pause is experimental.** It relies on two things iOS has not been shown to do: honor a `Disconnect` on-demand rule on a DNS settings payload, and replace the installed entry when a profile with the same identity is installed. Neither has been verified on a device. Removing the profile always works.
- **One entry, edited in place** is the intended behaviour of the shared identity (see the changelog for 2.1). It is untested on a device.
- **Signing with a real certificate is untested.** The tests use a throwaway self-signed certificate.
- **Failover (`AllowFailover`)** follows Apple's schema, but its behaviour has not been observed on iOS 26.
- **Local-name exclusion** via on-demand rules is not included. See [settings.md](settings.md).
- **The WireGuard output** has not been imported into the WireGuard app.
