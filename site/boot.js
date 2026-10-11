/* Runs first, before the page is painted. It marks the installed app, so the Home Screen dashboard shows
   at once and the browser home page never flashes. iOS sets navigator.standalone; other browsers use the
   display-mode media query. */
(function () {
  var standalone = window.navigator.standalone === true ||
    (window.matchMedia ? window.matchMedia("(display-mode: standalone)").matches : false);
  if (standalone) { document.body.classList.add("installed"); }
})();
