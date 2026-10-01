/* Option C — Almanac behaviour. ES5. */
(function () {
  'use strict';
  var d = document, html = d.documentElement, W = window;
  function $(s, c) { return (c || d).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); }

  // Day / night edition
  function syncEd() { var dark = html.getAttribute('data-theme') === 'dark'; $$('.c-ed').forEach(function (x) { x.textContent = dark ? 'Day edition' : 'Night edition'; }); }
  d.addEventListener('click', function (e) {
    var b = e.target.closest('[data-c-act]'); if (!b) return;
    var a = b.getAttribute('data-c-act');
    if (a === 'night') { W.VLTheme.toggle(); syncEd(); }
    if (a === 'nav') { var on = html.classList.toggle('c-navopen'); b.setAttribute('aria-expanded', String(on)); }
  });
  d.addEventListener('vl:theme', syncEd); setTimeout(syncEd, 0);

  // Download button tailored to the reader's system
  var dl = $('#c-dl');
  if (dl) {
    var ua = navigator.userAgent || '', pf = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '', V = '3.0.24', t = null;
    if (/Android/i.test(ua)) t = ['VLC for Android', 'p/vlc--download-android.html', 'Free on Google Play and F-Droid'];
    else if (/iPhone|iPad|iPod/i.test(ua) || (/Mac/i.test(pf) && navigator.maxTouchPoints > 1)) t = ['VLC for iPhone & iPad', 'p/vlc--download-ios.html', 'Free on the App Store'];
    else if (/Win/i.test(pf)) t = ['VLC ' + V + ' for Windows', 'https://get.videolan.org/vlc/' + V + '/win64/vlc-' + V + '-win64.exe', '64-bit installer · free · no ads'];
    else if (/Mac/i.test(pf)) t = ['VLC ' + V + ' for macOS', 'https://get.videolan.org/vlc/' + V + '/macosx/vlc-' + V + '-universal.dmg', 'Universal · Apple Silicon & Intel'];
    else if (/Linux|X11|CrOS|BSD/i.test(pf + ua)) t = ['VLC for Linux', 'p/section--download.html', 'From your distribution'];
    if (t) { $('#c-dl-t').textContent = t[0]; dl.href = t[1]; $('#c-dl-s').textContent = t[2]; if (/get\.videolan/.test(t[1])) dl.setAttribute('data-dl', ''); }
  }

  // Reveal on scroll
  var els = $$('.c-banner, .c-chart, .c-sec, .c-letter');
  if ('IntersectionObserver' in W && html.classList.contains('motion')) {
    $$('.c-sec, .c-letter').forEach(function (x) { x.classList.add('c-rv'); });
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -10% 0px' });
    els.forEach(function (x) { io.observe(x); });
  } else els.forEach(function (x) { x.classList.add('in'); });

  // Format wall: type to find a format
  var wall = $('#c-wall');
  if (wall) {
    var box = d.createElement('div');
    box.innerHTML = '<label style="display:flex;gap:.8rem;align-items:center;margin:0 0 1.2rem;font:800 .8rem/1 var(--sans);text-transform:uppercase;letter-spacing:.12em">Does VLC play it? <input type="search" id="c-wq" placeholder="Type a format, e.g. FLAC" style="flex:1;max-width:320px;min-height:46px;border:3px solid var(--rule);background:var(--paper);color:var(--ink);padding:0 .8rem;font:700 1rem var(--sans);text-transform:none;letter-spacing:0"></label><p id="c-wa" aria-live="polite" style="margin:-.6rem 0 1rem;font:italic 1.05rem var(--serif);min-height:1.5em"></p>';
    wall.parentNode.insertBefore(box, wall);
    var spans = $$('span', wall), q = $('#c-wq'), ans = $('#c-wa');
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase(), n = 0;
      if (!v) { wall.classList.remove('lit'); ans.textContent = ''; spans.forEach(function (s) { s.classList.remove('hit'); }); return; }
      wall.classList.add('lit');
      spans.forEach(function (s) { var h = s.textContent.toLowerCase().indexOf(v) > -1; s.classList.toggle('hit', h); if (h) n++; });
      ans.textContent = n ? 'Yes. ' + n + ' match' + (n > 1 ? 'es' : '') + ' on the wall, built in, no codec pack needed.' : 'Not on this wall. VLC probably still plays it — see the full feature list.';
    });
  }

  // TOC highlight
  var toc = $$('.c-toc a');
  if (toc.length && 'IntersectionObserver' in W) {
    var map = {}; toc.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var io2 = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { toc.forEach(function (a) { a.classList.remove('on'); }); if (map[en.target.id]) map[en.target.id].classList.add('on'); } }); }, { rootMargin: '0px 0px -75% 0px' });
    Object.keys(map).forEach(function (id) { var t = d.getElementById(id); if (t) io2.observe(t); });
  }
})();
