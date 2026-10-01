/* Shared UI for the VideoLAN redesign proposals (A, B, C). ES5, no dependencies.
   - Full-screen donation checkout (Stripe Checkout today, Stripe Elements / Payment Request ready)
   - "Not yet redesigned" notice for VideoLAN-owned pages outside this bundle
   - Option switcher, language dialog, display & accessibility dialog, search palette */
(function () {
  'use strict';
  var d = document, html = d.documentElement, W = window;
  var OPT = html.getAttribute('data-opt') || 'a';
  var ROOT = html.getAttribute('data-root') || './';
  var SLUG = html.getAttribute('data-slug') || 'home';

  /* ---------------- Config (VideoLAN can edit this block) ---------------- */
  var CFG = W.VL_DONATE_CONFIG || {};
  var CONFIG = {
    stripeCheckoutUrl: CFG.stripeCheckoutUrl || 'https://www.videolan.org/stripe/checkout.php', // existing VideoLAN endpoint
    stripePublishableKey: CFG.stripePublishableKey || '',   // set "pk_live_..." to enable embedded Elements + Apple/Google Pay sheet
    paypalBusiness: 'sponsor@videolan.org',
    paypalReturn: 'https://www.videolan.org/thank_you.html',
    iban: 'FR76 3000 3034 3000 1506 8853 588', bic: 'SOGEFRPP', holder: 'VIDEOLAN',
    bitcoin: 'bc1q27wp4frlsckghy3vgdjg4rnlsxztxca0f2r4a7',
    bitcoinQR: 'https://images.videolan.org/images/bitcoin-bc1q27wp4frlsckghy3vgdjg4rnlsxztxca0f2r4a7.png'
  };

  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  function el(h) { var t = d.createElement('div'); t.innerHTML = h; return t.firstElementChild; }
  function store(k, v) { try { if (arguments.length === 1) return localStorage.getItem('vl-' + k); if (v) localStorage.setItem('vl-' + k, v); else localStorage.removeItem('vl-' + k); } catch (e) { return null; } }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var CONE = '<svg viewBox="0 0 64 64" aria-hidden="true"><defs><clipPath id="uicc"><path d="M27.2 6.5c.9-2.6 8.7-2.6 9.6 0L50 51H14z"/></clipPath></defs><path d="M27.2 6.5c.9-2.6 8.7-2.6 9.6 0L50 51H14z" fill="#ff8800"/><g clip-path="url(#uicc)" fill="#fff"><rect y="19" width="64" height="7"/><rect y="34" width="64" height="7.5"/></g><rect x="6" y="49" width="52" height="9" rx="3.5" fill="#ff8800"/></svg>';
  var ICO = {
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></svg>',
    card: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/></svg>',
    bank: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5 12 4l9 5.5M5 10v7M9.5 10v7M14.5 10v7M19 10v7M3 20h18"/></svg>',
    btc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9.5 7.5v9M9.5 8h3.8a2 2 0 0 1 0 4H9.5h4.3a2.2 2.2 0 0 1 0 4.4H9.5M11 6v1.5M11 16.5V18M13 6v1.5M13 16.5V18"/></svg>',
    paypal: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8.3 21H5.2c-.3 0-.5-.3-.5-.6L7.4 3.5c.1-.3.3-.5.6-.5h6.2c3.4 0 5.4 1.8 4.9 4.9-.6 3.6-3 5.3-6.3 5.3h-2c-.3 0-.5.2-.6.5z" opacity=".55"/><path d="M19.6 8.2c.5 3.3-1.6 6.2-5.6 6.2h-1.6c-.3 0-.5.2-.6.5l-.8 5.2-.2 1c0 .3-.3.5-.6.5H7.7c-.3 0-.4-.2-.4-.5l.3-1.8L9 10.7c.1-.3.3-.5.6-.5H12c2.6 0 4.6-.6 5.7-2.4.2-.3.4-.7.5-1 .7.3 1.2.8 1.4 1.4z"/></svg>',
    sepa: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16.5 7.5A6 6 0 1 0 16.5 16.5M4.5 10.5h9M4.5 13.5h9"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.1"/></svg>',
    ext: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
    apple: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.4 12.7c0-2.4 2-3.6 2.1-3.7-1.1-1.7-2.9-1.9-3.5-1.9-1.5-.2-2.9.9-3.7.9-.8 0-1.9-.9-3.2-.8-1.6 0-3.1 1-4 2.4-1.7 3-.4 7.4 1.2 9.8.8 1.2 1.8 2.5 3 2.4 1.2 0 1.7-.8 3.1-.8 1.5 0 1.9.8 3.2.8 1.3 0 2.1-1.2 2.9-2.4.9-1.3 1.3-2.6 1.3-2.7 0 0-2.4-1-2.4-4zM14 5.4c.7-.8 1.1-1.9 1-3-1 0-2.1.7-2.8 1.5-.6.7-1.2 1.8-1 2.9 1 .1 2.1-.6 2.8-1.4z"/></svg>',
    gpay: '<svg viewBox="0 0 24 24"><path fill="#4285F4" d="M21.6 12.2c0-.7-.1-1.4-.2-2H12v3.8h5.4a4.6 4.6 0 0 1-2 3v2.5h3.2c1.9-1.7 3-4.3 3-7.3z"/><path fill="#34A853" d="M12 22c2.7 0 5-.9 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3.1v2.6A10 10 0 0 0 12 22z"/><path fill="#FBBC05" d="M6.4 14a6 6 0 0 1 0-3.9V7.5H3.1a10 10 0 0 0 0 9z"/><path fill="#EA4335" d="M12 6c1.5 0 2.8.5 3.8 1.5l2.9-2.9A10 10 0 0 0 3.1 7.5l3.3 2.6C7.2 7.8 9.4 6 12 6z"/></svg>'
  };

  /* ---------------- Toast ---------------- */
  var toastEl, toastT;
  function toast(m) {
    if (!toastEl) { toastEl = el('<div class="ui-toast" role="status" aria-live="polite"></div>'); d.body.appendChild(toastEl); }
    toastEl.textContent = m; toastEl.className = 'ui-toast show'; clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.className = 'ui-toast'; }, 6000);
  }
  W.VLToast = toast;

  /* ---------------- Generic layer (dialog) management ---------------- */
  var lastFocus = null, openLayer = null;
  function trap(layer, ev) {
    if (ev.key === 'Escape') { close(layer); return; }
    if (ev.key !== 'Tab') return;
    var f = $$('button, input, a[href], select, textarea', layer).filter(function (x) { return x.offsetParent !== null && !x.disabled; });
    if (!f.length) return;
    if (ev.shiftKey && d.activeElement === f[0]) { ev.preventDefault(); f[f.length - 1].focus(); }
    else if (!ev.shiftKey && d.activeElement === f[f.length - 1]) { ev.preventDefault(); f[0].focus(); }
  }
  function open(layer, focusSel) {
    if (openLayer) close(openLayer, true);
    lastFocus = d.activeElement; openLayer = layer;
    layer.classList.add('open'); layer.setAttribute('aria-hidden', 'false');
    html.style.overflow = 'hidden';
    setTimeout(function () { var f = (focusSel && $(focusSel, layer)) || $('input, button', layer); if (f) f.focus(); }, 30);
  }
  function close(layer, silent) {
    layer.classList.remove('open'); layer.setAttribute('aria-hidden', 'true'); openLayer = null;
    html.style.overflow = '';
    if (!silent && lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function makeLayer(id, title, body, wide, extraCls) {
    var L = el('<div class="ui-layer" id="' + id + '" aria-hidden="true"><div class="ui-scrim" data-ui-close></div>' +
      '<div class="ui-card ' + (wide ? 'wide ' : '') + (extraCls || '') + '" role="dialog" aria-modal="true" aria-labelledby="' + id + '-t">' +
      (title ? '<div class="ui-head"><h2 id="' + id + '-t">' + title + '</h2><button type="button" class="ui-x" data-ui-close aria-label="Close">×</button></div>' : '') +
      body + '</div></div>');
    d.body.appendChild(L);
    L.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-ui-close]')) close(L); });
    L.addEventListener('keydown', function (e) { trap(L, e); });
    return L;
  }

  /* ---------------- "Not yet redesigned" notice ---------------- */
  var OWNED = /(^|\.)videolan\.(org|me)$|(^|\.)videolabs\.io$/i;
  var DIRECT = /^(get|download|downloads|mirror|images|artifacts|nightlies)\.videolan\.org$/i;
  var NAMES = { 'wiki.videolan.org': 'the VideoLAN wiki', 'forum.videolan.org': 'the VideoLAN forums', 'code.videolan.org': 'VideoLAN’s GitLab', 'addons.videolan.org': 'the VLC add-ons site', 'docs.videolan.me': 'the VLC documentation', 'mailman.videolan.org': 'the mailing-list archives', 'trac.videolan.org': 'the legacy bug tracker', 'git.videolan.org': 'the Git browser', 'streams.videolan.org': 'the sample streams archive', 'www.videolan.org': 'this page on videolan.org', 'videolan.org': 'this page on videolan.org' };
  var extLayer = null, extHref = '';
  function extNotice(href, host) {
    if (!extLayer) {
      extLayer = makeLayer('ui-ext', 'Not redesigned yet',
        '<div class="ui-body"><div class="ui-ext-ico">' + CONE + '</div>' +
        '<p id="ui-ext-msg"></p><div class="ui-url" id="ui-ext-url"></div>' +
        '<div class="ui-btns"><a class="ui-btn primary" id="ui-ext-go" href="#">Continue to the current page ' + '<span aria-hidden="true">→</span></a>' +
        '<button type="button" class="ui-btn" data-ui-close>Stay here</button></div></div>');
      $('#ui-ext-go', extLayer).addEventListener('click', function () { close(extLayer, true); });
    }
    var name = NAMES[host] || host;
    $('#ui-ext-msg', extLayer).innerHTML = 'You are about to open <b style="color:var(--ui-fg)">' + esc(name) + '</b>. This part of VideoLAN is not part of the redesign proposal yet. It will get the new design once the redesign is deployed. For now, it opens in its current form.';
    $('#ui-ext-url', extLayer).textContent = href;
    var go = $('#ui-ext-go', extLayer); go.setAttribute('href', href); go.setAttribute('rel', 'noopener');
    open(extLayer, '#ui-ext-go');
  }

  /* ---------------- Option switcher ---------------- */
  function switcher() {
    if (html.hasAttribute('data-noswitch')) return;
    var opts = [['a', 'A', 'Clean'], ['b', 'B', 'Player'], ['c', 'C', 'Almanac']];
    var path = SLUG === 'home' ? 'index.html' : 'p/' + SLUG + '.html';
    var h = '<nav class="ui-switch' + (store('switch-min') ? ' min' : '') + '" aria-label="Design options"><span class="lbl">Design</span>';
    opts.forEach(function (o) { h += '<a href="' + ROOT + o[0] + '/' + path + '"' + (o[0] === OPT ? ' aria-current="true"' : '') + '>' + o[1] + ' <small>' + o[2] + '</small></a>'; });
    h += '<a href="' + ROOT + 'index.html" title="All options" aria-label="Compare all options">⋯</a></nav>';
    d.body.appendChild(el(h));
  }

  /* ---------------- Languages ---------------- */
  var LANGS = [["en","English","English"],["fr","Français","French"],["de","Deutsch","German"],["es","Español","Spanish"],["pt-PT","Português (Portugal)","Portuguese"],["pt-BR","Português (Brasil)","Brazilian Portuguese"],["it","Italiano","Italian"],["nl","Nederlands","Dutch"],["pl","Polski","Polish"],["ru","Русский","Russian"],["uk","Українська","Ukrainian"],["cs","Čeština","Czech"],["sk","Slovenčina","Slovak"],["hu","Magyar","Hungarian"],["ro","Română","Romanian"],["bg","Български","Bulgarian"],["el","Ελληνικά","Greek"],["tr","Türkçe","Turkish"],["ar","العربية","Arabic"],["he","עברית","Hebrew"],["fa","فارسی","Persian"],["ur","اردو","Urdu"],["ps","پښتو","Pashto"],["hi","हिन्दी","Hindi"],["bn","বাংলা","Bengali"],["pa","ਪੰਜਾਬੀ","Punjabi"],["gu","ગુજરાતી","Gujarati"],["mr","मराठी","Marathi"],["ta","தமிழ்","Tamil"],["te","తెలుగు","Telugu"],["kn","ಕನ್ನಡ","Kannada"],["ml","മലയാളം","Malayalam"],["si","සිංහල","Sinhala"],["ne","नेपाली","Nepali"],["th","ไทย","Thai"],["vi","Tiếng Việt","Vietnamese"],["id","Bahasa Indonesia","Indonesian"],["ms","Bahasa Melayu","Malay"],["fil","Filipino","Filipino"],["zh-Hans","简体中文","Chinese (Simplified)"],["zh-Hant","繁體中文","Chinese (Traditional)"],["ja","日本語","Japanese"],["ko","한국어","Korean"],["sv","Svenska","Swedish"],["nb","Norsk bokmål","Norwegian"],["da","Dansk","Danish"],["fi","Suomi","Finnish"],["is","Íslenska","Icelandic"],["et","Eesti","Estonian"],["lv","Latviešu","Latvian"],["lt","Lietuvių","Lithuanian"],["sl","Slovenščina","Slovenian"],["hr","Hrvatski","Croatian"],["sr","Српски","Serbian"],["bs","Bosanski","Bosnian"],["mk","Македонски","Macedonian"],["sq","Shqip","Albanian"],["ca","Català","Catalan"],["eu","Euskara","Basque"],["gl","Galego","Galician"],["cy","Cymraeg","Welsh"],["ga","Gaeilge","Irish"],["br","Brezhoneg","Breton"],["oc","Occitan","Occitan"],["eo","Esperanto","Esperanto"],["sw","Kiswahili","Swahili"],["af","Afrikaans","Afrikaans"],["zu","isiZulu","Zulu"],["am","አማርኛ","Amharic"],["ha","Hausa","Hausa"],["yo","Yorùbá","Yoruba"],["kk","Қазақ тілі","Kazakh"],["uz","Oʻzbekcha","Uzbek"],["az","Azərbaycanca","Azerbaijani"],["ka","ქართული","Georgian"],["hy","Հայերեն","Armenian"],["mn","Монгол","Mongolian"],["km","ភាសាខ្មែរ","Khmer"],["lo","ລາວ","Lao"],["my","မြန်မာ","Burmese"],["ku","Kurdî","Kurdish"]];
  var RTL = { ar: 1, he: 1, fa: 1, ur: 1, ps: 1 };
  W.VL_LANGS = LANGS;
  var langLayer = null;
  function langDialog() {
    if (!langLayer) {
      var b = '';
      LANGS.forEach(function (l) { b += '<button type="button" lang="' + l[0] + '" data-l="' + l[0] + '" data-s="' + esc((l[1] + ' ' + l[2] + ' ' + l[0]).toLowerCase()) + '"><b' + (RTL[l[0]] ? ' dir="rtl"' : '') + '>' + l[1] + '</b><span' + (l[0] === 'en' ? ' class="ok">Available' : '>' + l[2]) + '</span></button>'; });
      langLayer = makeLayer('ui-lang', 'Choose your language',
        '<div class="ui-body"><label class="ui-sr" for="ui-lq">Search languages</label><input class="ui-search" id="ui-lq" type="search" autocomplete="off" placeholder="Search ' + LANGS.length + ' languages… (Português, 日本語, Arabic)">' +
        '<div class="ui-note">' + ICO.info.replace('<svg', '<svg width="18" height="18" style="flex-shrink:0;margin-top:2px"') + '<span>For now this site is available in English only. Every language listed here will be added quickly once the VideoLAN team confirms the redesign is a go. Your choice is saved for when it’s ready.</span></div>' +
        '<div class="ui-langs" id="ui-langs">' + b + '</div><p class="ui-count" id="ui-lc" aria-live="polite"></p></div>', true);
      var q = $('#ui-lq', langLayer), btns = $$('#ui-langs button', langLayer);
      function filt() { var v = q.value.toLowerCase().trim(), n = 0; btns.forEach(function (x) { var hit = !v || x.getAttribute('data-s').indexOf(v) > -1; x.style.display = hit ? '' : 'none'; if (hit) n++; }); $('#ui-lc', langLayer).textContent = n + ' of ' + btns.length + ' languages'; }
      q.addEventListener('input', filt); filt();
      btns.forEach(function (x) { x.addEventListener('click', function () { setLang(x.getAttribute('data-l')); close(langLayer); }); });
    }
    var cur = store('lang') || 'en';
    $$('#ui-langs button', langLayer).forEach(function (x) { x.setAttribute('aria-pressed', String(x.getAttribute('data-l') === cur)); });
    open(langLayer, '#ui-lq');
  }
  function langName(code) { for (var i = 0; i < LANGS.length; i++) if (LANGS[i][0] === code) return LANGS[i]; return LANGS[0]; }
  function setLang(code, silent) {
    var l = langName(code); store('lang', code === 'en' ? '' : code);
    $$('[data-ui-langlabel]').forEach(function (x) { x.textContent = x.getAttribute('data-ui-langlabel') === 'code' ? l[0].split('-')[0].toUpperCase() : l[1]; });
    if (!silent) toast(code === 'en' ? 'English selected.' : l[1] + ' (' + l[2] + ') is not available yet. For now the site is in English only; ' + l[2] + ' will be added quickly once the VideoLAN team confirms the redesign is a go.');
    d.dispatchEvent(new CustomEvent('vl:lang', { detail: l }));
  }

  /* ---------------- Display & accessibility ---------------- */
  var themeKey = OPT === 'a' ? 'theme' : 'theme-' + OPT, defTheme = html.getAttribute('data-default-theme') || 'auto';
  function themePref() { return store(themeKey) || defTheme; }
  function applyTheme(p) {
    var mq = W.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches;
    var skin = p;
    var dark = p === 'dark' || (p === 'auto' && mq) || (p !== 'light' && p !== 'auto' && p !== 'dark' && html.getAttribute('data-skin-dark-' + p) === '1');
    html.setAttribute('data-theme', dark ? 'dark' : 'light');
    html.setAttribute('data-skin', skin);
    syncSeg(); d.dispatchEvent(new CustomEvent('vl:theme', { detail: { dark: dark, skin: skin } }));
  }
  W.VLTheme = { get: themePref, set: function (p) { store(themeKey, p === defTheme ? '' : p); applyTheme(p); }, toggle: function () { var dark = html.getAttribute('data-theme') === 'dark'; W.VLTheme.set(dark ? 'light' : 'dark'); } };
  var a11yLayer = null;
  function syncSeg() {
    if (!a11yLayer) return;
    $$('.ui-seg', a11yLayer).forEach(function (s) {
      var k = s.getAttribute('data-k'), cur = k === 'theme' ? themePref() : (html.getAttribute('data-' + k) || '');
      $$('button', s).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === cur)); });
    });
  }
  function a11yDialog() {
    if (!a11yLayer) {
      var themes = (html.getAttribute('data-skins') || 'auto:Auto,light:Light,dark:Dark').split(',');
      var tb = themes.map(function (t) { var p = t.split(':'); return '<button type="button" data-v="' + p[0] + '">' + p[1] + '</button>'; }).join('');
      function row(t, dsc, k, opts) { return '<div class="ui-row"><span><b>' + t + '</b><span class="d">' + dsc + '</span></span><span class="ui-seg" data-k="' + k + '">' + opts + '</span></div>'; }
      a11yLayer = makeLayer('ui-a11y', 'Display &amp; accessibility', '<div class="ui-body">' +
        row(html.getAttribute('data-skins') ? 'Skin' : 'Theme', 'Follows your system by default', 'theme', tb) +
        row('Text size', 'Scales the whole page', 'size', '<button type="button" data-v="" aria-label="Normal">A</button><button type="button" data-v="l" aria-label="Large" style="font-size:1.1em">A</button><button type="button" data-v="xl" aria-label="Extra large" style="font-size:1.25em">A</button>') +
        row('High contrast', 'Pure black and white surfaces', 'contrast', '<button type="button" data-v="">Off</button><button type="button" data-v="high">On</button>') +
        row('Motion', 'Stops animations', 'motion', '<button type="button" data-v="">On</button><button type="button" data-v="off">Off</button>') +
        row('Underline links', 'Easier to spot links', 'links', '<button type="button" data-v="">Off</button><button type="button" data-v="underline">On</button>') +
        row('Reading spacing', 'Wider letter and line spacing', 'spacing', '<button type="button" data-v="">Off</button><button type="button" data-v="wide">On</button>') + '</div>');
      a11yLayer.addEventListener('click', function (e) {
        var b = e.target.closest && e.target.closest('.ui-seg button'); if (!b) return;
        var s = b.parentNode, k = s.getAttribute('data-k'), v = b.getAttribute('data-v');
        if (k === 'theme') { W.VLTheme.set(v); return; }
        setPref(k, v);
      });
    }
    syncSeg(); open(a11yLayer);
  }
  function setPref(k, v) {
    if (v) html.setAttribute('data-' + k, v); else html.removeAttribute('data-' + k);
    store(k, v); syncSeg(); d.dispatchEvent(new CustomEvent('vl:pref', { detail: { k: k, v: v } }));
  }
  W.VLPref = setPref;

  /* ---------------- Search palette ---------------- */
  var palLayer = null;
  function palette() {
    var IDX = W.VL_INDEX || [];
    if (!palLayer) {
      palLayer = makeLayer('ui-pal', '', '<div class="ui-pal-in"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.3-4.3"/></svg><label class="ui-sr" for="ui-pq">Search the whole site</label><input id="ui-pq" type="search" autocomplete="off" placeholder="Open media… search ' + IDX.length + ' pages"><kbd>Esc</kbd></div><ul class="ui-res" id="ui-pr" role="listbox"></ul>', true, 'ui-pal');
      $('.ui-card', palLayer).setAttribute('aria-label', 'Search');
      var q = $('#ui-pq', palLayer), list = $('#ui-pr', palLayer), sel = 0;
      function base() { return ROOT + OPT + '/'; }
      function render() {
        var v = q.value.toLowerCase().trim(), out = [], words = v.split(/\s+/);
        for (var i = 0; i < IDX.length && out.length < 40; i++) {
          var it = IDX[i], hay = (it[1] + ' ' + it[2] + ' ' + it[0]).toLowerCase(), ok = true;
          for (var w = 0; w < words.length; w++) if (words[w] && hay.indexOf(words[w]) < 0) { ok = false; break; }
          if (ok) out.push(it);
        }
        sel = 0;
        list.innerHTML = out.length ? out.map(function (it, i) { return '<li><a href="' + base() + (it[0] === 'home' ? 'index.html' : 'p/' + it[0] + '.html') + '"' + (i === 0 ? ' class="on"' : '') + '><b>' + esc(it[1]) + '</b><span class="s">' + esc(it[2]) + '</span></a></li>'; }).join('') : '<li class="empty">No page matches “' + esc(v) + '”.</li>';
      }
      q.addEventListener('input', render);
      q.addEventListener('keydown', function (e) {
        var as = $$('a', list); if (!as.length) return;
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); as[sel].className = ''; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + as.length) % as.length; as[sel].className = 'on'; as[sel].scrollIntoView({ block: 'nearest' }); }
        if (e.key === 'Enter') { e.preventDefault(); location.href = as[sel].getAttribute('href'); }
      });
      render();
    }
    $('#ui-pq', palLayer).value = ''; $('#ui-pq', palLayer).dispatchEvent(new Event('input'));
    open(palLayer, '#ui-pq');
  }
  W.VLSearch = palette;

  /* ================= DONATE ================= */
  var dn = null, state = { freq: 'once', cur: 'EUR', amt: 10, method: 'card' };
  function sym() { return state.cur === 'EUR' ? '€' : '$'; }
  function buildDonate() {
    var h = '<div class="dn" id="ui-donate" role="dialog" aria-modal="true" aria-labelledby="dn-title" aria-hidden="true">' +
      '<button type="button" class="ui-x dn-close" data-dn-close aria-label="Close donation">×</button>' +
      '<div class="dn-grid">' +
      '<section class="dn-story"><div class="dn-brand">' + CONE + 'VideoLAN</div><div class="dn-cone">' + CONE + '</div>' +
      '<h2 id="dn-title">Keep VLC <em>free</em>. For everyone, forever.</h2>' +
      '<p>No ads, no tracking, no company behind it. VLC is made by volunteers and run by a small non-profit. Every donation goes straight to the project.</p>' +
      '<ul class="dn-uses"><li><b>Hardware</b>Discs, capture cards and devices to test against</li><li><b>Servers</b>Downloads and services used by millions every day</li><li><b>Events</b>VideoLAN Dev Days and FOSDEM</li><li><b>Independence</b>No investors, no data sold, ever</li></ul>' +
      '<p class="dn-legal">VideoLAN is a non-profit association under the French law of 1 July 1901. Donations stay with the association; no profits are distributed to its members.</p></section>' +
      '<section class="dn-pay">' +
      '<div><span class="dn-step">1 · How often</span><div class="dn-row2"><div class="dn-seg" data-dn="freq"><button type="button" data-v="once" aria-pressed="true">One time</button><button type="button" data-v="month" aria-pressed="false">Monthly</button></div>' +
      '<div class="dn-seg" data-dn="cur"><button type="button" data-v="EUR" aria-pressed="true">€ EUR</button><button type="button" data-v="USD" aria-pressed="false">$ USD</button></div></div></div>' +
      '<div><span class="dn-step">2 · Amount</span><div class="dn-amts" id="dn-amts"></div>' +
      '<label class="dn-custom"><span id="dn-sym">€</span><span class="ui-sr">Custom amount</span><input id="dn-custom" inputmode="decimal" placeholder="Other amount" autocomplete="off"></label></div>' +
      '<div><span class="dn-step">3 · Pay in one click</span><div class="dn-express">' +
      '<button type="button" class="dn-wallet" data-pay="applepay" aria-label="Donate with Apple Pay">' + ICO.apple + '<span>Pay</span></button>' +
      '<button type="button" class="dn-wallet" data-pay="googlepay" aria-label="Donate with Google Pay">' + ICO.gpay + '<span>Pay</span></button></div>' +
      '<div id="dn-prb" style="margin-top:.6rem"></div></div>' +
      '<div class="dn-or">or choose a method</div>' +
      '<div class="dn-methods" role="group" aria-label="Payment method">' +
      '<button type="button" data-m="card" aria-pressed="true">' + ICO.card + 'Card</button>' +
      '<button type="button" data-m="sepa" aria-pressed="false">' + ICO.sepa + 'SEPA debit</button>' +
      '<button type="button" data-m="paypal" aria-pressed="false">' + ICO.paypal + 'PayPal</button>' +
      '<button type="button" data-m="bank" aria-pressed="false">' + ICO.bank + 'Bank transfer</button>' +
      '<button type="button" data-m="btc" aria-pressed="false">' + ICO.btc + 'Bitcoin</button>' +
      '<button type="button" data-m="other" aria-pressed="false">' + ICO.info + 'More</button></div>' +
      '<div class="dn-panel" data-p="card"><div id="dn-elements"><div class="dn-field"><label>Card</label><div class="dn-element">' + ICO.card + '<span>Secure card field (Stripe Elements)</span></div></div>' +
      '<div class="dn-split"><div class="dn-field"><label for="dn-email">Email for the receipt</label><input class="dn-input" id="dn-email" type="email" autocomplete="email" placeholder="you@example.org"></div><div class="dn-field"><label for="dn-country">Country</label><input class="dn-input" id="dn-country" autocomplete="country-name" placeholder="France"></div></div></div>' +
      '<p class="dn-note">' + ICO.lock + '<span id="dn-card-note">Card details are entered on Stripe’s secure checkout. VideoLAN never sees your card number.</span></p></div>' +
      '<div class="dn-panel" data-p="sepa" hidden><p class="dn-note" style="margin:0">' + ICO.info + '<span>SEPA Direct Debit is available for euro donations from eligible European bank accounts. You’ll confirm your IBAN on Stripe’s secure page.</span></p></div>' +
      '<div class="dn-panel" data-p="paypal" hidden><p class="dn-note" style="margin:0">' + ICO.info + '<span>You’ll continue on PayPal. No PayPal account is needed, and there is no minimum amount. Monthly donations are supported.</span></p></div>' +
      '<div class="dn-panel" data-p="bank" hidden><div class="dn-copy"><div><small>Account holder</small><code>' + CONFIG.holder + ', France</code></div></div><div class="dn-copy"><div><small>IBAN</small><code>' + CONFIG.iban + '</code></div><button type="button" data-copy="' + CONFIG.iban.replace(/ /g, '') + '">Copy</button></div><div class="dn-copy"><div><small>BIC / SWIFT</small><code>' + CONFIG.bic + '</code></div><button type="button" data-copy="' + CONFIG.bic + '">Copy</button></div></div>' +
      '<div class="dn-panel" data-p="btc" hidden><div class="dn-qr"><img alt="Bitcoin QR code for VideoLAN" width="120" height="120" data-src="' + CONFIG.bitcoinQR + '"><div style="min-width:0;flex:1"><div class="dn-copy"><div><small>Bitcoin address</small><code>' + CONFIG.bitcoin + '</code></div><button type="button" data-copy="' + CONFIG.bitcoin + '">Copy</button></div><a class="ui-btn" href="bitcoin:' + CONFIG.bitcoin + '">Open in wallet</a></div></div></div>' +
      '<div class="dn-panel" data-p="other" hidden><p class="dn-note" style="margin:0 0 .6rem">' + ICO.info + '<span>Prefer to give time or hardware? Developers, translators, writers, testers and designers are all welcome.</span></p><div class="ui-btns"><a class="ui-btn" href="' + ROOT + OPT + '/p/contribute.html">Ways to contribute</a><a class="ui-btn" href="' + ROOT + OPT + '/p/contact.html">Contact VideoLAN</a></div></div>' +
      '<div class="dn-status" id="dn-status" role="status" aria-live="polite"></div>' +
      '<button type="button" class="ui-btn primary dn-cta" id="dn-cta">' + ICO.lock.replace('<svg', '<svg width="20" height="20"') + '<span id="dn-cta-t">Donate €10</span></button>' +
      '<div class="dn-trust"><span>' + ICO.check + 'Secure checkout by Stripe</span><span>' + ICO.check + 'No account needed</span><span>' + ICO.check + 'Receipt by email</span></div>' +
      '</section></div></div>';
    dn = el(h); d.body.appendChild(dn);
    dn.addEventListener('keydown', function (e) { trap(dn, e); });
    dn.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target : null; if (!t) return;
      if (t.closest('[data-dn-close]')) { closeDonate(); return; }
      var seg = t.closest('.dn-seg button');
      if (seg) { var k = seg.parentNode.getAttribute('data-dn'); state[k] = seg.getAttribute('data-v'); $$('button', seg.parentNode).forEach(function (b) { b.setAttribute('aria-pressed', String(b === seg)); }); renderAmts(); update(); return; }
      var a = t.closest('#dn-amts button');
      if (a) { state.amt = +a.getAttribute('data-a'); $('#dn-custom', dn).value = ''; renderAmts(); update(); return; }
      var m = t.closest('.dn-methods button');
      if (m) { state.method = m.getAttribute('data-m'); $$('.dn-methods button', dn).forEach(function (b) { b.setAttribute('aria-pressed', String(b === m)); }); $$('.dn-panel', dn).forEach(function (p) { p.hidden = p.getAttribute('data-p') !== state.method; }); if (state.method === 'btc') { var im = $('img[data-src]', dn); if (im && !im.src) im.src = im.getAttribute('data-src'); } update(); return; }
      var c = t.closest('[data-copy]');
      if (c) { copy(c.getAttribute('data-copy')); c.textContent = 'Copied'; setTimeout(function () { c.textContent = 'Copy'; }, 1800); return; }
      var w = t.closest('[data-pay]');
      if (w) { pay(w.getAttribute('data-pay')); return; }
      if (t.closest('#dn-cta')) { pay(state.method); }
    });
    $('#dn-custom', dn).addEventListener('input', function () { var v = parseFloat(this.value.replace(',', '.')); if (v > 0) { state.amt = v; renderAmts(true); update(); } });
    renderAmts(); update();
    if (CONFIG.stripePublishableKey) mountStripe();
  }
  function renderAmts(keepCustom) {
    var list = state.freq === 'month' ? [3, 5, 10, 20, 30, 50] : [5, 10, 25, 50, 100, 250];
    var lbl = { 5: 'A coffee', 10: 'Most popular', 25: 'A month of bandwidth', 3: 'Every bit helps', 20: 'Supporter', 50: 'Champion', 100: 'Test hardware', 250: 'Patron', 30: 'Sustainer' };
    if (!keepCustom && list.indexOf(state.amt) < 0 && !$('#dn-custom', dn).value) state.amt = list[1];
    $('#dn-amts', dn).innerHTML = list.map(function (v) { return '<button type="button" data-a="' + v + '" aria-pressed="' + (v === state.amt && !$('#dn-custom', dn).value) + '">' + sym() + v + '<small>' + (lbl[v] || '') + '</small></button>'; }).join('');
    $('#dn-sym', dn).textContent = sym();
  }
  function fmt() { var a = Math.round(state.amt * 100) / 100; return sym() + (a % 1 ? a.toFixed(2) : a); }
  function update() {
    var t = state.method === 'bank' || state.method === 'btc' || state.method === 'other';
    var cta = $('#dn-cta', dn); cta.style.display = t ? 'none' : '';
    var suffix = state.freq === 'month' ? ' per month' : '';
    var via = { card: '', sepa: ' by SEPA debit', paypal: ' with PayPal' }[state.method] || '';
    $('#dn-cta-t', dn).textContent = 'Donate ' + fmt() + suffix + via;
    if (state.method === 'sepa' && state.cur !== 'EUR') { state.cur = 'EUR'; $$('[data-dn="cur"] button', dn).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === 'EUR')); }); renderAmts(); $('#dn-cta-t', dn).textContent = 'Donate ' + fmt() + suffix + via; }
    $('#dn-card-note', dn).textContent = state.freq === 'month' ? 'Monthly card donations use Stripe subscriptions. You can cancel at any time from the link in your receipt.' : 'Card details are entered on Stripe’s secure checkout. VideoLAN never sees your card number.';
  }
  function copy(t) { try { navigator.clipboard.writeText(t); } catch (e) { var i = d.createElement('textarea'); i.value = t; d.body.appendChild(i); i.select(); try { d.execCommand('copy'); } catch (x) {} i.remove(); } toast('Copied to clipboard.'); }
  function post(action, fields) {
    var f = d.createElement('form'); f.method = 'post'; f.action = action; f.style.display = 'none';
    for (var k in fields) { var i = d.createElement('input'); i.type = 'hidden'; i.name = k; i.value = fields[k]; f.appendChild(i); }
    d.body.appendChild(f); f.submit();
  }
  function status(m) { var s = $('#dn-status', dn); s.textContent = m; s.className = 'dn-status show'; }
  function pay(method) {
    var amount = (Math.round(state.amt * 100) / 100).toFixed(2);
    if (!(state.amt >= 1)) { toast('Please choose an amount of at least ' + sym() + '1.'); return; }
    if (method === 'paypal') {
      status('Opening PayPal…');
      var f = { business: CONFIG.paypalBusiness, item_name: 'Development and communication of VideoLAN', currency_code: state.cur, no_note: '0', 'return': CONFIG.paypalReturn, lc: state.cur === 'EUR' ? 'GB' : 'US' };
      if (state.freq === 'month') { f.cmd = '_xclick-subscriptions'; f.a3 = amount; f.p3 = '1'; f.t3 = 'M'; f.src = '1'; f.sra = '1'; }
      else { f.cmd = '_xclick'; f.amount = amount; }
      post('https://www.paypal.com/cgi-bin/webscr', f); return;
    }
    if (stripe && prButton && (method === 'applepay' || method === 'googlepay')) { return; } // native sheet handled by Stripe button
    // Stripe Checkout (hosted). Apple Pay / Google Pay / Link / cards / SEPA appear automatically on Stripe's page.
    status('Opening secure Stripe checkout…' + (method === 'applepay' ? ' Apple Pay appears on supported devices.' : method === 'googlepay' ? ' Google Pay appears in supported browsers.' : ''));
    var fields = { currency: state.cur, amount: amount };
    if (state.freq === 'month') fields.interval = 'month';
    if (method === 'sepa') fields.method = 'sepa_debit';
    var em = $('#dn-email', dn).value; if (em) fields.email = em;
    post(CONFIG.stripeCheckoutUrl, fields);
  }
  /* Embedded Stripe (activates only when a publishable key is configured; no third-party request otherwise) */
  var stripe = null, prButton = null;
  function mountStripe() {
    var s = d.createElement('script'); s.src = 'https://js.stripe.com/v3/'; s.onload = function () {
      try {
        stripe = W.Stripe(CONFIG.stripePublishableKey);
        var pr = stripe.paymentRequest({ country: 'FR', currency: state.cur.toLowerCase(), total: { label: 'Donation to VideoLAN', amount: Math.round(state.amt * 100) }, requestPayerEmail: true });
        var els = stripe.elements();
        pr.canMakePayment().then(function (r) { if (r) { prButton = els.create('paymentRequestButton', { paymentRequest: pr }); prButton.mount('#dn-prb'); } });
        var card = els.create('card'); var host = $('#dn-elements .dn-element', dn); host.innerHTML = ''; card.mount(host);
        pr.on('paymentmethod', function (ev) { /* VideoLAN backend: create PaymentIntent, then stripe.confirmCardPayment(clientSecret, {payment_method: ev.paymentMethod.id}) */ ev.complete('success'); });
      } catch (e) { stripe = null; }
    };
    d.head.appendChild(s);
  }
  function openDonate(amt) {
    if (!dn) buildDonate();
    if (amt) { state.amt = amt; renderAmts(); update(); }
    lastFocus = d.activeElement; dn.classList.add('open'); dn.setAttribute('aria-hidden', 'false'); html.style.overflow = 'hidden';
    $('#dn-status', dn).className = 'dn-status';
    setTimeout(function () { var b = $('#dn-amts button[aria-pressed="true"]', dn) || $('#dn-amts button', dn); b.focus(); }, 40);
    if (history.replaceState && location.hash !== '#donate') history.replaceState(null, '', location.pathname + location.search + '#donate');
  }
  function closeDonate() {
    dn.classList.remove('open'); dn.setAttribute('aria-hidden', 'true'); html.style.overflow = '';
    if (history.replaceState && location.hash === '#donate') history.replaceState(null, '', location.pathname + location.search);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  W.VLDonate = openDonate;

  /* ---------------- Global click routing ---------------- */
  d.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var t = e.target.closest ? e.target.closest('a, [data-donate], [data-ui-open]') : null; if (!t) return;
    if (t.hasAttribute('data-donate')) { e.preventDefault(); openDonate(+t.getAttribute('data-donate') || 0); return; }
    var o = t.getAttribute('data-ui-open');
    if (o) { e.preventDefault(); if (o === 'lang') langDialog(); else if (o === 'a11y') a11yDialog(); else if (o === 'search') palette(); return; }
    if (t.tagName !== 'A') return;
    var href = t.getAttribute('href') || '';
    if (/contribute\.html#money$/.test(href) || href === '#donate') { e.preventDefault(); openDonate(); return; }
    if (t.hasAttribute('data-dl') || t.closest('.ui-layer')) return;
    if (!/^https?:/i.test(href)) return;
    var host = (t.hostname || '').toLowerCase();
    if (OWNED.test(host) && !DIRECT.test(host)) { e.preventDefault(); extNotice(t.href, host); }
  });
  d.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase(); if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) return;
    if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !openLayer)) { e.preventDefault(); palette(); }
    if (e.key === 'Escape' && dn && dn.classList.contains('open')) closeDonate();
  });

  /* Hide images that fail to load (legacy assets on the current site) */
  d.addEventListener('error', function (e) { var t = e.target; if (t && t.tagName === 'IMG' && !t.closest('.dn')) { t.style.display = 'none'; } }, true);

  /* ---------------- Init ---------------- */
  if (store('lang')) setLang(store('lang'), true);
  if (true) { applyTheme(themePref()); if (W.matchMedia) { var mq = matchMedia('(prefers-color-scheme: dark)'); if (mq.addEventListener) mq.addEventListener('change', function () { if (themePref() === 'auto') applyTheme('auto'); }); } }
  switcher();
  if (location.hash === '#donate') setTimeout(openDonate, 50);
})();
