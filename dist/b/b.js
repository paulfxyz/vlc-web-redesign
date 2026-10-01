/* Option B — Player shell behaviour. ES5. */
(function () {
  'use strict';
  var d = document, html = d.documentElement, W = window;
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }
  function store(k, v) { try { if (arguments.length === 1) return localStorage.getItem('vl-' + k); if (v) localStorage.setItem('vl-' + k, v); else localStorage.removeItem('vl-' + k); } catch (e) { return null; } }
  var main = $('#main'), reduce = (W.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) || html.getAttribute('data-motion') === 'off';

  /* OSD (on-screen display, like VLC) */
  var osd = $('#b-osd'), osdT;
  function OSD(t) { osd.textContent = t; osd.className = 'b-osd show'; clearTimeout(osdT); osdT = setTimeout(function () { osd.className = 'b-osd'; }, 1400); }

  /* Menus: one open at a time, hover switches while open, Esc closes */
  var menus = $$('.b-menu');
  menus.forEach(function (m) {
    m.addEventListener('toggle', function () { if (m.open) menus.forEach(function (x) { if (x !== m) x.open = false; }); });
    m.addEventListener('mouseenter', function () { if (W.innerWidth > 900 && menus.some(function (x) { return x.open; }) && !m.open) m.open = true; });
  });
  d.addEventListener('click', function (e) { if (!e.target.closest('.b-menu')) menus.forEach(function (x) { x.open = false; }); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') menus.forEach(function (x) { if (x.open) { x.open = false; $('summary', x).focus(); } }); });

  /* Layout toggles */
  if (store('b-noside')) html.classList.add('b-noside');
  function toggleSide() {
    if (W.innerWidth <= 900) { html.classList.toggle('b-sideopen'); return; }
    var off = html.classList.toggle('b-noside'); store('b-noside', off ? '1' : ''); OSD(off ? 'Playlist hidden' : 'Playlist');
  }
  function toggleFocus() { var on = html.classList.toggle('b-focus'); OSD(on ? 'Focus mode' : 'Focus mode off'); }
  function drawer() { var on = html.classList.toggle('b-drawer'); $('.b-menubtn').setAttribute('aria-expanded', String(on)); }
  function shuffle() { var I = W.VL_INDEX || []; if (!I.length) return; var it = I[Math.floor(Math.random() * I.length)]; var root = html.getAttribute('data-root'); location.href = root + 'b/' + (it[0] === 'home' ? 'index.html' : 'p/' + it[0] + '.html'); }
  function keys() { W.VLToast && W.VLToast('Space play/pause · N/P next/previous · F focus · Ctrl+L playlist · Ctrl+K open media · + / − text size · D donate'); }
  d.addEventListener('click', function (e) {
    var b = e.target.closest('[data-b-act]'); if (!b) return;
    var a = b.getAttribute('data-b-act'); menus.forEach(function (x) { x.open = false; });
    ({ playlist: toggleSide, focus: toggleFocus, drawer: drawer, shuffle: shuffle, keys: keys }[a] || function () {})();
  });
  main.addEventListener('click', function () { if (html.classList.contains('b-sideopen')) html.classList.remove('b-sideopen'); html.classList.remove('b-drawer'); });

  /* Seek bar = reading position; time = reading time */
  var seek = $('#b-seek'), cur = $('#b-cur'), tot = $('#b-tot'), secs = +tot.getAttribute('data-secs') || 60, dragging = false;
  function fmt(s) { s = Math.max(0, Math.round(s)); return (s / 60 < 10 ? '0' : '') + Math.floor(s / 60) + ':' + (s % 60 < 10 ? '0' : '') + (s % 60); }
  function sync() {
    var max = main.scrollHeight - main.clientHeight, p = max > 0 ? main.scrollTop / max : 0;
    if (!dragging) seek.value = Math.round(p * 1000);
    seek.style.setProperty('--p', (p * 100) + '%');
    cur.textContent = fmt(p * secs);
  }
  main.addEventListener('scroll', function () { if (!raf) raf = requestAnimationFrame(function () { raf = 0; sync(); }); }, { passive: true });
  var raf = 0;
  seek.addEventListener('input', function () { dragging = true; var max = main.scrollHeight - main.clientHeight; main.style.scrollBehavior = 'auto'; main.scrollTop = seek.value / 1000 * max; main.style.scrollBehavior = ''; sync(); });
  seek.addEventListener('change', function () { dragging = false; });
  sync();

  /* Play = gentle auto-scroll (reading mode). Pauses on any user scroll intent. */
  var playing = false, playBtn = $('#b-play'), last = 0, acc = 0;
  function setPlay(on) {
    playing = on; $('use', playBtn) ; playBtn.innerHTML = on ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.5 4.5h4v15h-4zM13.5 4.5h4v15h-4z"/></svg>' : '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 4.5v15l12.5-7.5z"/></svg>';
    playBtn.setAttribute('aria-label', on ? 'Pause auto-scroll' : 'Play: auto-scroll this page');
    OSD(on ? '▶ Play' : '❚❚ Pause'); if (on) { last = 0; requestAnimationFrame(step); }
    if (stage) stageRun(on || !playedOnce);
  }
  function step(t) {
    if (!playing) return;
    if (last) { acc += (t - last) * 0.045; var px = Math.floor(acc); if (px) { acc -= px; main.style.scrollBehavior = 'auto'; main.scrollTop += px; main.style.scrollBehavior = ''; } }
    last = t;
    if (main.scrollTop >= main.scrollHeight - main.clientHeight - 1) { setPlay(false); return; }
    requestAnimationFrame(step);
  }
  var playedOnce = false;
  playBtn.addEventListener('click', function () { playedOnce = true; setPlay(!playing); });
  ['wheel', 'touchstart', 'keydown'].forEach(function (ev) { main.addEventListener(ev, function (e) { if (playing && (ev !== 'keydown' || /Arrow|Page|Home|End/.test(e.key))) setPlay(false); }, { passive: true }); });

  /* Volume = text size */
  var vol = $('#b-vol'), sizes = ['', 'l', 'xl'], names = ['100%', '112%', '125%'];
  function setSize(i, quiet) {
    i = Math.max(0, Math.min(2, i)); if (vol) { vol.value = i; vol.style.setProperty('--p', (i * 50) + '%'); }
    var fx = $('#fx-size'); if (fx) { fx.value = i; fx.style.setProperty('--p', (i * 50) + '%'); }
    if (W.VLPref) W.VLPref('size', sizes[i]); if (!quiet) OSD('Text size ' + names[i]);
  }
  var curSize = Math.max(0, sizes.indexOf(html.getAttribute('data-size') || ''));
  setSize(curSize, true);
  if (vol) vol.addEventListener('input', function () { setSize(+vol.value); });
  var vb = $('#b-volbtn'); if (vb) vb.addEventListener('click', function () { setSize((+vol.value + 1) % 3); });

  /* Hotkeys (VLC-style) */
  d.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase(); if (tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable) return;
    if (d.querySelector('.ui-layer.open, .dn.open')) return;
    var k = e.key;
    if (k === ' ' && !e.target.closest('button, a, summary')) { e.preventDefault(); playedOnce = true; setPlay(!playing); }
    else if ((k === 'l' || k === 'L') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); toggleSide(); }
    else if (e.ctrlKey || e.metaKey || e.altKey) return;
    else if (k === 'f' || k === 'F') toggleFocus();
    else if (k === 'n' || k === 'N') { var n = $('[data-b-key="n"]'); if (n) location.href = n.href; }
    else if (k === 'p' || k === 'P') { var p = $('[data-b-key="p"]'); if (p) location.href = p.href; }
    else if (k === '+' || k === '=') setSize(+vol.value + 1);
    else if (k === '-') setSize(+vol.value - 1);
    else if (k === 'd' || k === 'D') W.VLDonate && W.VLDonate();
    else if (k === '?') keys();
    else if (k === 'v' || k === 'V') { var l = $('[data-ui-open="lang"]'); if (l) l.click(); }
  });

  /* Chapters: highlight current section */
  var chap = $$('.b-chap a');
  if (chap.length && 'IntersectionObserver' in W) {
    var map = {}; chap.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { chap.forEach(function (a) { a.classList.remove('on'); }); var a = map[en.target.id]; if (a) a.classList.add('on'); } }); }, { root: main, rootMargin: '0px 0px -70% 0px' });
    Object.keys(map).forEach(function (id) { var t = d.getElementById(id); if (t) io.observe(t); });
  }
  // keep the current playlist item visible
  var on = $('.b-side a.on'); if (on && on.scrollIntoView) { var sc = $('.b-side-scroll'); sc.scrollTop = on.offsetTop - sc.clientHeight / 2; }

  /* Tabs (ARIA) */
  function tabs(list) {
    var ts = $$('[role="tab"]', list);
    function sel(t, f) { ts.forEach(function (x) { var o = x === t; x.setAttribute('aria-selected', String(o)); x.tabIndex = o ? 0 : -1; var p = d.getElementById(x.getAttribute('aria-controls')); if (p) p.hidden = !o; }); if (f) t.focus(); }
    ts.forEach(function (t, i) { t.addEventListener('click', function () { sel(t); }); t.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') sel(ts[(i + 1) % ts.length], 1); if (e.key === 'ArrowLeft') sel(ts[(i - 1 + ts.length) % ts.length], 1); }); });
    return sel;
  }
  var tabSel = {}; $$('[role="tablist"]').forEach(function (l, i) { tabSel[i] = tabs(l); });

  /* ---------- Home only ---------- */
  var stage = $('.b-stage');
  if (stage) {
    // OS detection: preselect Open Media tab + hero button
    var ua = navigator.userAgent || '', pf = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
    var os = /Android/i.test(ua) ? 'mobile' : /iPhone|iPad|iPod/i.test(ua) || (/Mac/i.test(pf) && navigator.maxTouchPoints > 1) ? 'mobile' : /Win/i.test(pf) ? 'win' : /Mac/i.test(pf) ? 'mac' : /Linux|X11|CrOS|BSD/i.test(pf + ua) ? 'linux' : 'win';
    var V = '3.0.24', T = {
      win: ['Download VLC for Windows', 'Version ' + V + ' · 64-bit · .exe', 'https://get.videolan.org/vlc/' + V + '/win64/vlc-' + V + '-win64.exe'],
      mac: ['Download VLC for macOS', 'Version ' + V + ' · Universal · .dmg', 'https://get.videolan.org/vlc/' + V + '/macosx/vlc-' + V + '-universal.dmg'],
      linux: ['Get VLC for Linux', 'From your distribution', 'p/section--download.html'],
      mobile: [/Android/i.test(ua) ? 'Get VLC for Android' : 'Get VLC for iPhone & iPad', 'Free · no ads · no tracking', /Android/i.test(ua) ? 'p/vlc--download-android.html' : 'p/vlc--download-ios.html']
    }[os];
    var dl = $('#b-dl'); $('#b-dl-t').textContent = T[0]; $('#b-dl-s').textContent = T[1]; dl.href = T[2]; if (/get\.videolan/.test(T[2])) dl.setAttribute('data-dl', '');
    var tb = $('#bt-' + os); if (tb) tb.click();

    // Subtitle track
    var subs = ['Plays files, discs, webcams, devices and streams.', 'No codec packs needed.', 'No spyware. No ads. No user tracking.', 'Runs on Windows, macOS, Linux, Android, iOS and more.', 'Made by volunteers since 1996.', 'Subtitles in 81 languages are on their way. Press V to choose yours.'];
    var si = 0, sub = $('#b-sub span');
    setInterval(function () { if (reduce || !stageVisible) return; si = (si + 1) % subs.length; sub.style.opacity = 0; setTimeout(function () { sub.textContent = subs[si]; sub.style.opacity = 1; }, 380); }, 3600);

    // Skins + fx
    function syncSkins() { var s = html.getAttribute('data-skin') || 'dark'; $$('[data-skin]', $('.b-fx')).forEach(function (b) { if (b.tagName === 'BUTTON') b.setAttribute('aria-pressed', String(b.getAttribute('data-skin') === s)); }); $$('[data-fx]').forEach(function (b) { b.setAttribute('aria-pressed', String((html.getAttribute('data-' + b.getAttribute('data-fx')) || '') === b.getAttribute('data-v'))); }); }
    $$('.b-fx button[data-skin]').forEach(function (b) { b.addEventListener('click', function () { W.VLTheme.set(b.getAttribute('data-skin')); OSD('Skin: ' + b.textContent.trim()); syncSkins(); }); });
    $$('.b-fx [data-fx]').forEach(function (b) { b.addEventListener('click', function () { W.VLPref(b.getAttribute('data-fx'), b.getAttribute('data-v')); if (b.getAttribute('data-fx') === 'motion') { reduce = b.getAttribute('data-v') === 'off'; stageRun(!reduce); } syncSkins(); }); });
    var fx = $('#fx-size'); fx.addEventListener('input', function () { setSize(+fx.value); });
    d.addEventListener('vl:theme', syncSkins); d.addEventListener('vl:pref', syncSkins); setTimeout(syncSkins, 0);

    // Canvas: formats flying out of the cone, like a starfield
    var cv = $('#b-canvas'), cx = cv.getContext && cv.getContext('2d'), words = 'H.264 HEVC AV1 VP9 MPEG-2 MKV WebM MP4 FLAC Opus AAC MP3 DTS TrueHD AC-3 DVD Blu-ray HLS DASH RTSP SRT WebVTT ASS 4K 8K HDR10 360° Theora DivX XviD WMV OGG Vorbis ALAC MIDI DVB UDP RTP SMB NFS UPnP Chromecast ProRes VC-1 Dolby'.split(' ');
    var parts = [], wv = 0, hv = 0, dpr = Math.min(W.devicePixelRatio || 1, 2), running = false, stageVisible = true, lastT = 0;
    function resize() { var r = stage.getBoundingClientRect(); wv = r.width; hv = r.height; cv.width = wv * dpr; cv.height = hv * dpr; }
    function spawn(p, fresh) { p.x = (Math.random() - .5) * 2; p.y = (Math.random() - .5) * 2; p.z = fresh ? Math.random() : 1; p.w = words[(Math.random() * words.length) | 0]; p.o = Math.random() < .28; return p; }
    for (var i = 0; i < 90; i++) parts.push(spawn({}, true));
    function frame(t) {
      if (!running) return;
      if (t - lastT < 30) { requestAnimationFrame(frame); return; } lastT = t;
      cx.setTransform(dpr, 0, 0, dpr, 0, 0); cx.clearRect(0, 0, wv, hv);
      var ox = wv * (wv > 860 ? .78 : .5), oy = hv * (wv > 860 ? .5 : .2);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i]; p.z -= 0.0042; if (p.z <= 0.02) spawn(p);
        var k = 1 / p.z, sx = ox + p.x * k * 110, sy = oy + p.y * k * 70;
        if (sx < -120 || sx > wv + 120 || sy < -60 || sy > hv + 60) { spawn(p); continue; }
        var a = Math.min(1, (1 - p.z) * 1.4) * .85, fs = Math.min(42, 7 + k * 2.2);
        cx.font = '700 ' + fs.toFixed(1) + 'px ui-monospace, Menlo, Consolas, monospace';
        cx.fillStyle = p.o ? 'rgba(255,150,40,' + a + ')' : 'rgba(255,240,225,' + (a * .55) + ')';
        cx.fillText(p.w, sx, sy);
      }
      requestAnimationFrame(frame);
    }
    function stageRun(on) { if (!cx) return; if (on && !reduce && stageVisible) { if (!running) { running = true; requestAnimationFrame(frame); } } else running = false; }
    W.stageRun = stageRun;
    resize(); W.addEventListener('resize', resize);
    if ('IntersectionObserver' in W) new IntersectionObserver(function (es) { stageVisible = es[0].isIntersecting; stageRun(stageVisible); }, { root: main }).observe(stage);
    if (reduce) { /* draw one static frame */ running = true; frame(100); running = false; } else stageRun(true);
  }
  function stageRun(on) { if (W.stageRun) W.stageRun(on); }
})();
