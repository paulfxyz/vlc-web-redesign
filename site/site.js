/* videolan.org redesign — one small script, ES5, no dependencies.
   Everything works without it; it only adds: OS-aware download, dialogs (language,
   display, search, exit notices, donation checkout), tabs, copy buttons and effects. */
(function () {
  'use strict';
  var d = document, W = window, html = d.documentElement, L = W.VL || {};
  var ROOT = html.getAttribute('data-root') || '', BASE = html.getAttribute('data-base') || '', SLUG = html.getAttribute('data-slug') || 'home';
  var LANG = html.getAttribute('data-lang') || 'en', RTL = html.getAttribute('dir') === 'rtl';
  var FX = function () { return /\bfx\b/.test(html.className); };

  /* ---------- helpers */
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  function el(h) { var x = d.createElement('div'); x.innerHTML = h; return x.firstElementChild || x.firstChild; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function T(k, o) { var v = L[k] || k; if (o) for (var x in o) v = v.split('{' + x + '}').join(o[x]); return v; }
  function store(k, v) { try { if (arguments.length === 1) return localStorage.getItem('vl-' + k); if (v) localStorage.setItem('vl-' + k, v); else localStorage.removeItem('vl-' + k); } catch (e) { return null; } }
  function ico(n, c) { return '<svg class="' + (c || 'ic') + '" aria-hidden="true"><use href="' + ROOT + 'icons.svg#i-' + n + '"/></svg>'; }
  function closest(t, s) { while (t && t.nodeType === 1) { if (matches(t, s)) return t; t = t.parentNode; } return null; }
  function matches(n, s) { var f = n.matches || n.msMatchesSelector || n.webkitMatchesSelector; return f ? f.call(n, s) : false; }
  function mb(n) { return T('mb', { n: Math.round(n / 1048576) }); }
  var CONE = '<svg viewBox="0 0 64 64" aria-hidden="true"><use href="' + ROOT + 'icons.svg#i-cone"/></svg>';

  /* ---------- toast */
  var toastEl, toastT;
  function toast(m) {
    if (!toastEl) { toastEl = el('<div class="toast" role="status" aria-live="polite"></div>'); d.body.appendChild(toastEl); }
    toastEl.textContent = m; toastEl.className = 'toast on'; clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.className = 'toast'; }, 5200);
  }
  function copy(txt, btn) {
    function done() { toast(T('js_copied')); if (btn) { var o = btn.innerHTML; btn.innerHTML = ico('check') + esc(T('dl_copied')); setTimeout(function () { btn.innerHTML = o; }, 1600); } }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, fallback); else fallback();
    function fallback() { var i = d.createElement('textarea'); i.value = txt; i.setAttribute('readonly', ''); i.style.position = 'fixed'; i.style.opacity = '0'; d.body.appendChild(i); i.select(); try { d.execCommand('copy'); } catch (e) {} d.body.removeChild(i); done(); }
  }

  /* ---------- layers */
  var openL = null, lastF = null;
  function focusables(c) { return $$('a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])', c).filter(function (x) { return x.offsetWidth || x.offsetHeight; }); }
  function onKey(e) {
    if (!openL) return;
    if (e.key === 'Escape' || e.keyCode === 27) { e.preventDefault(); closeL(); return; }
    if (e.key !== 'Tab') return;
    var f = focusables(openL); if (!f.length) return;
    if (e.shiftKey && d.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && d.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  }
  d.addEventListener('keydown', onKey);
  function openLayer(L_, focusSel) {
    if (openL) closeL(true);
    lastF = d.activeElement; openL = L_; L_.className += ' open'; L_.removeAttribute('aria-hidden'); html.style.overflow = 'hidden';
    setTimeout(function () { var f = (focusSel && $(focusSel, L_)) || focusables(L_)[0]; if (f) f.focus(); }, 40);
  }
  function closeL(silent) {
    if (!openL) return; var L_ = openL; openL = null;
    L_.className = L_.className.replace(/\s*open\b/g, ''); L_.setAttribute('aria-hidden', 'true'); html.style.overflow = '';
    if (L_.id === 'dn' && history.replaceState && location.hash === '#donate') history.replaceState(null, '', location.pathname + location.search);
    if (!silent && lastF && lastF.focus) lastF.focus();
  }
  function layer(id, title, body, wide) {
    var x = el('<div class="ly" id="' + id + '" aria-hidden="true"><div class="scrim" data-x></div><div class="dg' + (wide ? ' wide' : '') + '" role="dialog" aria-modal="true"' + (title ? ' aria-labelledby="' + id + '-t"' : ' aria-label="' + esc(T('search')) + '"') + '>' +
      (title ? '<div class="dg-h"><h2 id="' + id + '-t">' + title + '</h2><button type="button" class="x" data-x aria-label="' + esc(T('close')) + '">' + ico('x') + '</button></div>' : '') + body + '</div></div>');
    d.body.appendChild(x);
    x.addEventListener('click', function (e) { if (closest(e.target, '[data-x]')) closeL(); });
    return x;
  }

  /* ---------- exit notices (download / not redesigned / leaving) */
  var OWNED = /(^|\.)videolan\.(org|me)$|(^|\.)videolabs\.io$/i;
  var NAMES = { 'wiki.videolan.org': 'x_names_wiki', 'forum.videolan.org': 'x_names_forum', 'code.videolan.org': 'x_names_code', 'addons.videolan.org': 'x_names_addons', 'docs.videolan.me': 'x_names_docs' };
  var xL = null;
  function exitNotice(a) {
    var href = a.href, host = (a.hostname || '').toLowerCase(), isDl = a.hasAttribute('data-dl') && !/\/$/.test(a.pathname || '');
    if (!xL) xL = layer('xl', '<span id="xl-h"></span>', '<div class="dg-b"><div class="xi" id="xl-i"></div><p id="xl-p"></p><div id="xl-x"></div><div class="btns"><a class="btn btn-or" id="xl-go" href="#" rel="noopener"></a><button type="button" class="btn btn-gh" data-x>' + esc(T('x_stay')) + '</button></div></div>');
    var go = $('#xl-go', xL), x = $('#xl-x', xL);
    go.setAttribute('href', href);
    if (isDl) {
      var name = decodeURIComponent((a.pathname || '').split('/').pop()), sha = a.getAttribute('data-sha'), size = a.getAttribute('data-size');
      $('#xl-h', xL).textContent = T('x_dl_h'); $('#xl-i', xL).innerHTML = CONE;
      $('#xl-p', xL).textContent = T('x_dl_p');
      x.innerHTML = '<dl class="xf"><dt>' + esc(T('x_file')) + '</dt><dd>' + esc(name) + '</dd>' + (size ? '<dt>' + esc(T('x_size')) + '</dt><dd>' + esc(mb(+size)) + '</dd>' : '') + '<dt>' + esc(T('x_from')) + '</dt><dd>' + esc(host) + '</dd></dl>' +
        (sha ? '<p style="font-size:.88rem;margin-bottom:.4rem">' + esc(T('x_dl_after')) + '</p><div class="cpr"><div><small>SHA-256</small><code style="font-size:.74rem">' + sha + '</code></div><button type="button" class="cp" data-copy="' + sha + '">' + ico('copy') + esc(T('dl_copy')) + '</button></div>' : '');
      go.innerHTML = ico('download') + esc(T('x_dl_go'));
    } else if (OWNED.test(host)) {
      $('#xl-h', xL).textContent = T('x_vl_h'); $('#xl-i', xL).innerHTML = CONE;
      $('#xl-p', xL).innerHTML = esc(T('x_vl_p')).replace('{name}', '<b>' + esc(T(NAMES[host] || 'x_names_other')) + '</b>');
      x.innerHTML = '<div class="url">' + esc(href) + '</div>'; go.innerHTML = esc(T('x_continue')) + ico('ext');
    } else {
      $('#xl-h', xL).textContent = T('x_out_h'); $('#xl-i', xL).innerHTML = ico('ext');
      $('#xl-p', xL).innerHTML = esc(T('x_out_p')).replace('{host}', '<b>' + esc(host.replace(/^www\./, '')) + '</b>');
      x.innerHTML = '<div class="url">' + esc(href) + '</div>'; go.innerHTML = esc(T('x_continue')) + ico('ext');
    }
    openLayer(xL, '#xl-go');
  }

  /* ---------- theme & display */
  function themePref() { return store('theme') || 'auto'; }
  function applyTheme() {
    var p = themePref(), dk = p === 'dark' || (p === 'auto' && W.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches);
    html.setAttribute('data-theme', dk ? 'dark' : 'light');
    $$('[data-open="theme"]').forEach(function (b) { b.innerHTML = ico(dk ? 'sun' : 'moon'); b.setAttribute('aria-label', b.getAttribute(dk ? 'data-l-light' : 'data-l-dark')); });
    sync();
  }
  if (W.matchMedia) { var mq = matchMedia('(prefers-color-scheme: dark)'); var f = function () { if (themePref() === 'auto') applyTheme(); }; if (mq.addEventListener) mq.addEventListener('change', f); else if (mq.addListener) mq.addListener(f); }
  var aL = null;
  function sync() {
    if (!aL) return;
    $$('.sg', aL).forEach(function (s) { var k = s.getAttribute('data-k'), cur = k === 'theme' ? themePref() : (html.getAttribute('data-' + k) || ''); $$('button', s).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === cur)); }); });
  }
  function setPref(k, v) {
    if (k === 'theme') { store('theme', v === 'auto' ? '' : v); applyTheme(); return; }
    if (v) html.setAttribute('data-' + k, v); else html.removeAttribute('data-' + k);
    store(k, v);
    if (k === 'motion') { if (v === 'off') html.className = html.className.replace(/\s*\bfx\b/g, ''); else if (!FX() && !(W.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches)) { html.className += ' fx'; reveal(); } }
    sync();
  }
  function a11y() {
    if (!aL) {
      function row(t, ds, k, o) { return '<div class="row"><span><b>' + esc(T(t)) + '</b><span class="d">' + esc(T(ds)) + '</span></span><span class="sg" role="group" aria-label="' + esc(T(t)) + '" data-k="' + k + '">' + o + '</span></div>'; }
      function b(v, l, st) { return '<button type="button" data-v="' + v + '"' + (st ? ' style="' + st + '"' : '') + '>' + l + '</button>'; }
      var on = esc(T('js_on')), off = esc(T('js_off'));
      aL = layer('al', esc(T('display')), '<div class="dg-b">' +
        row('js_theme', 'js_follow', 'theme', b('auto', esc(T('js_auto'))) + b('light', esc(T('js_light'))) + b('dark', esc(T('js_dark')))) +
        row('js_size', 'js_scale', 'size', '<button type="button" data-v="" aria-label="' + esc(T('js_n')) + '">A</button><button type="button" data-v="l" aria-label="' + esc(T('js_l')) + '" style="font-size:1.1em">A</button><button type="button" data-v="xl" aria-label="' + esc(T('js_xl')) + '" style="font-size:1.25em">A</button>') +
        row('js_contrast', 'js_bw', 'contrast', b('', off) + b('high', on)) +
        row('js_motion', 'js_stop', 'motion', b('', on) + b('off', off)) +
        row('js_links', 'js_spot', 'links', b('', off) + b('underline', on)) +
        row('js_spacing', 'js_wide', 'spacing', b('', off) + b('wide', on)) + '</div>');
      aL.addEventListener('click', function (e) { var x = closest(e.target, '.sg button'); if (x) setPref(x.parentNode.getAttribute('data-k'), x.getAttribute('data-v')); });
    }
    sync(); openLayer(aL);
  }

  /* ---------- languages */
  var LANGS = [["en","English","English"],["fr","Français","French"],["zh-Hans","简体中文","Chinese (Simplified)"],["ar","العربية","Arabic"],["de","Deutsch","German"],["es","Español","Spanish"],["pt-PT","Português (Portugal)","Portuguese"],["pt-BR","Português (Brasil)","Brazilian Portuguese"],["it","Italiano","Italian"],["nl","Nederlands","Dutch"],["pl","Polski","Polish"],["ru","Русский","Russian"],["uk","Українська","Ukrainian"],["cs","Čeština","Czech"],["sk","Slovenčina","Slovak"],["hu","Magyar","Hungarian"],["ro","Română","Romanian"],["bg","Български","Bulgarian"],["el","Ελληνικά","Greek"],["tr","Türkçe","Turkish"],["he","עברית","Hebrew"],["fa","فارسی","Persian"],["ur","اردو","Urdu"],["ps","پښتو","Pashto"],["hi","हिन्दी","Hindi"],["bn","বাংলা","Bengali"],["pa","ਪੰਜਾਬੀ","Punjabi"],["gu","ગુજરાતી","Gujarati"],["mr","मराठी","Marathi"],["ta","தமிழ்","Tamil"],["te","తెలుగు","Telugu"],["kn","ಕನ್ನಡ","Kannada"],["ml","മലയാളം","Malayalam"],["si","සිංහල","Sinhala"],["ne","नेपाली","Nepali"],["th","ไทย","Thai"],["vi","Tiếng Việt","Vietnamese"],["id","Bahasa Indonesia","Indonesian"],["ms","Bahasa Melayu","Malay"],["fil","Filipino","Filipino"],["zh-Hant","繁體中文","Chinese (Traditional)"],["ja","日本語","Japanese"],["ko","한국어","Korean"],["sv","Svenska","Swedish"],["nb","Norsk bokmål","Norwegian"],["da","Dansk","Danish"],["fi","Suomi","Finnish"],["is","Íslenska","Icelandic"],["et","Eesti","Estonian"],["lv","Latviešu","Latvian"],["lt","Lietuvių","Lithuanian"],["sl","Slovenščina","Slovenian"],["hr","Hrvatski","Croatian"],["sr","Српски","Serbian"],["bs","Bosanski","Bosnian"],["mk","Македонски","Macedonian"],["sq","Shqip","Albanian"],["ca","Català","Catalan"],["eu","Euskara","Basque"],["gl","Galego","Galician"],["cy","Cymraeg","Welsh"],["ga","Gaeilge","Irish"],["br","Brezhoneg","Breton"],["oc","Occitan","Occitan"],["eo","Esperanto","Esperanto"],["sw","Kiswahili","Swahili"],["af","Afrikaans","Afrikaans"],["zu","isiZulu","Zulu"],["am","አማርኛ","Amharic"],["ha","Hausa","Hausa"],["yo","Yorùbá","Yoruba"],["kk","Қазақ тілі","Kazakh"],["uz","Oʻzbekcha","Uzbek"],["az","Azərbaycanca","Azerbaijani"],["ka","ქართული","Georgian"],["hy","Հայերեն","Armenian"],["mn","Монгол","Mongolian"],["km","ភាសាខ្មែរ","Khmer"],["lo","ລາວ","Lao"],["my","မြန်မာ","Burmese"],["ku","Kurdî","Kurdish"]];
  var RTLS = { ar: 1, he: 1, fa: 1, ur: 1, ps: 1 }, AV = L._avail || { en: '' };
  var curLang = { en: 'en', fr: 'fr', zh: 'zh-Hans', ar: 'ar' }[LANG];
  function langUrl(code) { var dir = AV[code]; return ROOT + (dir ? dir + '/' : '') + (SLUG === 'home' ? 'index.html' : 'p/' + SLUG + '.html') + (SLUG === 'home' ? location.hash.replace('#donate', '') : ''); }
  var lL = null;
  function langs() {
    if (!lL) {
      var b = '';
      LANGS.forEach(function (l) {
        var ok = l[0] in AV, dir = RTLS[l[0].split('-')[0]] ? ' dir="rtl"' : '';
        var s = esc((l[1] + ' ' + l[2] + ' ' + l[0]).toLowerCase());
        b += ok ? '<a href="' + langUrl(l[0]) + '" hreflang="' + l[0] + '" lang="' + l[0] + '" data-s="' + s + '"' + (l[0] === curLang ? ' aria-current="true"' : '') + '><b' + dir + '>' + l[1] + '</b><span>' + esc(T('js_available')) + '</span></a>'
          : '<button type="button" lang="' + l[0] + '" data-l="' + l[0] + '" data-s="' + s + '"><b' + dir + '>' + l[1] + '</b><span lang="' + (curLang) + '">' + esc(T('js_soon')) + '</span></button>';
      });
      lL = layer('ll', esc(T('js_lang_title')), '<div class="dg-b"><label class="sr" for="lq">' + esc(T('js_lang_title')) + '</label><input class="srch" id="lq" type="search" autocomplete="off" placeholder="' + esc(T('js_lang_search', { n: LANGS.length })) + '">' +
        '<p class="note">' + ico('info') + '<span>' + esc(T('js_lang_note')) + '</span></p><div class="lg" id="lgs">' + b + '</div><p class="lgc" id="lgc" aria-live="polite"></p></div>', true);
      var q = $('#lq', lL), items = $$('#lgs > *', lL);
      var filt = function () { var v = q.value.toLowerCase().replace(/^\s+|\s+$/g, ''), n = 0; items.forEach(function (x) { var hit = !v || x.getAttribute('data-s').indexOf(v) > -1; x.style.display = hit ? '' : 'none'; if (hit) n++; }); $('#lgc', lL).textContent = T('js_count', { a: n, b: items.length }); };
      q.addEventListener('input', filt); filt();
      lL.addEventListener('click', function (e) {
        var x = closest(e.target, 'button[data-l]'); if (!x) return;
        var code = x.getAttribute('data-l'), name = ''; LANGS.forEach(function (l) { if (l[0] === code) name = l[1]; });
        store('lang-wish', code); closeL(); toast(T('js_lang_soon', { l: name }));
      });
    }
    openLayer(lL, '#lq');
  }

  /* ---------- search palette (index loaded on demand) */
  var sL = null;
  function loadIndex(cb) { if (W.VL_INDEX) return cb(); var s = d.createElement('script'); s.src = ROOT + 'search.js'; s.onload = cb; d.head.appendChild(s); }
  function search() {
    if (!sL) {
      sL = layer('sl', '', '<div class="pal-in">' + ico('search') + '<label class="sr" for="sq">' + esc(T('search')) + '</label><input id="sq" type="search" autocomplete="off"></div><ul class="res" id="sr" role="listbox"></ul>', true);
      var q = $('#sq', sL), list = $('#sr', sL), sel = 0;
      var render = function () {
        var IDX = W.VL_INDEX || [], v = q.value.toLowerCase().replace(/^\s+|\s+$/g, ''), out = [], ws = v.split(/\s+/);
        for (var i = 0; i < IDX.length && out.length < 40; i++) {
          var it = IDX[i], hay = (it[1] + ' ' + it[0] + ' ' + (L._secs[it[2]] || '')).toLowerCase(), ok = true;
          for (var w = 0; w < ws.length; w++) if (ws[w] && hay.indexOf(ws[w]) < 0) { ok = false; break; }
          if (ok) out.push(it);
        }
        sel = 0;
        list.innerHTML = out.length ? out.map(function (it, i) { return '<li><a href="' + BASE + 'p/' + it[0] + '.html"' + (i === 0 ? ' class="on"' : '') + '><b lang="en">' + esc(it[1]) + '</b><span>' + esc(L._secs[it[2]] || '') + '</span></a></li>'; }).join('') : '<li class="empty">' + esc(T('search_none', { q: v })) + '</li>';
      };
      q.addEventListener('input', render);
      q.addEventListener('keydown', function (e) {
        var as = $$('a', list); if (!as.length) return;
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); as[sel].className = ''; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + as.length) % as.length; as[sel].className = 'on'; as[sel].scrollIntoView({ block: 'nearest' }); }
        if (e.key === 'Enter') { e.preventDefault(); location.href = as[sel].getAttribute('href'); }
      });
      sL._r = render;
    }
    var q = $('#sq', sL); q.value = '';
    loadIndex(function () { q.setAttribute('placeholder', T('search_ph', { n: (W.VL_INDEX || []).length })); sL._r(); });
    openLayer(sL, '#sq');
  }

  /* ================= DONATE ================= */
  var CFG = W.VL_DONATE_CONFIG || {};
  var DC = {
    checkout: CFG.stripeCheckoutUrl || 'https://www.videolan.org/stripe/checkout.php',
    pk: CFG.stripePublishableKey || '',
    paypal: 'sponsor@videolan.org', ret: 'https://www.videolan.org/thank_you.html',
    iban: 'FR76 3000 3034 3000 1506 8853 588', bic: 'SOGEFRPP', holder: 'VIDEOLAN',
    btc: 'bc1q27wp4frlsckghy3vgdjg4rnlsxztxca0f2r4a7', btcQR: 'https://images.videolan.org/images/bitcoin-bc1q27wp4frlsckghy3vgdjg4rnlsxztxca0f2r4a7.png'
  };
  var dn = null, st = { freq: 'once', cur: 'EUR', amt: 10, m: 'card', custom: false };
  var LOC = { en: 'en-GB', fr: 'fr-FR', zh: 'zh-CN', ar: 'ar-u-nu-latn' }[LANG] || 'en';
  function money(a) {
    try { return new Intl.NumberFormat(LOC, { style: 'currency', currency: st.cur, minimumFractionDigits: a % 1 ? 2 : 0, maximumFractionDigits: 2 }).format(a); }
    catch (e) { return (st.cur === 'EUR' ? '€' : '$') + a; }
  }
  function buildDonate() {
    var u = ['d_u1', 'd_u2', 'd_u3', 'd_u4'], ui = ['cpu', 'stream', 'users', 'shield'];
    var h = '<div class="dn" id="dn" role="dialog" aria-modal="true" aria-labelledby="dn-t" aria-hidden="true">' +
      '<button type="button" class="x dn-x" data-x aria-label="' + esc(T('close')) + '">' + ico('x') + '</button><div class="dn-g">' +
      '<section class="dn-s"><div class="dn-brand">' + CONE + 'VideoLAN</div><div class="dn-cone">' + CONE + '</div>' +
      '<h2 id="dn-t">' + T('d_title') + '</h2><p>' + esc(T('d_story')) + '</p>' +
      '<ul class="dn-u">' + u.map(function (k, i) { return '<li>' + ico(ui[i]) + esc(T(k)) + '</li>'; }).join('') + '</ul><p class="dn-legal">' + esc(T('d_legal')) + '</p></section>' +
      '<section class="dn-p"><div class="dn-pi">' +
      '<div><p class="dn-st">1 · ' + esc(T('d_freq')) + '</p><div class="dn-r2"><div class="dsg" data-k="freq"><button type="button" data-v="once" aria-pressed="true">' + esc(T('d_once')) + '</button><button type="button" data-v="month" aria-pressed="false">' + esc(T('d_month')) + '</button></div>' +
      '<div class="dsg" data-k="cur"><button type="button" data-v="EUR" aria-pressed="true">€ EUR</button><button type="button" data-v="USD" aria-pressed="false">$ USD</button></div></div></div>' +
      '<div><p class="dn-st">2 · ' + esc(T('d_amount')) + '</p><div class="dn-a" id="dn-a"></div><label class="dn-c"><span id="dn-sym">€</span><span class="sr">' + esc(T('d_other')) + '</span><input id="dn-in" inputmode="decimal" placeholder="' + esc(T('d_other')) + '" autocomplete="off"></label></div>' +
      '<div><p class="dn-st">3 · ' + esc(T('d_express')) + '</p><div class="dn-e"><button type="button" class="wal" data-pay="applepay" aria-label="Apple Pay">' + ico('applef') + 'Pay</button><button type="button" class="wal" data-pay="googlepay" aria-label="Google Pay">' + ico('gpay') + 'Pay</button></div><div id="dn-prb"></div></div>' +
      '<div class="or">' + esc(T('d_or')) + '</div>' +
      '<div class="dn-m" role="group" aria-label="' + esc(T('d_or')) + '">' + [['card', 'card', 'd_card'], ['sepa', 'sepa', 'd_sepa'], ['paypal', 'paypal', 'd_paypal'], ['bank', 'bank', 'd_bank'], ['btc', 'btc', 'd_btc'], ['other', 'users', 'd_more']].map(function (m, i) { return '<button type="button" data-m="' + m[0] + '" aria-pressed="' + (i === 0) + '">' + ico(m[1]) + esc(T(m[2])) + '</button>'; }).join('') + '</div>' +
      '<div class="dn-pn" data-p="card"><p class="dn-n">' + ico('lock') + '<span id="dn-cn"></span></p></div>' +
      '<div class="dn-pn" data-p="sepa" hidden><p class="dn-n">' + ico('info') + '<span>' + esc(T('d_sepa_note')) + '</span></p></div>' +
      '<div class="dn-pn" data-p="paypal" hidden><p class="dn-n">' + ico('info') + '<span>' + esc(T('d_paypal_note')) + '</span></p></div>' +
      '<div class="dn-pn" data-p="bank" hidden>' + cpr(T('d_holder'), DC.holder + ', France') + cpr('IBAN', DC.iban, DC.iban.replace(/ /g, '')) + cpr('BIC / SWIFT', DC.bic, DC.bic) + '</div>' +
      '<div class="dn-pn" data-p="btc" hidden><div class="qr"><img alt="Bitcoin QR" width="116" height="116" data-src="' + DC.btcQR + '"><div style="min-width:0;flex:1">' + cpr(T('d_btc_addr'), DC.btc, DC.btc) + '<a class="btn btn-gh btn-sm" href="bitcoin:' + DC.btc + '">' + esc(T('d_wallet')) + '</a></div></div></div>' +
      '<div class="dn-pn" data-p="other" hidden><p class="dn-n" style="margin-bottom:.8rem">' + ico('info') + '<span>' + esc(T('d_more_note')) + '</span></p><a class="btn btn-gh btn-sm" href="' + BASE + 'p/contribute.html">' + esc(T('d_ways')) + '</a></div>' +
      '<div class="dn-sts" id="dn-sts" role="status" aria-live="polite"></div>' +
      '<button type="button" class="btn btn-or dn-cta" id="dn-go">' + ico('lock') + '<span id="dn-gt"></span></button>' +
      '<div class="dn-tr"><span>' + ico('check') + esc(T('d_trust1')) + '</span><span>' + ico('check') + esc(T('d_trust2')) + '</span><span>' + ico('check') + esc(T('d_trust3')) + '</span></div><p class="dn-legal2">' + esc(T('d_legal')) + '</p>' +
      '</div></section></div></div>';
    function cpr(lbl, val, c) { return '<div class="cpr"><div><small>' + esc(lbl) + '</small><code>' + esc(val) + '</code></div>' + (c ? '<button type="button" class="cp" data-copy="' + esc(c) + '">' + ico('copy') + esc(T('dl_copy')) + '</button>' : '') + '</div>'; }
    dn = el(h); d.body.appendChild(dn);
    dn.addEventListener('click', function (e) {
      var t = e.target;
      if (closest(t, '[data-x]')) { closeL(); return; }
      var s = closest(t, '.dsg button');
      if (s) { st[s.parentNode.getAttribute('data-k')] = s.getAttribute('data-v'); $$('button', s.parentNode).forEach(function (b) { b.setAttribute('aria-pressed', String(b === s)); }); amts(); upd(); return; }
      var a = closest(t, '#dn-a button');
      if (a) { st.amt = +a.getAttribute('data-a'); st.custom = false; $('#dn-in', dn).value = ''; amts(); upd(); return; }
      var m = closest(t, '.dn-m button');
      if (m) { st.m = m.getAttribute('data-m'); $$('.dn-m button', dn).forEach(function (b) { b.setAttribute('aria-pressed', String(b === m)); }); $$('.dn-pn', dn).forEach(function (p) { p.hidden = p.getAttribute('data-p') !== st.m; }); if (st.m === 'btc') { var im = $('img[data-src]', dn); if (im && !im.getAttribute('src')) im.src = im.getAttribute('data-src'); } upd(); return; }
      var w = closest(t, '[data-pay]'); if (w) { pay(w.getAttribute('data-pay')); return; }
      if (closest(t, '#dn-go')) pay(st.m);
    });
    $('#dn-in', dn).addEventListener('input', function () { var v = parseFloat(this.value.replace(',', '.')); if (v > 0) { st.amt = v; st.custom = true; amts(); upd(); } });
    amts(); upd();
    if (DC.pk) mountStripe();
  }
  function amts() {
    var once = st.freq === 'once', list = once ? [5, 10, 25, 50, 100, 250] : [3, 5, 10, 20, 30, 50];
    var lbl = once ? { 5: 'd_l1', 10: 'd_l2', 25: 'd_l3', 50: 'd_l4', 100: 'd_l5', 250: 'd_l6' } : { 5: 'd_l1', 10: 'd_l2', 50: 'd_l4' };
    if (!st.custom && list.indexOf(st.amt) < 0) st.amt = once ? 10 : 5;
    $('#dn-a', dn).innerHTML = list.map(function (v) { return '<button type="button" data-a="' + v + '" aria-pressed="' + (v === st.amt && !st.custom) + '">' + esc(money(v)) + '<small>' + (lbl[v] ? esc(T(lbl[v])) : '&nbsp;') + '</small></button>'; }).join('');
    $('#dn-sym', dn).textContent = st.cur === 'EUR' ? '€' : '$';
  }
  function upd() {
    if (st.m === 'sepa' && st.cur !== 'EUR') { st.cur = 'EUR'; $$('[data-k="cur"] button', dn).forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-v') === 'EUR')); }); amts(); }
    var hide = st.m === 'bank' || st.m === 'btc' || st.m === 'other', a = money(Math.round(st.amt * 100) / 100);
    $('#dn-go', dn).style.display = hide ? 'none' : '';
    $('#dn-gt', dn).textContent = st.m === 'paypal' ? T('d_cta_pp', { a: a + (st.freq === 'month' ? ' / ' + T('d_month') : '') }) : st.m === 'sepa' ? T('d_sepa_cta', { a: a }) : T(st.freq === 'month' ? 'd_cta_m' : 'd_cta', { a: a });
    $('#dn-cn', dn).textContent = st.freq === 'month' ? T('d_card_month') : T('d_card_note');
  }
  function post(action, fields) {
    var f = d.createElement('form'); f.method = 'post'; f.action = action; f.style.display = 'none';
    for (var k in fields) { var i = d.createElement('input'); i.type = 'hidden'; i.name = k; i.value = fields[k]; f.appendChild(i); }
    d.body.appendChild(f); f.submit();
  }
  function sts(m) { var s = $('#dn-sts', dn); s.textContent = m; s.className = 'dn-sts on'; }
  function pay(method) {
    if (!(st.amt >= 1)) { toast(T('d_min', { a: money(1) })); return; }
    var amount = (Math.round(st.amt * 100) / 100).toFixed(2);
    if (method === 'paypal') {
      sts(T('d_opening_pp'));
      var f = { business: DC.paypal, item_name: 'Development and communication of VideoLAN', currency_code: st.cur, no_note: '0', 'return': DC.ret, lc: LANG === 'fr' ? 'FR' : LANG === 'zh' ? 'C2' : 'US' };
      if (st.freq === 'month') { f.cmd = '_xclick-subscriptions'; f.a3 = amount; f.p3 = '1'; f.t3 = 'M'; f.src = '1'; f.sra = '1'; } else { f.cmd = '_xclick'; f.amount = amount; }
      post('https://www.paypal.com/cgi-bin/webscr', f); return;
    }
    if (prb && (method === 'applepay' || method === 'googlepay')) return;
    sts(T('d_opening') + (method === 'applepay' || method === 'googlepay' ? ' ' + T('d_wallet_note') : ''));
    var fl = { currency: st.cur, amount: amount }; if (st.freq === 'month') fl.interval = 'month'; if (method === 'sepa') fl.method = 'sepa_debit';
    post(DC.checkout, fl);
  }
  var prb = null;
  function mountStripe() {
    var s = d.createElement('script'); s.src = 'https://js.stripe.com/v3/';
    s.onload = function () { try { var sp = W.Stripe(DC.pk), pr = sp.paymentRequest({ country: 'FR', currency: st.cur.toLowerCase(), total: { label: 'VideoLAN', amount: Math.round(st.amt * 100) }, requestPayerEmail: true }), els = sp.elements(); pr.canMakePayment().then(function (r) { if (r) { prb = els.create('paymentRequestButton', { paymentRequest: pr }); prb.mount('#dn-prb'); } }); pr.on('paymentmethod', function (ev) { ev.complete('success'); }); } catch (e) {} };
    d.head.appendChild(s);
  }
  function donate() {
    if (!dn) buildDonate();
    lastF = d.activeElement; if (openL) closeL(true); openL = dn; dn.className = 'dn open'; dn.removeAttribute('aria-hidden'); html.style.overflow = 'hidden';
    $('#dn-sts', dn).className = 'dn-sts';
    setTimeout(function () { var b = $('#dn-a button[aria-pressed="true"]', dn) || $('#dn-a button', dn); if (b) b.focus(); }, 50);
    if (history.replaceState && location.hash !== '#donate') history.replaceState(null, '', location.pathname + location.search + '#donate');
  }

  /* ---------- global clicks */
  d.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var t = e.target, c;
    if ((c = closest(t, '[data-copy]'))) { e.preventDefault(); copy(c.getAttribute('data-copy'), c); return; }
    if ((c = closest(t, '[data-rib-close]'))) { e.preventDefault(); store('rib', 'off'); html.className += ' rib-off'; var mn = $('#main'); if (mn) mn.focus(); return; }
    if ((c = closest(t, '[data-donate]'))) { e.preventDefault(); donate(); return; }
    if ((c = closest(t, '[data-open]'))) {
      e.preventDefault(); var o = c.getAttribute('data-open');
      if (o === 'lang') langs(); else if (o === 'a11y') a11y(); else if (o === 'search') search(); else if (o === 'theme') { setPref('theme', html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'); }
      return;
    }
    if ((c = closest(t, '[data-tab]')) && $('#download-x, #dlp-x')) { e.preventDefault(); selectOS(c.getAttribute('data-tab'), true); return; }
    var a = closest(t, 'a'); if (!a) return;
    // close open <details> menus
    var href = a.getAttribute('href') || '';
    if (/contribute\.html#money$/.test(href)) { e.preventDefault(); donate(); return; }
    if (closest(a, '#xl')) { if (a.id === 'xl-go') setTimeout(function () { closeL(true); }, 50); return; }
    if (!/^https?:/i.test(href) && !a.hasAttribute('data-dl')) return;
    if (a.hostname && a.hostname === location.hostname && !a.hasAttribute('data-dl')) return;
    e.preventDefault(); exitNotice(a);
  });
  d.addEventListener('click', function (e) { $$('details[open]').forEach(function (x) { if (!x.contains(e.target)) x.removeAttribute('open'); }); }, true);
  d.addEventListener('keydown', function (e) {
    var tg = (e.target.tagName || '').toLowerCase(); if (tg === 'input' || tg === 'textarea' || e.target.isContentEditable) return;
    if (((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !openL)) { e.preventDefault(); search(); }
    if (e.key === 'Escape') $$('details[open]').forEach(function (x) { x.removeAttribute('open'); });
  });

  /* ---------- OS detection + smart CTA */
  var UA = navigator.userAgent || '', OS = 'windows', ARCH = '64';
  if (/Android/i.test(UA)) OS = 'android';
  else if (/iPhone|iPad|iPod/i.test(UA) || (/Macintosh/.test(UA) && navigator.maxTouchPoints > 1)) OS = 'ios';
  else if (/Mac/i.test(UA)) OS = 'mac';
  else if (/CrOS/.test(UA)) OS = 'other';
  else if (/Linux|X11|BSD/i.test(UA)) OS = 'linux';
  else if (/Win/i.test(UA)) { if (/ARM64|aarch64/i.test(UA)) ARCH = 'arm'; else if (!/Win64|WOW64|x64|amd64/i.test(UA)) ARCH = '32'; }
  var DL = L._dl || {}, ST = L._store || {};
  function setCTA() {
    var a = $('#cta'); if (!a) return;
    var b = $('#cta-b'), s = $('#cta-s'), u = $('#cta-ico'), f = null, os = '', sub = '', icon = 'windows';
    function file(x) { f = DL[x]; a.setAttribute('href', f.url); a.setAttribute('data-dl', ''); a.setAttribute('data-sha', f.sha); a.setAttribute('data-size', f.size); a.removeAttribute('data-tab'); }
    function link(h) { a.setAttribute('href', h); a.removeAttribute('data-dl'); a.removeAttribute('data-sha'); a.removeAttribute('data-size'); }
    if (OS === 'windows') { file(ARCH === 'arm' ? 'arm64' : ARCH === '32' ? 'win32' : 'win64'); os = T('os_windows'); sub = T(ARCH === 'arm' ? 'dl_arm' : ARCH === '32' ? 'dl_32' : 'dl_64'); }
    else if (OS === 'mac') { file('macu'); os = T('os_mac'); sub = T('dl_universal'); icon = 'apple'; }
    else if (OS === 'linux') { link('#download'); a.setAttribute('data-tab', 'linux'); os = T('os_linux'); sub = 'apt · dnf · pacman · Flatpak · Snap'; icon = 'linux'; }
    else if (OS === 'android') { link(ST.play); os = T('os_android'); sub = 'Google Play · F-Droid'; icon = 'android'; }
    else if (OS === 'ios') { link(ST.ios); os = T('os_ios'); sub = 'App Store · Apple TV'; icon = 'apple'; }
    else { link('#download'); a.setAttribute('data-tab', 'other'); os = 'ChromeOS'; sub = 'Google Play'; icon = 'box'; }
    b.textContent = T(f ? 'cta_download' : 'cta_get');
    s.textContent = T('cta_for', { os: os }) + ' · ' + sub + (f ? ' · ' + mb(f.size) : '');
    u.setAttribute('href', ROOT + 'icons.svg#i-' + icon);
    var dlu = $('.cta-dl use', a); if (dlu) dlu.setAttribute('href', ROOT + 'icons.svg#i-' + (f ? 'download' : (OS === 'linux' || OS === 'other' ? 'chev' : 'ext')));
  }
  function selectOS(k, scroll) {
    var rail = $('.rail'); if (!rail) return;
    $$('[role=tab]', rail).forEach(function (b) { var on = b.getAttribute('data-os') === k; b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
    $$('.dpanel').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== k; });
    if (scroll) { var s = $('#download') || $('.dlx'); if (s) s.scrollIntoView({ behavior: FX() ? 'smooth' : 'auto', block: 'start' }); }
  }
  function initDownload() {
    var rail = $('.rail'); if (!rail) return;
    var det = $('[data-os="' + OS + '"]', rail); if (det) det.className += ' is-det';
    selectOS(OS);
    var pick = OS === 'windows' ? ARCH : '64';
    $$('#dp-windows .seg button').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-a') === pick)); });
    $$('#dp-windows [data-arch]').forEach(function (x) { x.hidden = x.getAttribute('data-arch') !== pick; });
    rail.addEventListener('click', function (e) { var b = closest(e.target, '[role=tab]'); if (b) selectOS(b.getAttribute('data-os')); });
    rail.addEventListener('keydown', tabKeys);
    d.addEventListener('click', function (e) {
      var b = closest(e.target, '.seg button');
      if (b) { var a = b.getAttribute('data-a'); $$('button', b.parentNode).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); $$('#dp-windows [data-arch]').forEach(function (x) { x.hidden = x.getAttribute('data-arch') !== a; }); }
      var dd = closest(e.target, '.distros button');
      if (dd) { var k = dd.getAttribute('data-d'); $$('button', dd.parentNode).forEach(function (x) { x.setAttribute('aria-pressed', String(x === dd)); }); $$('[data-dterm]').forEach(function (x) { x.hidden = x.getAttribute('data-dterm') !== k; }); }
    });
    if (OS === 'linux' && /Fedora/i.test(UA)) { var fb = $('.distros [data-d="fedora"]'); if (fb) fb.click(); }
    if (/^#download/.test(location.hash) && location.hash.length > 10) selectOS(location.hash.slice(10));
  }
  function tabKeys(e) {
    var tabs = $$('[role=tab]', e.currentTarget), i = tabs.indexOf(d.activeElement); if (i < 0) return;
    var n = { ArrowDown: 1, ArrowRight: RTL ? -1 : 1, ArrowUp: -1, ArrowLeft: RTL ? 1 : -1, Home: -99, End: 99 }[e.key]; if (!n) return;
    e.preventDefault(); var j = n === -99 ? 0 : n === 99 ? tabs.length - 1 : (i + n + tabs.length) % tabs.length; tabs[j].focus(); tabs[j].click();
  }
  function initShow() {
    var tl = $('.tabs[role=tablist]'); if (!tl) return;
    tl.addEventListener('click', function (e) {
      var b = closest(e.target, '[role=tab]'); if (!b) return; var k = b.getAttribute('data-show');
      $$('[role=tab]', tl).forEach(function (x) { var on = x === b; x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1; });
      $$('.show').forEach(function (p) { p.hidden = p.id !== 'sp-' + k; });
    });
    tl.addEventListener('keydown', tabKeys);
    var map = { windows: 'win', mac: 'mac', linux: 'lin', android: 'and', ios: 'ios' }[OS];
    if (map && map !== 'win') { var b = $('[data-show="' + map + '"]', tl); if (b) b.click(); }
  }

  /* ---------- effects (only with html.fx) */
  var io = null;
  function reveal() {
    if (!FX()) { $$('.rv').forEach(function (x) { x.className += ' in'; }); return; }
    if (!io) io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.className += ' in'; io.unobserve(en.target); if (en.target.hasAttribute('data-count')) count(en.target); $$('[data-count]', en.target).forEach(count); } }); }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    $$('.rv:not(.in)').forEach(function (x) { io.observe(x); });
  }
  function count(x) {
    var n = +x.getAttribute('data-count'), txt = x.textContent, suf = txt.replace(/[0-9]/g, ''), t0 = null; if (!n || x._c) return; x._c = 1;
    function step(ts) { if (!t0) t0 = ts; var p = Math.min(1, (ts - t0) / 1400), v = Math.round(n * (1 - Math.pow(1 - p, 3))); x.textContent = v + suf; if (p < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  function players() {
    var figs = $$('[data-play]'); if (!figs.length || !FX()) return;
    var vis = [];
    var ob = new IntersectionObserver(function (es) { es.forEach(function (en) { en.target._v = en.isIntersecting; }); });
    figs.forEach(function (f) { f._cur = Math.round(+f.getAttribute('data-dur') * +f.getAttribute('data-p') / 100); f._dur = +f.getAttribute('data-dur'); f._run = true; ob.observe(f);
      f.addEventListener('click', function () { f._run = !f._run; var u = $('.pl use', f); if (u) u.setAttribute('href', ROOT + 'icons.svg#i-' + (f._run ? 'pause' : 'play')); osd(f, f._run ? '▶' : '❚❚'); });
    });
    function fmt(s) { var m = Math.floor(s / 60), x = s % 60; return (m < 10 ? '0' : '') + m + ':' + (x < 10 ? '0' : '') + x; }
    var tick = 0;
    setInterval(function () {
      if (d.hidden) return; tick++;
      figs.forEach(function (f) {
        if (!f._v || !f._run || !FX()) return;
        f._cur = (f._cur + 1) % f._dur; var p = (f._cur / f._dur * 100).toFixed(2);
        $$('.bar', f).forEach(function (b) { b.style.setProperty('--p', p + '%'); });
        $$('.tc', f).forEach(function (t) { t.textContent = fmt(f._cur); });
        if (tick % 4 === 0) { var s = $('.sub[data-subs]', f); if (s) { var l = s.getAttribute('data-subs').split('|'); s._i = ((s._i || 0) + 1) % l.length; s.style.opacity = '0'; setTimeout(function () { s.textContent = l[s._i]; s.style.opacity = '1'; }, 380); } }
        if (tick % 9 === 3 && $('.osd', f)) osd(f, [T('osd_vol') + ' 74%', T('mk_speed'), T('mk_sub_track', { l: { en: 'English', fr: 'Français', zh: '中文', ar: 'العربية' }[LANG] })][(tick / 9 | 0) % 3]);
      });
      $$('[data-tvrow]').forEach(function (r) { if (tick % 3) return; var k = $$('div', r), i = 0; k.forEach(function (x, j) { if (/\bf\b/.test(x.className)) i = j; x.className = ''; }); k[(i + 1) % k.length].className = 'f'; });
      $$('[data-delay]').forEach(function (x) { if (tick % 3) return; var v = ['+250 ms', '+100 ms', '0 ms', '−150 ms']; x._i = ((x._i || 0) + 1) % v.length; x.textContent = v[x._i]; });
    }, 1000);
  }
  function osd(f, txt) { var o = $('.osd', f); if (!o) return; o.textContent = txt; o.className = 'osd on'; clearTimeout(o._t); o._t = setTimeout(function () { o.className = 'osd'; }, 1600); }
  function pointerFx() {
    if (!FX() || !W.matchMedia || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    d.addEventListener('pointermove', function (e) {
      var g = closest(e.target, '.glow'); if (g) { var r = g.getBoundingClientRect(); g.style.setProperty('--mx', (e.clientX - r.left) + 'px'); g.style.setProperty('--my', (e.clientY - r.top) + 'px'); }
    }, { passive: true });
    var stg = $('.stage'), tilt = stg && $('.tilt', stg);
    if (tilt) {
      stg.addEventListener('pointermove', function (e) { var r = stg.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5; tilt.style.setProperty('--ry', ((RTL ? 7 : -7) + x * 8).toFixed(2) + 'deg'); tilt.style.setProperty('--rx', (2 - y * 6).toFixed(2) + 'deg'); });
      stg.addEventListener('pointerleave', function () { tilt.style.removeProperty('--ry'); tilt.style.removeProperty('--rx'); });
    }
  }
  function tocSpy() {
    var links = $$('.toc a'); if (!links.length || !W.IntersectionObserver) return;
    var map = {}; links.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var ob = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { links.forEach(function (a) { a.className = ''; }); var a = map[en.target.id]; if (a) a.className = 'on'; } }); }, { rootMargin: '-15% 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var h = d.getElementById(id); if (h) ob.observe(h); });
  }

  /* ---------- init */
  d.addEventListener('error', function (e) { var t = e.target; if (t && t.tagName === 'IMG' && closest(t, '.prose')) t.style.display = 'none'; }, true);
  applyTheme(); setCTA(); initDownload(); initShow(); reveal(); players(); pointerFx(); tocSpy();
  if (location.hash === '#donate') setTimeout(donate, 60);
  W.VLDonate = donate;
})();
