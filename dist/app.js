/* VideoLAN redesign — progressive enhancement. ES5, no dependencies. */
(function () {
  'use strict';
  var d = document, html = d.documentElement;
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  var store = { get: function (k) { try { return localStorage.getItem('vl-' + k); } catch (e) { return null; } },
                set: function (k, v) { try { if (v) localStorage.setItem('vl-' + k, v); else localStorage.removeItem('vl-' + k); } catch (e) {} } };
  var toastT;
  function toast(msg) { var t = $('#toast'); t.textContent = msg; t.className = 'toast show'; clearTimeout(toastT); toastT = setTimeout(function () { t.className = 'toast'; }, 3800); }

  /* ---------- Router ---------- */
  var views = $$('.view'), ids = views.map(function (v) { return v.id; });
  var pending = null;
  function route() {
    var h = (location.hash || '#home').slice(1), target = null, viewId = 'home';
    if (ids.indexOf(h) > -1) viewId = h;
    else {
      var el = h && d.getElementById(h);
      if (el) { var v = el.closest ? el.closest('.view') : null; if (v) { viewId = v.id; target = el; } }
    }
    if (pending) { target = d.getElementById(pending); pending = null; }
    views.forEach(function (v) { v.classList.toggle('active', v.id === viewId); });
    $$('[data-nav]').forEach(function (a) { if (a.getAttribute('data-nav') === viewId) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
    var view = d.getElementById(viewId); d.title = view.getAttribute('data-title') || d.title;
    closeDrawer();
    if (target) { setTimeout(function () { target.scrollIntoView(); }, 30); }
    else { window.scrollTo(0, 0); }
    if (route.ran) { var m = $('#main'); m.focus({ preventScroll: true }); }
    route.ran = true;
    observe();
  }
  d.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('[data-goto]');
    if (a) { pending = a.getAttribute('data-goto'); if (location.hash === a.getAttribute('href')) { ev.preventDefault(); route(); } }
  });
  window.addEventListener('hashchange', route);

  /* ---------- Mobile drawer ---------- */
  var menuBtn = $('#menu-btn'), drawer = $('#drawer');
  function closeDrawer() { drawer.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); menuBtn.setAttribute('aria-label', 'Open menu'); }
  menuBtn.addEventListener('click', function () {
    var open = !drawer.classList.contains('open');
    drawer.classList.toggle('open', open); menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menuBtn.querySelector('use').setAttribute('href', open ? '#i-close' : '#i-menu');
    menuBtn.querySelector('use').setAttribute('xlink:href', open ? '#i-close' : '#i-menu');
  });

  /* ---------- Ribbon ---------- */
  if (store.get('ribbon') === 'hidden') $('#ribbon').style.display = 'none';
  $('#ribbon-close').addEventListener('click', function () { $('#ribbon').style.display = 'none'; store.set('ribbon', 'hidden'); });

  /* ---------- Theme ---------- */
  var mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  function applyTheme(pref) {
    var dark = pref === 'dark' || (pref === 'auto' && mq && mq.matches);
    html.setAttribute('data-theme', dark ? 'dark' : 'light');
    var use = $('#theme-ico use'); use.setAttribute('href', dark ? '#i-sun' : '#i-moon'); use.setAttribute('xlink:href', dark ? '#i-sun' : '#i-moon');
    $('#theme-btn').setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    var meta = $$('meta[name="theme-color"]'); meta.forEach(function (m) { m.setAttribute('content', dark ? '#0f0e0d' : '#fbf8f4'); });
    syncSeg();
  }
  function themePref() { return store.get('theme') || 'auto'; }
  $('#theme-btn').addEventListener('click', function () {
    var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    store.set('theme', next); applyTheme(next);
  });
  if (mq && mq.addEventListener) mq.addEventListener('change', function () { if (themePref() === 'auto') applyTheme('auto'); });

  /* ---------- Dialogs ---------- */
  var lastFocus = null;
  function openDialog(id) {
    var o = d.getElementById(id); lastFocus = d.activeElement;
    o.classList.add('open'); o.setAttribute('aria-hidden', 'false');
    var f = o.querySelector('input, button:not([data-close])') || o.querySelector('button'); setTimeout(function () { f.focus(); }, 20);
  }
  function closeDialog(o) { o.classList.remove('open'); o.setAttribute('aria-hidden', 'true'); if (lastFocus) lastFocus.focus(); }
  $$('.overlay').forEach(function (o) {
    o.addEventListener('click', function (ev) { if (ev.target === o || (ev.target.closest && ev.target.closest('[data-close]'))) closeDialog(o); });
    o.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' || ev.keyCode === 27) { closeDialog(o); return; }
      if (ev.key === 'Tab') { // focus trap
        var f = $$('button, input, a[href]', o).filter(function (x) { return x.offsetParent !== null; });
        if (!f.length) return; var first = f[0], last = f[f.length - 1];
        if (ev.shiftKey && d.activeElement === first) { ev.preventDefault(); last.focus(); }
        else if (!ev.shiftKey && d.activeElement === last) { ev.preventDefault(); first.focus(); }
      }
    });
  });
  $('#lang-btn').addEventListener('click', function () { openDialog('lang-dialog'); });
  $$('[data-open-lang]').forEach(function (b) { b.addEventListener('click', function () { openDialog('lang-dialog'); }); });
  $('#a11y-btn').addEventListener('click', function () { openDialog('a11y-dialog'); });

  /* ---------- Language ---------- */
  var langBtns = $$('#lang-grid button');
  function setLang(code, silent) {
    var b = $('#lang-grid [data-lang="' + code + '"]'); if (!b) return;
    langBtns.forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
    var native = b.getAttribute('data-native');
    $('#lang-code').textContent = code.split('-')[0].toUpperCase();
    $('#foot-lang').textContent = native;
    $('#lang-btn').setAttribute('aria-label', 'Language: ' + native + '. Change language');
    store.set('lang', code === 'en' ? '' : code);
    if (!silent) {
      closeDialog($('#lang-dialog'));
      if (code === 'en') toast('English selected.');
      else toast(native + ' is not translated yet. Showing English for now, and your choice is saved.');
    }
  }
  langBtns.forEach(function (b) { b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); }); });
  var q = $('#lang-q');
  function filterLangs() {
    var v = q.value.toLowerCase().trim(), n = 0;
    langBtns.forEach(function (b) {
      var hit = !v || (b.getAttribute('data-native') + ' ' + b.getAttribute('data-en') + ' ' + b.getAttribute('data-lang')).toLowerCase().indexOf(v) > -1;
      b.style.display = hit ? '' : 'none'; if (hit) n++;
    });
    $('#lang-count').textContent = n + ' of ' + langBtns.length + ' languages';
  }
  q.addEventListener('input', filterLangs); filterLangs();
  if (store.get('lang')) setLang(store.get('lang'), true);

  /* ---------- Accessibility prefs ---------- */
  function syncSeg() {
    $$('.seg').forEach(function (s) {
      var k = s.getAttribute('data-pref'), cur = k === 'theme' ? themePref() : (html.getAttribute('data-' + k) || '');
      $$('button', s).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === cur)); });
    });
  }
  $$('.seg').forEach(function (s) {
    s.addEventListener('click', function (ev) {
      var b = ev.target.closest('button'); if (!b) return;
      var k = s.getAttribute('data-pref'), v = b.getAttribute('data-v');
      if (k === 'theme') { store.set('theme', v === 'auto' ? '' : v); applyTheme(v); return; }
      if (v) html.setAttribute('data-' + k, v); else html.removeAttribute('data-' + k);
      store.set(k, v);
      if (k === 'motion') { html.classList.toggle('motion', v !== 'off'); }
      syncSeg();
    });
  });

  /* ---------- OS detection ---------- */
  var V = '3.0.24';
  var OS = {
    windows: ['Download VLC for Windows', 'Version ' + V + ' · 64-bit · 39 MB', 'https://www.videolan.org/vlc/download-windows.html'],
    mac: ['Download VLC for macOS', 'Version ' + V + ' · Universal · Apple Silicon & Intel', 'https://www.videolan.org/vlc/download-macosx.html'],
    linux: ['Get VLC for Linux', 'Version ' + V + ' · from your distribution, Flatpak or Snap', '#os-linux'],
    android: ['Get VLC for Android', 'Free on Google Play and F-Droid', 'https://www.videolan.org/vlc/download-android.html'],
    ios: ['Get VLC for iPhone & iPad', 'Free on the App Store', 'https://www.videolan.org/vlc/download-ios.html'],
    cros: ['Get VLC for ChromeOS', 'Free on Google Play', 'https://www.videolan.org/vlc/download-chromeos.html']
  };
  function detect() {
    var ua = navigator.userAgent || '', p = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
    if (/Android/i.test(ua)) return 'android';
    if (/iPhone|iPad|iPod/i.test(ua) || (/Mac/i.test(p) && navigator.maxTouchPoints > 1)) return 'ios';
    if (/CrOS/i.test(ua)) return 'cros';
    if (/Win/i.test(p) || /Windows/i.test(ua)) return 'windows';
    if (/Mac/i.test(p) || /Mac OS X/i.test(ua)) return 'mac';
    if (/Linux|X11|BSD/i.test(p + ua)) return 'linux';
    return 'windows';
  }
  var os = detect(), o = OS[os];
  $('#dl-label').textContent = o[0]; $('#dl-sub').textContent = o[1]; $('#dl-primary').setAttribute('href', o[2]);
  if (os === 'linux') $('#dl-primary').setAttribute('data-goto', 'os-linux');
  var blk = $('.os-block[data-os="' + (os === 'ios' ? 'mac' : os === 'cros' ? 'android' : os) + '"]'); if (blk) blk.classList.add('detected');

  /* ---------- Tabs (ARIA, arrow keys) ---------- */
  var tabs = $$('[role="tab"]');
  function selectTab(t, focus) {
    tabs.forEach(function (x) { var on = x === t; x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1; d.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
    if (focus) t.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectTab(t); });
    t.addEventListener('keydown', function (ev) {
      if (ev.key === 'ArrowRight') selectTab(tabs[(i + 1) % tabs.length], true);
      if (ev.key === 'ArrowLeft') selectTab(tabs[(i - 1 + tabs.length) % tabs.length], true);
    });
  });

  /* ---------- News filter ---------- */
  $$('.news-filter button').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-filter');
      $$('.news-filter button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      $$('#news-list .news-item').forEach(function (n) { n.style.display = (f === 'all' || n.getAttribute('data-cat') === f) ? '' : 'none'; });
    });
  });

  /* ---------- Donate amount ---------- */
  $$('.amounts').forEach(function (form) {
    var label = form.querySelector('[data-amt-label]');
    form.addEventListener('click', function (ev) {
      var b = ev.target.closest('[data-amt]'); if (!b) return;
      $$('[data-amt]', form).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var a = b.getAttribute('data-amt'); label.textContent = a === 'other' ? 'any amount' : '€' + a;
    });
    form.addEventListener('change', function () {
      var m = form.querySelector('input[value="monthly"]').checked;
      label.parentNode.firstChild.nodeValue = m ? 'Donate monthly ' : 'Donate ';
    });
  });

  /* ---------- Reveal on scroll ---------- */
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px' }) : null;
  function observe() {
    $$('.view.active .reveal:not(.in)').forEach(function (el) { if (io) io.observe(el); else el.classList.add('in'); });
  }

  applyTheme(themePref());
  route();
})();
