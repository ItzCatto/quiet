/* Quiet DNS website: screens, settings and the profile download. Depends on core.js and boot.js. */
(function () {
  // Shown in the support details. Keep it equal to the newest version in CHANGELOG.md; a test checks this.
  var APP_VERSION = "2.3.0";
  // Every setting the profile depends on. The filter choice on the home screen sets block_ads and block_adult.
  var SETTINGS = ["enabled", "block_ads", "block_adult", "use_tls", "bootstrap_ips", "failover"];
  // The settings with a switch of their own: the power switch, and the Connection page.
  var SWITCHES = ["enabled", "use_tls", "bootstrap_ips", "failover"];
  var DEFAULTS = {enabled: true, block_ads: true, block_adult: false, use_tls: false, bootstrap_ips: true, failover: false};
  var SCREENS = ["home", "setup", "connection", "profile", "install", "help", "privacy", "settings"];
  // A browser tab can open these. The other screens need the installed app, so they go to the setup page.
  var BROWSER_SCREENS = ["home", "setup", "privacy", "help"];
  var THEME_KEY = "quiet.theme";
  var TEXT_KEY = "quiet.textSize";
  var KEYS_KEY = "quiet.showKeys";
  // The settings last downloaded as a profile. The save bar compares the current settings with them.
  var DOWNLOADED_KEY = "quiet.downloaded";
  // When the profile was last downloaded, for the Profile page and the support details.
  var SAVED_AT_KEY = "quiet.savedAt";
  var FILTER_LABEL = {"default": "Standard", "family": "Family", "unfiltered": "Unfiltered"};
  var FILTER_NOTE = {
    "default": "Recommended for most people. Blocks ads, trackers and phishing sites.",
    "family": "Also blocks adult websites and turns on safe search.",
    "unfiltered": "Nothing is blocked. Lookups are still encrypted."
  };
  var state = JSON.parse(JSON.stringify(DEFAULTS));
  // True after Save starts a download, until the person taps Continue.
  var awaitingAllow = false;
  // Set by boot.js before this file runs.
  var installed = document.body.classList.contains("installed");

  function $(id) { return document.getElementById(id); }

  // What the profile will contain. Adult blocking always includes ad blocking.
  function normalized() {
    var s = {};
    SETTINGS.forEach(function (k) { s[k] = state[k]; });
    if (s.block_adult) { s.block_ads = true; }
    return s;
  }

  function hostOf(url) {
    return url.replace(/^https:\/\//, "").replace(/\/dns-query$/, "");
  }

  function fileName(s) {
    var base = s.enabled ? FILTER_LABEL[QuietCore.resolverKey(s)] : "Paused";
    if (s.use_tls) { base += "-TLS"; }
    if (s.failover) { base += "-Failover"; }
    return "Quiet-DNS-" + base + ".mobileconfig";
  }

  // Website preferences. They are remembered in this browser only, and never touch the profile.
  // Storage can be blocked (private windows, some previews), so every read and write is guarded.
  function readPref(key, fallback) {
    try {
      var value = window.localStorage.getItem(key);
      return value === null ? fallback : value;
    } catch (err) {
      return fallback;
    }
  }

  function savePref(key, value) {
    try { window.localStorage.setItem(key, value); } catch (err) { /* keep working without memory */ }
  }

  // True when the settings on screen differ from the last profile downloaded.
  function isUnsaved() {
    return readPref(DOWNLOADED_KEY, "") !== JSON.stringify(normalized());
  }

  // The address this page was opened from, for the Home Screen icon in the profile. Only a secure address
  // works, so a page opened from a file or a preview gets no icon.
  function pageAddress() {
    var href = window.location.href.split("#")[0].split("?")[0];
    return /^https:\/\//.test(href) ? href : null;
  }

  // The settings that differ from the last download, in words. Empty before the first download.
  function changedNames() {
    var saved = readPref(DOWNLOADED_KEY, "");
    if (!saved) { return []; }
    var base;
    try { base = JSON.parse(saved); } catch (err) { return []; }
    var now = normalized();
    var names = [];
    if (QuietCore.resolverKey(base) !== QuietCore.resolverKey(now)) { names.push("Filter"); }
    if (!!base.enabled !== !!now.enabled) { names.push("Quiet DNS on or paused"); }
    if (!!base.use_tls !== !!now.use_tls) { names.push("DNS over TLS"); }
    if (!!base.bootstrap_ips !== !!now.bootstrap_ips) { names.push("AdGuard's IP addresses"); }
    if (!!base.failover !== !!now.failover) { names.push("Fall back to your network's DNS"); }
    return names;
  }

  function savedText() {
    var value = readPref(SAVED_AT_KEY, "");
    var when = value ? new Date(value) : null;
    if (!when || isNaN(when.getTime())) { return "Not yet"; }
    return when.toLocaleString(undefined, {dateStyle: "medium", timeStyle: "short"});
  }

  function render() {
    var s = normalized();
    var key = QuietCore.resolverKey(s);
    var r = QuietCore.RESOLVERS[key];
    var transport = s.use_tls ? "TLS" : "HTTPS";
    var downloaded = readPref(DOWNLOADED_KEY, "");

    SWITCHES.forEach(function (id) { $(id).checked = s[id]; });

    // Switch, status line and connection value
    $("widget").classList.toggle("is-on", s.enabled);
    $("w-title").textContent = s.enabled ? "Quiet DNS is on" : "Quiet DNS is paused";
    $("w-sub").textContent = s.enabled ? FILTER_LABEL[key] + " filter, " + transport : "Using your network's DNS";
    $("v-connection").textContent = transport;

    // Filter picker
    var filter = s.block_adult ? "family" : (s.block_ads ? "default" : "unfiltered");
    document.querySelectorAll('input[name="filter"]').forEach(function (radio) {
      radio.checked = radio.value === filter;
    });
    $("pick-note").textContent = FILTER_NOTE[filter];

    // Profile screen
    var host = s.use_tls ? r.dot + ", port 853" : hostOf(r.doh) + ", port 443";
    $("summary").textContent = QuietCore.summary(s);
    $("fact-state").textContent = s.enabled ? "On, " + FILTER_LABEL[key] : "Paused";
    $("fact-host").textContent = host;
    $("fact-proto").textContent = transport;
    $("fact-ips").textContent = s.bootstrap_ips ? (r.ipv4.length + r.ipv6.length) + " included" : "Not included";
    $("fact-saved").textContent = savedText();
    $("fact-clip").textContent = pageAddress() ? "Added with the profile" : "Not added. Open the hosted site.";
    $("warn").hidden = !(s.enabled && s.failover);
    $("download").textContent = s.enabled ? "Download profile" : "Download paused profile";
    $("next-step").textContent = s.enabled
      ? "Installing replaces any Quiet DNS profile already on your iPhone, so you won't end up with two."
      : "Installing this pauses Quiet DNS. Install the normal profile to turn it back on.";
    var changes = changedNames();
    $("changes").hidden = changes.length === 0;
    $("changes").textContent = changes.length
      ? "Changed since your last download: " + changes.join(", ") + "."
      : "";
    $("consent").textContent = QuietCore.consentText(s, !!pageAddress());
    $("xml").textContent = QuietCore.profileXML(s, pageAddress());
    $("clip-note").hidden = !pageAddress();

    // Save bar: unsaved until the profile is downloaded with these settings. After Save it waits for Allow,
    // and Continue then opens the install steps. Discard puts the settings back to the last download.
    var unsaved = isUnsaved();
    var waiting = awaitingAllow && !unsaved;
    $("savebar-text").textContent = waiting ? "Waiting for Allow" : (unsaved ? "Unsaved" : "Saved");
    $("savebar-text").classList.toggle("is-unsaved", unsaved || waiting);
    // Discard only shows when there is something to discard: a change since the last download, or any change
    // before the first download.
    $("discard").hidden = !unsaved || (downloaded === "" && JSON.stringify(s) === JSON.stringify(DEFAULTS));
    $("save").textContent = waiting ? "Continue" : "Save";
    $("save").disabled = !unsaved && !waiting;

    // First run: the three-step card shows until a profile has been downloaded once
    $("start").hidden = downloaded !== "";
  }

  // fromSave: Save waits for the person to allow the download, then Continue opens the install steps.
  // The Download button on the Profile page only downloads.
  function download(fromSave) {
    var s = normalized();
    var xml = QuietCore.profileXML(s, pageAddress());
    try {
      var blob = new Blob([xml], {type: "application/x-apple-aspen-config"});
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = fileName(s);
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Keep the link valid for a while, so a slow tap on Allow still works.
      setTimeout(function () { URL.revokeObjectURL(url); }, 5 * 60 * 1000);
    } catch (err) {
      $("download-status").textContent = "The download didn't start. Open this page in Safari and try again.";
      return;
    }
    // Remember what was downloaded, so the save bar shows Saved. A web page can't open Settings on iPhone,
    // so the bar says where to tap instead.
    savePref(DOWNLOADED_KEY, JSON.stringify(s));
    savePref(SAVED_AT_KEY, new Date().toISOString());
    $("download-status").textContent = "Download started. If nothing happens, allow downloads for this site.";
    awaitingAllow = fromSave;
    $("save-status").textContent = fromSave
      ? "Tap Allow in the pop-up, then tap Continue."
      : "Downloaded. Next, open Settings, tap General, then VPN & Device Management.";
    render();
  }

  // The page can't see whether Allow was tapped, so Continue is the confirmation. Then the install steps open.
  function continueToInstall() {
    awaitingAllow = false;
    $("save-status").textContent = "Downloaded. Next, open Settings, tap General, then VPN & Device Management.";
    window.location.hash = "#install";
    render();
  }

  // Back to the settings last downloaded, or to the defaults when nothing has been downloaded yet.
  function discard() {
    var base = DEFAULTS;
    try {
      var saved = readPref(DOWNLOADED_KEY, "");
      if (saved) { base = JSON.parse(saved); }
    } catch (err) {
      base = DEFAULTS;
    }
    SETTINGS.forEach(function (k) { state[k] = base[k] === undefined ? DEFAULTS[k] : base[k]; });
    awaitingAllow = false;
    $("download-status").textContent = "";
    $("save-status").textContent = "Changes discarded.";
    render();
  }

  // Copies a short summary for support. It holds the settings and the version, and nothing about the device.
  function copyDetails() {
    var text = [
      "Quiet DNS " + APP_VERSION,
      "Status: " + $("fact-state").textContent,
      "Server: " + $("fact-host").textContent,
      "Protocol: " + $("fact-proto").textContent,
      "Addresses: " + $("fact-ips").textContent,
      "Last saved: " + $("fact-saved").textContent
    ].join("\n");
    function report(ok) {
      $("download-status").textContent = ok
        ? "Copied. Paste it into your message."
        : "Couldn't copy on this phone. Try again, or write the details down.";
    }
    try {
      navigator.clipboard.writeText(text).then(function () { report(true); }, function () { report(false); });
    } catch (err) {
      report(false);
    }
  }

  // Screens are chosen by the URL hash, so every row is a real link that works without a page reload.
  // In a browser tab only the pages in BROWSER_SCREENS open. The rest open from the Home Screen, so any other
  // link goes to the setup page and the address bar shows #setup.
  function current() {
    var name = (window.location.hash || "").replace(/^#/, "");
    if (SCREENS.indexOf(name) < 0) { name = "home"; }
    if (!installed && BROWSER_SCREENS.indexOf(name) < 0) {
      name = "setup";
      if (window.history && window.history.replaceState) { window.history.replaceState(null, "", "#setup"); }
    }
    return name;
  }

  function show(name, moveFocus) {
    SCREENS.forEach(function (id) { $("screen-" + id).hidden = id !== name; });
    document.body.setAttribute("data-screen", name);

    // The browser tab title follows the screen, so each page has its own name in history and tabs.
    var titleId = name === "home" && !installed ? "title-landing" : "title-" + name;
    var heading = $(titleId);
    var text = heading.textContent.trim();
    if (name === "home") {
      document.title = "Quiet DNS";
    } else if (text.indexOf("Quiet DNS") >= 0) {
      document.title = text;
    } else {
      document.title = text + " – Quiet DNS";
    }

    if (moveFocus) {
      // Move focus to the new screen's title, so screen readers announce the change.
      heading.focus({preventScroll: true});
      window.scrollTo(0, 0);
    }
  }

  window.addEventListener("hashchange", function () { show(current(), true); });

  // Any change clears the messages from the last download, then redraws. Until the profile is saved and installed,
  // the iPhone keeps its current setting, so the save bar says so as soon as something changes.
  function changed() {
    awaitingAllow = false;
    $("download-status").textContent = "";
    $("save-status").textContent = "";
    render();
    if (isUnsaved()) {
      $("save-status").textContent = "Not on your iPhone yet. Save, then install the profile.";
    }
  }

  SWITCHES.forEach(function (id) {
    $(id).addEventListener("change", function () {
      state[id] = $(id).checked;
      changed();
    });
  });

  document.querySelectorAll('input[name="filter"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
      if (radio.value === "family") { state.block_ads = true; state.block_adult = true; }
      else if (radio.value === "default") { state.block_ads = true; state.block_adult = false; }
      else { state.block_ads = false; state.block_adult = false; }
      changed();
    });
  });

  $("download").addEventListener("click", function () { download(false); });
  $("save").addEventListener("click", function () {
    if (awaitingAllow) { continueToInstall(); } else { download(true); }
  });
  $("discard").addEventListener("click", discard);
  $("copy-details").addEventListener("click", copyDetails);

  function applyTheme(value) {
    var root = document.documentElement;
    if (value === "light" || value === "dark") {
      root.setAttribute("data-theme", value);
    } else {
      value = "system";
      root.removeAttribute("data-theme");
    }
    document.querySelectorAll('input[name="theme"]').forEach(function (radio) {
      radio.checked = radio.value === value;
    });
  }

  function applyText(value) {
    var root = document.documentElement;
    if (value === "larger") {
      root.setAttribute("data-text", "larger");
    } else {
      value = "standard";
      root.removeAttribute("data-text");
    }
    document.querySelectorAll('input[name="text"]').forEach(function (radio) {
      radio.checked = radio.value === value;
    });
  }

  function applyKeys(on) {
    document.body.classList.toggle("hide-keys", !on);
    $("show_keys").checked = on;
  }

  document.querySelectorAll('input[name="theme"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
      applyTheme(radio.value);
      savePref(THEME_KEY, radio.value);
    });
  });
  document.querySelectorAll('input[name="text"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
      applyText(radio.value);
      savePref(TEXT_KEY, radio.value);
    });
  });
  $("show_keys").addEventListener("change", function () {
    applyKeys($("show_keys").checked);
    savePref(KEYS_KEY, $("show_keys").checked ? "1" : "0");
  });

  applyTheme(readPref(THEME_KEY, "dark"));
  applyText(readPref(TEXT_KEY, "standard"));
  applyKeys(readPref(KEYS_KEY, "0") === "1");

  render();
  show(current(), false);
})();
