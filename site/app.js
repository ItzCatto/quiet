/* Quiet DNS website: screens, settings and the profile download. Depends on core.js. */
(function () {
  var TOGGLES = ["enabled", "block_ads", "block_adult", "use_tls", "bootstrap_ips", "failover"];
  var SCREENS = ["home", "setup", "filters", "connection", "profile", "install", "privacy", "settings"];
  var THEME_KEY = "quiet.theme";
  var KEYS_KEY = "quiet.showKeys";
  // The settings last downloaded as a profile. The save bar compares the current settings with them.
  var DOWNLOADED_KEY = "quiet.downloaded";
  var FILTER_LABEL = {"default": "Standard", "family": "Family", "unfiltered": "Unfiltered"};
  var FILTER_NOTE = {
    "default": "Blocks ads and trackers.",
    "family": "Also blocks adult sites. Safe search is on.",
    "unfiltered": "Nothing is blocked. Lookups are still encrypted."
  };
  var state = {enabled: true, block_ads: true, block_adult: false, use_tls: false, bootstrap_ips: true, failover: false};

  function $(id) { return document.getElementById(id); }

  // What the profile will contain. Adult blocking always includes ad blocking.
  function normalized() {
    var s = {};
    TOGGLES.forEach(function (k) { s[k] = state[k]; });
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

  function render() {
    var s = normalized();
    var key = QuietCore.resolverKey(s);
    var r = QuietCore.RESOLVERS[key];
    var transport = s.use_tls ? "TLS" : "HTTPS";

    TOGGLES.forEach(function (id) { $(id).checked = s[id]; });
    $("block_ads").disabled = state.block_adult;
    $("note-block_ads").hidden = !state.block_adult;

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
    $("warn").hidden = !(s.enabled && s.failover);
    $("download").textContent = s.enabled ? "Download profile" : "Download paused profile";
    $("next-step").textContent = s.enabled
      ? "Installing updates the Quiet DNS entry already on your iPhone."
      : "Installing this pauses Quiet DNS. Install the normal profile to turn it back on.";
    $("consent").textContent = QuietCore.consentText(s);
    $("xml").textContent = QuietCore.profileXML(s);

    // Save bar: unsaved until the profile is downloaded with these settings
    var unsaved = readPref(DOWNLOADED_KEY, "") !== JSON.stringify(s);
    $("savebar-text").textContent = unsaved ? "Unsaved" : "Saved";
    $("savebar-text").classList.toggle("is-unsaved", unsaved);
    $("save").disabled = !unsaved;
  }

  function download() {
    var s = normalized();
    var xml = QuietCore.profileXML(s);
    try {
      var blob = new Blob([xml], {type: "application/x-apple-aspen-config"});
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = fileName(s);
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
    } catch (err) {
      $("download-status").textContent = "The download didn't start. Try another browser.";
      return;
    }
    // Remember what was downloaded, so the save bar shows Saved. A web page can't open Settings on iPhone,
    // so the bar says where to tap instead.
    savePref(DOWNLOADED_KEY, JSON.stringify(s));
    $("download-status").textContent = "Download started. If nothing happens, allow downloads for this site.";
    $("save-status").textContent = "Downloaded. Open Settings and tap Profile Downloaded.";
    render();
  }

  // Screens are chosen by the URL hash, so every row is a real link that works without a page reload.
  // In a browser tab only the home page and the setup page open. The app screens open from the Home Screen,
  // so any other link goes to the setup page and the address bar shows #setup.
  function current() {
    var name = (window.location.hash || "").replace(/^#/, "");
    if (SCREENS.indexOf(name) < 0) { name = "home"; }
    if (!installed && name !== "home" && name !== "setup") {
      name = "setup";
      if (window.history && window.history.replaceState) { window.history.replaceState(null, "", "#setup"); }
    }
    return name;
  }

  function show(name, moveFocus) {
    SCREENS.forEach(function (id) { $("screen-" + id).hidden = id !== name; });
    document.body.setAttribute("data-screen", name);
    if (moveFocus) {
      // Move focus to the new screen's title, so screen readers announce the change.
      var title = name === "home" && !installed ? "title-landing" : "title-" + name;
      $(title).focus({preventScroll: true});
      window.scrollTo(0, 0);
    }
  }

  window.addEventListener("hashchange", function () { show(current(), true); });

  // Any change clears the messages from the last download, then redraws.
  function changed() {
    $("download-status").textContent = "";
    $("save-status").textContent = "";
    render();
  }

  TOGGLES.forEach(function (id) {
    $(id).addEventListener("change", function () {
      state[id] = $(id).checked;
      if (id === "block_adult" && state.block_adult) { state.block_ads = true; }
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

  $("download").addEventListener("click", download);
  $("save").addEventListener("click", download);

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
  $("show_keys").addEventListener("change", function () {
    applyKeys($("show_keys").checked);
    savePref(KEYS_KEY, $("show_keys").checked ? "1" : "0");
  });

  applyTheme(readPref(THEME_KEY, "dark"));
  applyKeys(readPref(KEYS_KEY, "0") === "1");

  // The app is installed when it opens from the Home Screen. iOS sets navigator.standalone;
  // other browsers use the display-mode media query.
  var installed = window.navigator.standalone === true ||
    (window.matchMedia ? window.matchMedia("(display-mode: standalone)").matches : false);
  document.body.classList.toggle("installed", installed);

  render();
  show(current(), false);
})();
