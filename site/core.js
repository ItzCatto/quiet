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
    "dns4eu-protective": {
      "provider": "DNS4EU",
      "name": "Security only",
      "file": "DNS4EU-Security",
      "blocks": "blocks malware, phishing and command-and-control domains, but not ads or trackers",
      "note": "Court-ordered domain blocks still apply.",
      "doh": "https://protective.joindns4.eu/dns-query",
      "dot": "protective.joindns4.eu",
      "ipv4": [
        "86.54.11.1",
        "86.54.11.201"
      ],
      "ipv6": []
    },
    "dns4eu-child": {
      "provider": "DNS4EU",
      "name": "Child protection",
      "file": "DNS4EU-Child",
      "blocks": "blocks malware, phishing and content not suitable for children, but not ads or trackers",
      "note": "Court-ordered domain blocks still apply.",
      "doh": "https://child.joindns4.eu/dns-query",
      "dot": "child.joindns4.eu",
      "ipv4": [
        "86.54.11.12",
        "86.54.11.212"
      ],
      "ipv6": []
    },
    "dns4eu-noads": {
      "provider": "DNS4EU",
      "name": "Ads and trackers",
      "file": "DNS4EU-Ads",
      "blocks": "blocks malware, phishing, ads and trackers",
      "note": "Court-ordered domain blocks still apply.",
      "doh": "https://noads.joindns4.eu/dns-query",
      "dot": "noads.joindns4.eu",
      "ipv4": [
        "86.54.11.13",
        "86.54.11.213"
      ],
      "ipv6": []
    },
    "dns4eu-child-noads": {
      "provider": "DNS4EU",
      "name": "Ads, trackers and child protection",
      "file": "DNS4EU-Ads-Child",
      "blocks": "blocks malware, phishing, ads, trackers and content not suitable for children",
      "note": "Court-ordered domain blocks still apply.",
      "doh": "https://child-noads.joindns4.eu/dns-query",
      "dot": "child-noads.joindns4.eu",
      "ipv4": [
        "86.54.11.11",
        "86.54.11.211"
      ],
      "ipv6": []
    },
    "dns4eu-unfiltered": {
      "provider": "DNS4EU",
      "name": "Unfiltered",
      "file": "DNS4EU-Unfiltered",
      "blocks": "does not filter content",
      "note": "Court-ordered domain blocks still apply.",
      "doh": "https://unfiltered.joindns4.eu/dns-query",
      "dot": "unfiltered.joindns4.eu",
      "ipv4": [
        "86.54.11.100",
        "86.54.11.200"
      ],
      "ipv6": []
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
  // The Home Screen icon that installs with the profile when the page has a secure address. Its icon is the same
  // image as site/icons/apple-touch-icon.png; a test checks the base64 text below matches that file.
  var WEBCLIP = {
    id: "com.quiet.dns.webclip",
    uuid: "21077DBB-A8F2-4AC4-84E7-3E456C036E45",
    text: "It also adds a Quiet DNS icon to your Home Screen.",
    icon: "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"
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

  function consentText(s, webclip) {
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
    if (webclip) { text += " " + WEBCLIP.text; }
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

  function webClipPayload(url) {
    return {
      FullScreen: true,
      Icon: {base64: WEBCLIP.icon},
      Label: DISPLAY_NAME,
      PayloadDescription: "Opens Quiet DNS from your Home Screen.",
      PayloadDisplayName: DISPLAY_NAME,
      PayloadIdentifier: WEBCLIP.id,
      PayloadType: "com.apple.webClip.managed",
      PayloadUUID: WEBCLIP.uuid,
      PayloadVersion: PAYLOAD_VERSION,
      URL: url
    };
  }

  // siteUrl: the page's own secure address. When it is given, the profile also adds the Home Screen icon.
  function buildProfile(s, siteUrl) {
    var content = [dnsPayload(s)];
    if (siteUrl) { content.push(webClipPayload(siteUrl)); }
    return {
      ConsentText: {"default": consentText(s, !!siteUrl)},
      PayloadContent: content,
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
    // Binary data, such as the icon. Lines of 76 characters keep the file readable; plists ignore the line breaks.
    if (v && typeof v === "object" && typeof v.base64 === "string") {
      var lines = v.base64.match(/.{1,76}/g) || [];
      return pad + "<data>\n" + lines.map(function (line) { return pad + line; }).join("\n") + "\n" + pad + "</data>";
    }
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

  function profileXML(s, siteUrl) {
    return '<?xml version="1.0" encoding="UTF-8"?>\n' +
      '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n' +
      '<plist version="1.0">\n' + plistValue(buildProfile(s, siteUrl), 0) + '\n</plist>\n';
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
