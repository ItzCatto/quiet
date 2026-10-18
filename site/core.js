/* Quiet DNS profile builder. This must match quiet/profiles.py exactly; tests/test_site_parity.py checks it
   against the Python builder for all 64 combinations of settings. */
var QuietCore = (function () {
  // Generated from quiet/settings.py. tests/test_site_parity.py checks it matches.
  var RESOLVERS = {
    "default": {
      "provider": "AdGuard DNS",
      "name": "Standard",
      "file": "Standard",
      "blocks": "blocks ads, trackers and phishing sites",
      "note": "Recommended for most people.",
      "doh": "https://dns.adguard-dns.com/dns-query",
      "dot": "dns.adguard-dns.com",
      "ipv4": [
        "94.140.14.14",
        "94.140.15.15"
      ],
      "ipv6": [
        "2a10:50c0::ad1:ff",
        "2a10:50c0::ad2:ff"
      ]
    },
    "family": {
      "provider": "AdGuard DNS",
      "name": "Family",
      "file": "Family",
      "blocks": "blocks ads, trackers, phishing sites and adult websites, and turns on safe search",
      "note": "",
      "doh": "https://family.adguard-dns.com/dns-query",
      "dot": "family.adguard-dns.com",
      "ipv4": [
        "94.140.14.15",
        "94.140.15.16"
      ],
      "ipv6": [
        "2a10:50c0::bad1:ff",
        "2a10:50c0::bad2:ff"
      ]
    },
    "unfiltered": {
      "provider": "AdGuard DNS",
      "name": "Unfiltered",
      "file": "Unfiltered",
      "blocks": "does not block ads or trackers",
      "note": "Lookups are still encrypted.",
      "doh": "https://unfiltered.adguard-dns.com/dns-query",
      "dot": "unfiltered.adguard-dns.com",
      "ipv4": [
        "94.140.14.140",
        "94.140.14.141"
      ],
      "ipv6": [
        "2a10:50c0::1:ff",
        "2a10:50c0::2:ff"
      ]
    },
    "controld-ads": {
      "provider": "Control D",
      "name": "Ads and tracking",
      "file": "ControlD-Ads",
      "blocks": "blocks ads and tracking domains",
      "note": "",
      "doh": "https://freedns.controld.com/p2",
      "dot": null,
      "ipv4": [
        "76.76.2.2",
        "76.76.10.2"
      ],
      "ipv6": [
        "2606:1a40::2",
        "2606:1a40:1::2"
      ]
    },
    "controld-hagezi-normal": {
      "provider": "Control D",
      "name": "Hagezi Normal",
      "file": "ControlD-Hagezi-Normal",
      "blocks": "blocks ads, trackers and telemetry, with rare and minor restrictions",
      "note": "",
      "doh": "https://freedns.controld.com/x-hagezi-normal",
      "dot": null,
      "ipv4": [
        "76.76.2.40",
        "76.76.10.40"
      ],
      "ipv6": [
        "2606:1a40::40",
        "2606:1a40:1::40"
      ]
    },
    "controld-hagezi-pro": {
      "provider": "Control D",
      "name": "Hagezi Pro",
      "file": "ControlD-Hagezi-Pro",
      "blocks": "blocks more ads, trackers and crash reporters, with uncommon restrictions",
      "note": "",
      "doh": "https://freedns.controld.com/x-hagezi-pro",
      "dot": null,
      "ipv4": [
        "76.76.2.41",
        "76.76.10.41"
      ],
      "ipv6": [
        "2606:1a40::41",
        "2606:1a40:1::41"
      ]
    },
    "controld-hagezi-proplus": {
      "provider": "Control D",
      "name": "Hagezi Pro Plus",
      "file": "ControlD-Hagezi-ProPlus",
      "blocks": "blocks nearly all device trackers and some referral domains",
      "note": "May cause some restrictions and false positives.",
      "doh": "https://freedns.controld.com/x-hagezi-proplus",
      "dot": null,
      "ipv4": [
        "76.76.2.42",
        "76.76.10.42"
      ],
      "ipv6": [
        "2606:1a40::42",
        "2606:1a40:1::42"
      ]
    },
    "controld-hagezi-ultimate": {
      "provider": "Control D",
      "name": "Hagezi Ultimate",
      "file": "ControlD-Hagezi-Ultimate",
      "blocks": "blocks every device tracker, including location and IP trackers",
      "note": "Meant for experienced users. Some apps and sites may stop working, such as some Facebook and Messenger features.",
      "doh": "https://freedns.controld.com/x-hagezi-ultimate",
      "dot": null,
      "ipv4": [
        "76.76.2.45",
        "76.76.10.45"
      ],
      "ipv6": [
        "2606:1a40::45",
        "2606:1a40:1::45"
      ]
    }
  };
  // Same identity for every setting, so a new download replaces the installed entry.
  var DISPLAY_NAME = "Quiet DNS";
  var SLOT = {
    profileId: "com.quiet.dns.profile",
    profileUuid: "A7C3E912-5B64-4D8F-A120-9E6B3F7C2045",
    dnsId: "com.quiet.dns.settings",
    dnsUuid: "F5D2B0C1-7A83-4E96-9B21-6C8D4F0A2E17"
  };
  var REMOVE_HINT = "You can remove this profile any time in Settings > General > VPN & Device Management.";
  var PAUSED_RULES = [{Action: "Disconnect"}];

  // The resolver these settings use. Without a named resolver, the two older toggles choose an AdGuard one.
  function resolverKey(s) {
    if (s.resolver && RESOLVERS[s.resolver]) { return s.resolver; }
    if (s.block_adult) { return "family"; }
    if (s.block_ads !== false) { return "default"; }
    return "unfiltered";
  }

  function profileName() {
    return DISPLAY_NAME;
  }

  function summary(s) {
    if (!s.enabled) {
      return "Paused. Lookups use your network's normal DNS until Quiet DNS is turned back on.";
    }
    var r = RESOLVERS[resolverKey(s)];
    return "Encrypted DNS through " + r.provider + ". It " + r.blocks + ".";
  }

  function consentText(s) {
    var text;
    if (!s.enabled) {
      text = "Quiet DNS is paused, so lookups from this device use your network's normal DNS. " +
        "Install Quiet DNS again to turn it back on.";
    } else {
      var r = RESOLVERS[resolverKey(s)];
      text = "Lookups from this device go over an encrypted connection to " + r.provider + ", which " +
        r.blocks + ". Your network can no longer see the domain names this device looks up, but " +
        r.provider + " can.";
      if (s.failover) {
        text += " If " + r.provider + " can't be reached, lookups fall back to your network's DNS, " +
          "which is not encrypted.";
      }
    }
    return text + " " + REMOVE_HINT;
  }

  // Same as profiles.PAYLOAD_VERSION. Every profile uses 1.
  var PAYLOAD_VERSION = 1;

  function dnsPayload(s) {
    var r = RESOLVERS[resolverKey(s)];
    if (s.use_tls && !r.dot) { throw new Error(r.provider + " " + r.name + " doesn't offer DNS over TLS."); }
    var dns = {DNSProtocol: s.use_tls ? "TLS" : "HTTPS"};
    if (s.use_tls) {
      dns.ServerName = r.dot;
    } else {
      dns.ServerURL = r.doh;
    }
    if (s.bootstrap_ips) { dns.ServerAddresses = r.ipv4.concat(r.ipv6); }
    if (s.failover) { dns.AllowFailover = true; }
    var payload = {
      DNSSettings: dns,
      PayloadDescription: summary(s),
      PayloadDisplayName: DISPLAY_NAME,
      PayloadIdentifier: SLOT.dnsId,
      PayloadType: "com.apple.dnsSettings.managed",
      PayloadUUID: SLOT.dnsUuid,
      PayloadVersion: PAYLOAD_VERSION
    };
    if (!s.enabled) {
      payload.OnDemandRules = PAUSED_RULES.map(function (rule) { return {Action: rule.Action}; });
    }
    return payload;
  }

  function buildProfile(s) {
    return {
      ConsentText: {"default": consentText(s)},
      PayloadContent: [dnsPayload(s)],
      PayloadDescription: summary(s),
      PayloadDisplayName: DISPLAY_NAME,
      PayloadIdentifier: SLOT.profileId,
      PayloadOrganization: "Quiet",
      PayloadRemovalDisallowed: false,
      PayloadScope: "System",
      PayloadType: "Configuration",
      PayloadUUID: SLOT.profileUuid,
      PayloadVersion: PAYLOAD_VERSION
    };
  }

  function esc(text) {
    return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function plistValue(v, depth) {
    var pad = new Array(depth + 1).join("\t");
    if (v === true) { return pad + "<true/>"; }
    if (v === false) { return pad + "<false/>"; }
    if (typeof v === "number") { return pad + "<integer>" + v + "</integer>"; }
    if (typeof v === "string") { return pad + "<string>" + esc(v) + "</string>"; }
    if (Array.isArray(v)) {
      if (!v.length) { return pad + "<array/>"; }
      return pad + "<array>\n" + v.map(function (x) { return plistValue(x, depth + 1); }).join("\n") + "\n" + pad + "</array>";
    }
    var keys = Object.keys(v);
    if (!keys.length) { return pad + "<dict/>"; }
    return pad + "<dict>\n" + keys.map(function (k) {
      return pad + "\t<key>" + esc(k) + "</key>\n" + plistValue(v[k], depth + 1);
    }).join("\n") + "\n" + pad + "</dict>";
  }

  function profileXML(s) {
    return '<?xml version="1.0" encoding="UTF-8"?>\n' +
      '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n' +
      '<plist version="1.0">\n' + plistValue(buildProfile(s), 0) + '\n</plist>\n';
  }

  return {
    RESOLVERS: RESOLVERS,
    resolverKey: resolverKey,
    profileName: profileName,
    summary: summary,
    consentText: consentText,
    buildProfile: buildProfile,
    profileXML: profileXML
  };
})();
