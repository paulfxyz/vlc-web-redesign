#!/usr/bin/env python3
"""Build all three proposals + chooser into dist/."""
import json, re, shutil, subprocess, gzip, pathlib, sys, html as H
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import vlsite as S
from vlsite import e

ROOT = S.ROOT
DIST = ROOT / 'dist'
if DIST.exists() and len(sys.argv) == 1: shutil.rmtree(DIST)
(DIST / "shared").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- shared assets
for f in ['ui.css', 'ui.js', 'favicon.svg']: shutil.copy(ROOT / 'shared' / f, DIST / 'shared' / f)
(DIST / 'shared' / 'search-index.js').write_text('window.VL_INDEX=' + json.dumps(S.search_index(), ensure_ascii=False, separators=(',', ':')) + ';')

CONE = '<svg viewBox="0 0 64 64" aria-hidden="true" class="cone"><use href="#cone"/></svg>'
CONE_DEF = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><clipPath id="conecp"><path d="M27.2 6.5c.9-2.6 8.7-2.6 9.6 0L50 51H14z"/></clipPath>'
            '<symbol id="cone" viewBox="0 0 64 64"><path d="M27.2 6.5c.9-2.6 8.7-2.6 9.6 0L50 51H14z" fill="#ff8800"/><g clip-path="url(#conecp)" fill="#fff"><rect y="19" width="64" height="7"/><rect y="34" width="64" height="7.5"/></g><rect x="6" y="49" width="52" height="9" rx="3.5" fill="#ff8800"/></symbol></defs></svg>')

FORMATS = ("H.264;HEVC;AV1;VP9;VP8;MPEG-1;MPEG-2;MPEG-4 ASP;DivX;XviD;3ivX;H.261;H.263;Cinepak;Theora;Dirac;VC-2;MJPEG;WMV 1;WMV 2;WMV 3;VC-1;Sorenson;DV;On2 VP3;VP5;VP6;Indeo 3;RealVideo;"
           "MP3;MP2;AAC;Vorbis;Opus;AC-3;E-AC-3;TrueHD;MLP;DTS;WMA;FLAC;ALAC;Speex;Musepack;ATRAC3;ATRAC9;WavPack;MOD;TrueAudio;APE;RealAudio;A-law;µ-law;AMR;MIDI;LPCM;ADPCM;QCELP;QDM2;MACE;"
           "SubRip;SSA;ASS;WebVTT;MicroDVD;SubViewer;SAMI;VPlayer;CEA-608;CEA-708;VobSub;USF;DVB subs;CMML;Kate;TTML;"
           "MKV;WebM;MP4;MOV;3GP;AVI;ASF;OGG;OGM;FLV;MXF;NUT;TS;PS;WAV;RealMedia;Matroska 3D;"
           "DVD;Blu-ray;BD-J;VCD;SVCD;Audio CD;DVB-T;DVB-S;DVB-C;ATSC;"
           "HTTP;HTTPS;HLS;DASH;RTSP;RTP;UDP;Multicast;SRT;RIST;MMS;FTP;SFTP;SMB;NFS;UPnP;DLNA;Chromecast;SAP;Bonjour;IPv6;"
           "HDR10;HDR10+;Dolby Vision;10-bit;360° video;Ambisonics;4K;8K;Hardware decoding;0-copy GPU").split(';')

def shell_head(opt, title, desc, root, slug, extra_head='', default_theme='auto', skins=None, body_cls=''):
    sk = f' data-skins="{skins}"' if skins else ''
    tkey = 'vl-theme' if opt == 'a' else 'vl-theme-' + opt
    return f'''<!doctype html>
<html lang="en" dir="ltr" class="no-js" data-opt="{opt}" data-root="{root}" data-slug="{slug}" data-default-theme="{default_theme}"{sk}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc or 'VideoLAN, the home of VLC media player.')}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="{root}shared/favicon.svg" type="image/svg+xml">
<script>(function(){{var d=document.documentElement;d.className=d.className.replace('no-js','js');try{{var s=localStorage,t=s.getItem('{tkey}')||'{default_theme}',mq=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches;var dk=t==='dark'||(t==='auto'&&mq)||(t==='classic'?false:false);d.setAttribute('data-theme',dk?'dark':'light');d.setAttribute('data-skin',t);['contrast','size','motion','links','spacing'].forEach(function(k){{var v=s.getItem('vl-'+k);if(v)d.setAttribute('data-'+k,v);}});if(s.getItem('vl-motion')!=='off'&&!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches))d.className+=' motion';}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="{root}shared/ui.css">
{extra_head}
</head>
<body class="{body_cls}">
{CONE_DEF}'''

def shell_foot(root, scripts=''):
    return f'''<script src="{root}shared/search-index.js" defer></script>
<script src="{root}shared/ui.js" defer></script>
{scripts}
</body>
</html>'''

def page_href(slug, at_home):
    return S.href_for(slug, '', at_home)

def write(path, txt):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt)

def prose(p, at_home=False):
    body = S.rewrite(p['html'], at_home)
    body, t = S.toc(body)
    return body, t

def section_label(p):
    if p.get('hub'): return S.SECTIONS[p['hub']]['label']
    return S.SECTIONS.get(S.sec_key(p), {}).get('label', p['section'])

def meta_bits(p):
    bits = [section_label(p), f"{S.read_min(p['words'])} min read"]
    if p.get('path') and not p.get('virtual'): bits.append('videolan.org' + p['path'])
    return bits

# ================================================================ OPTION A (pages)
def build_a():
    out = DIST / 'a'
    subprocess.run([sys.executable, str(ROOT / 'a' / 'build.py')], check=True)
    # home: post-process links + shared kit
    home = (out / 'index.html').read_text()
    home = S.rewrite(home, at_home=True)
    home = home.replace('<html lang="en" dir="ltr" class="no-js">', '<html lang="en" dir="ltr" class="no-js" data-opt="a" data-root="../" data-slug="home">')
    home = home.replace('<link rel="stylesheet" href="styles.css">', '<link rel="stylesheet" href="styles.css">\n<link rel="stylesheet" href="../shared/ui.css">')
    home = home.replace('<script src="app.js" defer></script>', '<script src="app.js" defer></script>\n<script src="../shared/search-index.js" defer></script>\n<script src="../shared/ui.js" defer></script>')
    (out / 'index.html').write_text(home)
    sprite = (ROOT / 'a' / 'sprite.svg.part').read_text()
    sprite = re.sub(r'^<g fill="none"[^>]*>\n|^</g>\n', '', sprite, flags=re.M)
    nav = [('download', 'Download', '../index.html#download'), ('features', 'Features', '../index.html#features'), ('projects', 'Projects', '../index.html#projects'),
           ('news', 'News', 'news.html'), ('support', 'Support', '../index.html#support'), ('contribute', 'Contribute', '../index.html#contribute'), ('videolan', 'About', '../index.html#videolan')]
    for slug, p in S.ALL.items():
        body, t = prose(p)
        sk = S.sec_key(p) if not p.get('hub') else p['hub']
        navh = ''.join(f'<a href="{h}"' + (' aria-current="page"' if k == sk else '') + f'>{l}</a>' for k, l, h in nav)
        prev, nxt = S.seq(slug)
        pn = ''
        if prev or nxt:
            pn = '<nav class="ap-pn" aria-label="More in this section">' + (f'<a class="card" href="{prev}.html"><span class="tag">Previous</span><h3 style="margin-top:.6rem">{e(S.ALL[prev]["display"])}</h3></a>' if prev else '<span></span>') + (f'<a class="card" href="{nxt}.html" style="text-align:right"><span class="tag">Next</span><h3 style="margin-top:.6rem;justify-content:flex-end">{e(S.ALL[nxt]["display"])}</h3></a>' if nxt else '<span></span>') + '</nav>'
        tochtml = ''
        if len(t) >= 3:
            tochtml = '<aside class="ap-toc"><p class="eyebrow">On this page</p><ul>' + ''.join(f'<li><a href="#{i}">{e(x)}</a></li>' for i, x in t[:18]) + '</ul></aside>'
        html = shell_head('a', p['display'] + ' — VideoLAN', p.get('desc'), '../../', slug, '<link rel="stylesheet" href="../styles.css"><link rel="stylesheet" href="../page.css">', 'auto') + sprite + f'''
<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
<a class="brand" href="../index.html" aria-label="VideoLAN home"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="#i-cone"/></svg><span>VideoLAN<small>Non-profit · Since 1996</small></span></a>
<nav class="nav" aria-label="Main">{navh}</nav>
<div class="tools">
<button type="button" class="icon-btn" data-ui-open="search" aria-label="Search the site"><svg aria-hidden="true"><use href="#i-search"/></svg></button>
<button type="button" class="icon-btn" data-ui-open="lang" aria-label="Change language"><svg aria-hidden="true"><use href="#i-globe"/></svg><span class="lbl-code" data-ui-langlabel="code">EN</span></button>
<button type="button" class="icon-btn" data-ui-open="a11y" aria-label="Display and accessibility"><svg aria-hidden="true"><use href="#i-a11y"/></svg></button>
<button type="button" class="btn btn-ghost btn-sm btn-donate" data-donate><svg aria-hidden="true"><use href="#i-heart"/></svg>Donate</button>
</div></div></header>
<main id="main" tabindex="-1">
<section class="page-hero"><div class="wrap">
<p class="crumbs"><a href="../index.html">Home</a><span aria-hidden="true">/</span><a href="section--{sk}.html">{e(section_label(p))}</a><span aria-hidden="true">/</span><span>{e(p['display'][:60])}</span></p>
<p class="eyebrow">{' · '.join(e(b) for b in meta_bits(p))}</p>
<h1>{e(p['display'])}</h1>
{f'<p class="lede">{e(p["desc"])}</p>' if p.get('desc') and len(p['desc']) < 240 else ''}
</div></section>
<section class="band" style="padding-top:0"><div class="wrap ap-wrap{' has-toc' if tochtml else ''}">
{tochtml}
<article class="ap-prose x-prose">{body}</article>
</div><div class="wrap">{pn}</div></section>
</main>
<footer class="site-footer"><div class="wrap"><div class="foot-bottom" style="margin-top:0;border-top:0;padding-top:0">
<p>VLC, VideoLAN and x264 are registered trademarks of VideoLAN. Unofficial redesign concept by Paul Fleury. <a href="design-notes.html">Design notes</a> · <a href="sitemap.html">Site index</a></p>
<p class="weight">No cookies · No trackers · Static HTML5</p></div></div></footer>
''' + shell_foot('../../')
        write(out / 'p' / f'{slug}.html', html)
    shutil.copy(ROOT / 'a' / 'page.css', out / 'page.css')

# ================================================================ OPTION B
B_MENUS = [
    ('Media', [('Download VLC', 'download', 'Ctrl+D'), ('Windows', 'vlc--download-windows', ''), ('macOS', 'vlc--download-macosx', ''), ('Linux', 'section--download', ''), ('Android', 'vlc--download-android', ''), ('iPhone, iPad & Apple TV', 'vlc--download-ios', ''), ('Source code', 'vlc--download-sources', ''), ('—', '', ''), ('Open media… (search)', '#search', 'Ctrl+K')]),
    ('Playback', [('News', 'news', 'N'), ('Release notes', 'section--releases', ''), (f'VLC {S.VERSION} highlights', f'vlc--releases--{S.VERSION}', ''), ('Security bulletins', 'section--security', ''), ('Press releases', 'section--press', '')]),
    ('Video', [('Features', 'vlc--features', ''), ('Screenshots', 'vlc--screenshots', ''), ('Skins', 'vlc--skins', ''), ('Skin editor', 'vlc--skineditor', ''), ('Goodies', 'goodies', ''), ('Streaming features', 'streaming-features', ''), ('Download statistics', 'vlc--stats--downloads', '')]),
    ('Subtitle', [('Choose language…', '#lang', 'V'), ('Help translate VLC', 'developers--i18n', '')]),
    ('Tools', [('All projects', 'projects', ''), ('libVLC', 'vlc--libvlc', ''), ('dav1d', 'projects--dav1d', ''), ('x264', 'developers--x264', ''), ('DVBlast', 'projects--dvblast', ''), ('multicat', 'projects--multicat', ''), ('VLMa', 'projects--vlma', ''), ('Developer zone', 'developers', '')]),
    ('View', [('Playlist', '#playlist', 'Ctrl+L'), ('Focus mode', '#focus', 'F'), ('Skins & display…', '#a11y', ''), ('Keyboard shortcuts', '#keys', '?'), ('Site index', 'sitemap', '')]),
    ('Help', [('Support', 'support', 'F1'), ('FAQ', 'support--faq', ''), ('Contribute', 'contribute', ''), ('Donate…', '#donate', ''), ('Team & organisation', 'videolan', ''), ('Partners', 'videolan--partners', ''), ('Events', 'videolan--events', ''), ('Legal', 'legal', ''), ('Privacy', 'privacy', ''), ('Contact', 'contact', ''), ('About this redesign', 'design-notes', '')]),
]
BI = {  # tiny icon set for option B (stroke)
 'prev': '<path fill="currentColor" d="M6 5h2.2v14H6zM19 5v14L9.5 12z"/>', 'next': '<path fill="currentColor" d="M15.8 5H18v14h-2.2zM5 5v14l9.5-7z"/>',
 'play': '<path fill="currentColor" d="M7 4.5v15l12.5-7.5z"/>', 'pause': '<path fill="currentColor" d="M6.5 4.5h4v15h-4zM13.5 4.5h4v15h-4z"/>',
 'cc': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M10.5 10.3a2.2 2.2 0 1 0 0 3.4M17 10.3a2.2 2.2 0 1 0 0 3.4"/></g>',
 'vol': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z" fill="currentColor"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/></g>',
 'full': '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></g>',
 'list': '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h11M4 12h11M4 18h7M19 15v6M16 18h6"/></g>',
 'shuffle': '<g fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h4l10 10h4M3 17h4l3-3M14 10l3-3h4M18 4l3 3-3 3M18 14l3 3-3 3"/></g>',
 'heart': '<path fill="currentColor" d="M12 20.5s-8-4.7-8-10.6C4 7 6.1 5 8.6 5c1.5 0 2.7.7 3.4 1.8C12.7 5.7 13.9 5 15.4 5 17.9 5 20 7 20 9.9c0 5.9-8 10.6-8 10.6z"/>',
 'search': '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.3-4.3"/></g>',
 'skin': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a9 9 0 0 0 0 18c1.2 0 1.8-.8 1.8-1.7 0-1.2-1-1.5-1-2.6 0-1 .8-1.7 1.8-1.7H17a4 4 0 0 0 4-4C21 6.6 17 3 12 3z"/><circle cx="7.5" cy="11.5" r="1.1" fill="currentColor"/><circle cx="10" cy="7.5" r="1.1" fill="currentColor"/><circle cx="15" cy="7.5" r="1.1" fill="currentColor"/></g>',
 'menu': '<g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></g>',
 'a11y': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="7.6" r="1.2" fill="currentColor"/><path d="M7.5 10.2 12 11l4.5-.8M12 11v3.2m0 0-2.2 3.8M12 14.2l2.2 3.8"/></g>',
 'eq': '<g fill="currentColor"><rect class="eq1" x="4" y="10" width="3" height="10" rx="1"/><rect class="eq2" x="10.5" y="5" width="3" height="15" rx="1"/><rect class="eq3" x="17" y="8" width="3" height="12" rx="1"/></g>',
 'folder': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2h8.5A1.5 1.5 0 0 1 21 9.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"/></g>',
 'film': '<g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M7.5 4v16M16.5 4v16M3 9h4.5M3 15h4.5M16.5 9H21M16.5 15H21"/></g>',
}
def bi(name, cls=''):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{BI[name]}</svg>'

def b_menu_html(at_home):
    out = ['<nav class="b-menubar" aria-label="Main menu">']
    for name, items in B_MENUS:
        lis = []
        for label, target, key in items:
            if label == '—': lis.append('<li role="separator" class="sep"></li>'); continue
            if target.startswith('#'):
                act = target[1:]
                attr = {'search': 'data-ui-open="search"', 'lang': 'data-ui-open="lang"', 'a11y': 'data-ui-open="a11y"', 'donate': 'data-donate'}.get(act, f'data-b-act="{act}"')
                lis.append(f'<li><button type="button" {attr}><span>{e(label)}</span><kbd>{e(key)}</kbd></button></li>')
            else:
                lis.append(f'<li><a href="{page_href(target, at_home)}"><span>{e(label)}</span><kbd>{e(key)}</kbd></a></li>')
        out.append(f'<details class="b-menu"><summary>{name}</summary><ul>{"".join(lis)}</ul></details>')
    out.append('</nav>')
    return ''.join(out)

def b_sidebar(cur_slug, at_home, chapters):
    cur = S.ALL.get(cur_slug)
    cur_sec = (cur.get('hub') or S.sec_key(cur)) if cur else None
    h = ['<aside class="b-side" id="b-side" aria-label="Playlist"><div class="b-side-head"><span>Playlist</span><button type="button" class="b-ib" data-ui-open="search" aria-label="Search all pages">' + bi('search') + '</button></div>']
    h.append('<div class="b-side-scroll">')
    h.append(f'<a class="b-pl-home{" on" if cur_slug == "home" else ""}" href="{page_href("home", at_home)}">{bi("film")}<span>Home</span>{bi("eq", "b-eq") if cur_slug == "home" else ""}</a>')
    h.append(f'<a class="b-pl-home{" on" if cur_slug == "download" else ""}" href="{page_href("download", at_home)}">{bi("film")}<span>Download VLC {S.VERSION}</span>{bi("eq", "b-eq") if cur_slug == "download" else ""}</a>')
    if chapters:
        h.append('<div class="b-group b-chap"><p class="b-gh">Chapters</p><ol>' + ''.join(f'<li><a href="#{i}"><span class="n">{n+1:02d}</span><span>{e(t)}</span></a></li>' for n, (i, t) in enumerate(chapters[:20])) + '</ol></div>')
    h.append('<p class="b-gh" style="margin-top:.6rem">Media library</p>')
    for k, s in S.SECTIONS.items():
        items = S.ordered(k)
        n = len(items) + (len(S.YEARS) if k == 'news' else 0)
        is_open = k == cur_sec
        h.append(f'<details class="b-group"{" open" if is_open else ""}><summary>{bi("folder")}<span>{e(s["label"])}</span><small>{n}</small></summary><ul>')
        h.append(f'<li><a href="{page_href("section--" + k, at_home)}" class="all">All {e(s["label"].lower())} →</a></li>')
        shown = items if is_open and len(items) <= 60 else items[:8]
        if k == 'news':
            h.append(f'<li><a href="{page_href("news", at_home)}"{" class=on" if cur_slug == "news" else ""}>Latest news</a></li>')
            for y in S.YEARS[:8 if not is_open else 40]:
                sl = 'news--' + y
                h.append(f'<li><a href="{page_href(sl, at_home)}"{" class=on aria-current=page" if cur_slug == sl else ""}>{y}</a></li>')
        else:
            for p in shown:
                on = p['slug'] == cur_slug
                h.append(f'<li><a href="{page_href(p["slug"], at_home)}"' + (' class="on" aria-current="page"' if on else '') + f'>{e(p["display"][:58])}</a></li>')
            if cur and cur_slug not in [p['slug'] for p in shown] and is_open and cur_slug in [p['slug'] for p in items]:
                h.append(f'<li><a class="on" aria-current="page" href="{page_href(cur_slug, at_home)}">{e(cur["display"][:58])}</a></li>')
        h.append('</ul></details>')
    h.append('</div></aside>')
    return ''.join(h)

def b_transport(prev, nxt, at_home, words):
    pv = f'<a class="b-tb" href="{page_href(prev, at_home)}" aria-label="Previous page: {e(S.ALL[prev]["display"])}" data-b-key="p">{bi("prev")}</a>' if prev else f'<span class="b-tb dis" aria-hidden="true">{bi("prev")}</span>'
    nx = f'<a class="b-tb" href="{page_href(nxt, at_home)}" aria-label="Next page: {e(S.ALL[nxt]["display"])}" data-b-key="n">{bi("next")}</a>' if nxt else f'<span class="b-tb dis" aria-hidden="true">{bi("next")}</span>'
    secs = max(30, int(words / 220 * 60))
    tot = f'{secs // 60:02d}:{secs % 60:02d}'
    return f'''<div class="b-transport" role="toolbar" aria-label="Player controls">
{pv}<button type="button" class="b-tb b-play" id="b-play" aria-label="Play: auto-scroll this page">{bi("play")}</button>{nx}
<span class="b-time" id="b-cur">00:00</span>
<label class="b-seek"><span class="ui-sr">Reading position</span><input type="range" id="b-seek" min="0" max="1000" value="0" step="1"></label>
<span class="b-time" id="b-tot" data-secs="{secs}">{tot}</span>
<button type="button" class="b-tb hide-s" data-ui-open="lang" aria-label="Subtitles and language">{bi("cc")}</button>
<span class="b-volw hide-s"><button type="button" class="b-tb" id="b-volbtn" aria-label="Text size">{bi("vol")}</button><label class="b-vol"><span class="ui-sr">Text size</span><input type="range" id="b-vol" min="0" max="2" step="1" value="0"></label></span>
<button type="button" class="b-tb hide-s" data-b-act="shuffle" aria-label="Random page">{bi("shuffle")}</button>
<button type="button" class="b-tb" data-b-act="playlist" aria-label="Toggle playlist">{bi("list")}</button>
<button type="button" class="b-tb hide-s" data-b-act="focus" aria-label="Focus mode">{bi("full")}</button>
<button type="button" class="b-tb b-heart" data-donate aria-label="Donate">{bi("heart")}</button>
</div>'''

def b_shell(slug, title, desc, at_home, main_html, chapters, words, crumbs):
    root = '../' if at_home else '../../'
    prefix = '' if at_home else '../'
    prev, nxt = S.seq(slug) if slug in S.ALL else (None, 'download')
    if slug == 'home': prev, nxt = None, 'download'
    head = shell_head('b', title, desc, root, slug, f'<link rel="stylesheet" href="{prefix}b.css">', 'dark', 'dark:Dark,light:Daylight,classic:Classic 2006')
    return head + f'''
<a class="skip" href="#main">Skip to content</a>
<div class="b-app" id="b-app">
<header class="b-title"><span class="b-dots" aria-hidden="true"><i></i><i></i><i></i></span><a class="b-brand" href="{page_href("home", at_home)}" aria-label="VideoLAN home">{CONE}<b>VLC media player</b></a><span class="b-path" aria-hidden="true">{e(crumbs)}</span>
<span class="b-tools"><button type="button" class="b-ib" data-ui-open="search" aria-label="Open media: search the site">{bi("search")}<span class="hide-s">Open Media…</span><kbd class="hide-s">Ctrl K</kbd></button><button type="button" class="b-ib" data-ui-open="lang" aria-label="Language"><span data-ui-langlabel="code">EN</span></button><button type="button" class="b-ib" data-ui-open="a11y" aria-label="Skins and display">{bi("skin")}</button><button type="button" class="b-donate" data-donate>{bi("heart")}<span>Donate</span></button><button type="button" class="b-ib b-menubtn" data-b-act="drawer" aria-label="Menu" aria-expanded="false">{bi("menu")}</button></span></header>
{b_menu_html(at_home)}
<div class="b-body">
{b_sidebar(slug, at_home, chapters)}
<main class="b-main" id="main" tabindex="-1">{main_html}</main>
</div>
{b_transport(prev, nxt, at_home, words)}
<div class="b-osd" id="b-osd" aria-hidden="true"></div>
</div>
''' + shell_foot(root, f'<script src="{prefix}b.js" defer></script>')

def b_page(p):
    slug = p['slug']
    body, t = prose(p)
    prev, nxt = S.seq(slug)
    sec = section_label(p)
    hub = p.get('hub') or S.sec_key(p)
    pn = ''
    if prev or nxt:
        pn = '<nav class="b-pn" aria-label="Previous and next">' + (f'<a href="{prev}.html"><small>{bi("prev")} Previous</small><b>{e(S.ALL[prev]["display"])}</b></a>' if prev else '<span></span>') + (f'<a href="{nxt}.html" class="r"><small>Next {bi("next")}</small><b>{e(S.ALL[nxt]["display"])}</b></a>' if nxt else '<span></span>') + '</nav>'
    info = ''.join(f'<span>{e(b)}</span>' for b in meta_bits(p))
    main = f'''<div class="b-doc">
<p class="b-kicker"><a href="section--{hub}.html">{e(sec)}</a> <span aria-hidden="true">›</span> <span>Now playing</span></p>
<h1>{e(p["display"])}</h1>
{f'<p class="b-lede">{e(p["desc"])}</p>' if p.get('desc') and len(p['desc']) < 240 else ''}
<div class="b-info">{info}</div>
<article class="b-prose x-prose">{body}</article>
{pn}
<p class="b-foot">VLC, VideoLAN and x264 are trademarks of VideoLAN. Unofficial redesign concept · <a href="design-notes.html">Design notes</a> · <a href="sitemap.html">Site index</a></p>
</div>'''
    crumbs = 'videolan.org' + (p['path'] if p.get('path') else '/' + slug)
    return b_shell(slug, p['display'] + ' — VLC media player', p.get('desc'), False, main, t, p['words'], crumbs)

def b_home():
    news = S.latest_news(8)
    rows = ''.join(f'<tr><td class="n">{i+1}</td><td><a href="{S.href_for(*(S.resolve("https://www.videolan.org/news.html#" + n["id"]) or ("news", "")), True)}">{e(n["title"])}</a></td><td class="d">{S.nice_date(n["date"])}</td></tr>' for i, n in enumerate(news))
    chapters = [('download', 'Download', 'Every platform', 'c1'), ('vlc--features', 'Features', 'Plays everything', 'c2'), ('news', 'News', f'{len(S.NEWS)} stories', 'c3'),
                ('projects', 'Projects', 'x264, dav1d, DVBlast…', 'c4'), ('section--releases', 'Release notes', 'Since VLC 1.1', 'c5'), ('contribute', 'Contribute', 'Time, code, money', 'c6'),
                ('videolan--events', 'Events', 'Dev Days since 2008', 'c7'), ('videolan', 'VideoLAN', 'The non-profit', 'c8')]
    chap = ''.join(f'<a class="b-chapter {c}" href="p/{s}.html"><span class="thumb" aria-hidden="true"><i></i></span><span class="num">{i+1:02d}</span><b>{t}</b><small>{d}</small></a>' for i, (s, t, d, c) in enumerate(chapters))
    tabs = [('win', 'Windows', [('Windows 64-bit', f'vlc-{S.VERSION}-win64.exe', f'https://get.videolan.org/vlc/{S.VERSION}/win64/vlc-{S.VERSION}-win64.exe'), ('Windows ARM64', 'Snapdragon PCs', f'https://get.videolan.org/vlc/{S.VERSION}/winarm64/vlc-{S.VERSION}-winarm64.exe'), ('Windows 32-bit', 'Older PCs', f'https://get.videolan.org/vlc/{S.VERSION}/win32/vlc-{S.VERSION}-win32.exe'), ('MSI, ZIP, 7z and more', 'All Windows packages', 'p/vlc--download-windows.html')]),
            ('mac', 'macOS', [('Universal', 'Apple Silicon & Intel', f'https://get.videolan.org/vlc/{S.VERSION}/macosx/vlc-{S.VERSION}-universal.dmg'), ('Apple Silicon', 'Smaller download', f'https://get.videolan.org/vlc/{S.VERSION}/macosx/vlc-{S.VERSION}-arm64.dmg'), ('Intel', '64-bit', f'https://get.videolan.org/vlc/{S.VERSION}/macosx/vlc-{S.VERSION}-intel64.dmg'), ('Older Macs', 'Back to PowerPC', 'p/vlc--download-macosx.html')]),
            ('linux', 'Linux', [('Ubuntu', 'sudo apt install vlc', 'p/vlc--download-ubuntu.html'), ('Debian', 'sudo apt install vlc', 'p/vlc--download-debian.html'), ('Fedora', 'RPM Fusion', 'p/vlc--download-fedora.html'), ('Arch Linux', 'sudo pacman -S vlc', 'p/vlc--download-archlinux.html'), ('openSUSE', 'zypper', 'p/vlc--download-suse.html'), ('All distributions', '', 'p/section--download.html')]),
            ('mobile', 'Mobile & TV', [('Android', 'Google Play · F-Droid · APK', 'p/vlc--download-android.html'), ('iPhone & iPad', 'App Store', 'p/vlc--download-ios.html'), ('Apple TV', 'App Store', 'p/vlc--download-appletv.html'), ('ChromeOS', 'Google Play', 'p/vlc--download-chromeos.html')]),
            ('src', 'Source', [(f'vlc-{S.VERSION}.tar.xz', 'Source tarball', f'https://get.videolan.org/vlc/{S.VERSION}/vlc-{S.VERSION}.tar.xz'), ('Build instructions', '', 'p/vlc--download-sources.html'), ('GitLab', 'code.videolan.org', 'https://code.videolan.org/videolan/vlc')])]
    tabbtn = ''.join(f'<button type="button" role="tab" id="bt-{k}" aria-controls="bp-{k}" aria-selected="{"true" if i == 0 else "false"}"{" tabindex=-1" if i else ""} data-os="{k}">{l}</button>' for i, (k, l, _) in enumerate(tabs))
    panels = ''
    for i, (k, l, rows_) in enumerate(tabs):
        items = ''.join(f'<a class="b-file" href="{e(u)}"{" data-dl" if "get.videolan.org" in u else ""}><span class="ic" aria-hidden="true">{bi("film")}</span><b>{e(a)}</b><small>{e(m)}</small></a>' for a, m, u in rows_)
        panels += f'<div role="tabpanel" id="bp-{k}" aria-labelledby="bt-{k}"{"" if i == 0 else " hidden"} class="b-files">{items}</div>'
    fmts = ' · '.join(FORMATS[:40])
    main = f'''<section class="b-stage" aria-label="VLC media player">
<canvas id="b-canvas" aria-hidden="true"></canvas>
<div class="b-stage-cone" aria-hidden="true">{CONE}</div>
<div class="b-osd-tl"><span class="rec"></span> Now playing</div>
<div class="b-osd-tr" aria-hidden="true">HEVC · AV1 · HDR10 · 8K · 7.1</div>
<div class="b-stage-copy">
<h1><span>VLC media player</span> Plays everything.</h1>
<p>Free and open source, made by volunteers since 1996. Files, discs, webcams, devices and streams, on every system. No spyware, no ads, no user tracking.</p>
<div class="b-cta"><a class="b-btn" id="b-dl" href="p/download.html">{bi("play")}<span><span id="b-dl-t">Download VLC</span><small id="b-dl-s">Version {S.VERSION} · all platforms</small></span></a><button type="button" class="b-btn ghost" data-donate>{bi("heart")}<span>Donate</span></button></div>
</div>
<p class="b-sub" id="b-sub" aria-live="off"><span>Plays files, discs, webcams, devices and streams.</span></p>
</section>

<section class="b-win" aria-labelledby="om-t"><header class="b-win-t"><span class="b-dots" aria-hidden="true"><i></i><i></i><i></i></span><h2 id="om-t">Open Media <small>— Download VLC {S.VERSION} “{S.CODENAME}”</small></h2></header>
<div class="b-tabs" role="tablist" aria-label="Platforms">{tabbtn}</div>{panels}
<p class="b-win-foot">Signed builds · SHA-256 checksums on <a href="https://download.videolan.org/pub/videolan/vlc/{S.VERSION}/" data-dl>our mirrors</a> · <a href="p/download.html">Every platform and version</a></p></section>

<div class="b-two">
<section class="b-win" aria-labelledby="mi-t"><header class="b-win-t"><span class="b-dots" aria-hidden="true"><i></i><i></i><i></i></span><h2 id="mi-t">Media Information <small>Ctrl+I</small></h2></header>
<div class="b-tabs" role="tablist" aria-label="Media information"><button type="button" role="tab" id="mt-g" aria-controls="mp-g" aria-selected="true">General</button><button type="button" role="tab" id="mt-c" aria-controls="mp-c" aria-selected="false" tabindex="-1">Codec</button><button type="button" role="tab" id="mt-s" aria-controls="mp-s" aria-selected="false" tabindex="-1">Statistics</button></div>
<dl class="b-meta" role="tabpanel" id="mp-g" aria-labelledby="mt-g"><dt>Title</dt><dd>VLC media player</dd><dt>Artist</dt><dd>VideoLAN and volunteers from 40+ countries</dd><dt>Genre</dt><dd>Free and open source software</dd><dt>Date</dt><dd>1996 · open source since 2001</dd><dt>Publisher</dt><dd>VideoLAN, non-profit (French law of 1901)</dd><dt>Copyright</dt><dd>GNU GPLv2 · LGPL for libVLC</dd><dt>Language</dt><dd>81 subtitle tracks ready · <button type="button" class="b-link" data-ui-open="lang">choose</button></dd><dt>Now playing</dt><dd>{S.VERSION} “{S.CODENAME}”</dd></dl>
<div class="b-meta-codec" role="tabpanel" id="mp-c" aria-labelledby="mt-c" hidden><p><b>Stream 0 · Video</b> H.264, HEVC, AV1, VP9, MPEG-2, VC-1, Theora, ProRes and more · up to 8K, 10-bit, HDR10</p><p><b>Stream 1 · Audio</b> AAC, MP3, Opus, FLAC, ALAC, AC-3, E-AC-3, DTS, TrueHD, ATRAC9 · passthrough to your receiver</p><p><b>Stream 2 · Subtitles</b> SRT, ASS, WebVTT, DVB, CEA-608/708, VobSub</p><p><b>Stream 3 · Network</b> HLS, DASH, RTSP, SRT, RIST, multicast, SMB, NFS, UPnP, Chromecast</p><p><a href="p/vlc--features.html">Full feature list →</a></p></div>
<dl class="b-meta" role="tabpanel" id="mp-s" aria-labelledby="mt-s" hidden><dt>Pages</dt><dd>{len(S.PAGES)} carried over from videolan.org</dd><dt>News</dt><dd>{len(S.NEWS)} items since 1999</dd><dt>Releases</dt><dd>{len(S.ordered("releases"))} release notes</dd><dt>Security</dt><dd>{len(S.ordered("security"))} advisories &amp; bulletins</dd><dt>Events</dt><dd>{len(S.ordered("events"))} event pages</dd><dt>Trackers</dt><dd>0</dd><dt>Cookies</dt><dd>0</dd></dl>
</section>
<section class="b-win" aria-labelledby="pl-t"><header class="b-win-t"><span class="b-dots" aria-hidden="true"><i></i><i></i><i></i></span><h2 id="pl-t">Playlist <small>— Latest news</small></h2></header>
<table class="b-table"><thead><tr><th scope="col" class="n">#</th><th scope="col">Title</th><th scope="col" class="d">Date</th></tr></thead><tbody>{rows}</tbody></table>
<p class="b-win-foot"><a href="p/news.html">All {len(S.NEWS)} news items →</a></p></section>
</div>

<section class="b-chapters" aria-labelledby="ch-t"><h2 id="ch-t" class="b-h2">Chapters</h2><div class="b-chgrid">{chap}</div></section>

<section class="b-win" aria-labelledby="fx-t"><header class="b-win-t"><span class="b-dots" aria-hidden="true"><i></i><i></i><i></i></span><h2 id="fx-t">Adjustments and Effects <small>— make this site yours</small></h2></header>
<div class="b-fx">
<div><p class="b-gh">Skin</p><div class="b-skins" role="group" aria-label="Skin"><button type="button" data-skin="dark"><i class="sw sw-dark"></i>Dark</button><button type="button" data-skin="light"><i class="sw sw-light"></i>Daylight</button><button type="button" data-skin="classic"><i class="sw sw-classic"></i>Classic 2006</button></div></div>
<div><p class="b-gh"><label for="fx-size">Text size</label></p><input type="range" id="fx-size" min="0" max="2" step="1" value="0"><p class="b-gh" style="margin-top:1rem">Contrast</p><div class="b-skins" role="group" aria-label="Contrast"><button type="button" data-fx="contrast" data-v="">Normal</button><button type="button" data-fx="contrast" data-v="high">High</button></div></div>
<div><p class="b-gh">Motion</p><div class="b-skins" role="group" aria-label="Motion"><button type="button" data-fx="motion" data-v="">On</button><button type="button" data-fx="motion" data-v="off">Off</button></div><p class="b-gh" style="margin-top:1rem">Hotkeys</p><p class="b-small"><kbd>Space</kbd> play · <kbd>N</kbd>/<kbd>P</kbd> next/previous · <kbd>F</kbd> focus · <kbd>Ctrl K</kbd> open media · <kbd>?</kbd> all</p></div>
</div></section>

<section class="b-support"><div>{CONE}</div><div><h2>Support the cone.</h2><p>VLC is free because volunteers build it and people like you fund the servers, hardware and meetings. Apple Pay, Google Pay, card, SEPA, PayPal, bank transfer or Bitcoin.</p></div><button type="button" class="b-btn" data-donate>{bi("heart")}<span>Donate</span></button></section>
<p class="b-foot">VLC, VideoLAN and x264 are trademarks of VideoLAN. Unofficial redesign concept by Paul Fleury · <a href="p/design-notes.html">Design notes</a> · <a href="p/sitemap.html">Site index</a> · <span class="b-small">Formats: {e(fmts)}…</span></p>'''
    return b_shell('home', 'VLC media player — VideoLAN', 'VLC is a free and open source cross-platform multimedia player.', True, main, [], 900, 'videolan.org/')

def build_b():
    out = DIST / 'b'
    shutil.copy(ROOT / 'b' / 'b.css', out.mkdir(parents=True, exist_ok=True) or out / 'b.css')
    shutil.copy(ROOT / 'b' / 'b.js', out / 'b.js')
    write(out / 'index.html', b_home())
    for slug, p in S.ALL.items(): write(out / 'p' / f'{slug}.html', b_page(p))

# ================================================================ OPTION C
C_NAV = [(k, s['label']) for k, s in S.SECTIONS.items()]
def c_num(k): return list(S.SECTIONS).index(k) + 1

def c_masthead(at_home, cur_sec, big=False):
    nav = ''.join(f'<a href="{page_href("section--" + k, at_home)}"' + (' aria-current="page"' if k == cur_sec else '') + f'><span>{c_num(k):02d}</span>{e(l)}</a>' for k, l in C_NAV)
    return f'''<header class="c-mast{' big' if big else ''}">
<div class="c-strip"><div class="c-wrap"><span>Vol. 30 · Est. 1996 · Free since 2001</span><span class="c-strip-r"><button type="button" data-ui-open="lang" class="c-tl"><span data-ui-langlabel="name">English</span> edition</button><button type="button" class="c-tl" data-c-act="night" aria-label="Switch between day and night edition"><span class="c-ed">Night edition</span></button><button type="button" class="c-tl" data-ui-open="search" aria-label="Search">Search</button><button type="button" class="c-tl" data-ui-open="a11y">Display</button><button type="button" class="c-donate" data-donate>Donate</button></span></div></div>
<div class="c-wrap c-name"><a href="{page_href("home", at_home)}" aria-label="VideoLAN — home">{CONE}<span class="c-word">VideoLAN</span></a>{'<p class="c-motto">The free multimedia almanac — home of VLC media player</p>' if big else ''}</div>
<nav class="c-nav" aria-label="Chapters"><div class="c-wrap"><button type="button" class="c-navtoggle" data-c-act="nav" aria-expanded="false">Chapters</button><div class="c-navlinks">{nav}</div></div></nav>
</header>'''

def c_footer(at_home):
    cols = ''
    for k, s in list(S.SECTIONS.items()):
        cols += f'<div><h3><span>{c_num(k):02d}</span> <a href="{page_href("section--" + k, at_home)}">{e(s["label"])}</a></h3><p>{e(s["blurb"])}</p></div>'
    return f'''<footer class="c-foot"><div class="c-wrap"><div class="c-foot-grid">{cols}</div>
<div class="c-colophon"><p><b>Colophon.</b> Set in your system’s own serif and sans faces, so nothing is downloaded but words. No cookies, no trackers. VLC, VideoLAN and x264 are registered trademarks of VideoLAN. Unofficial redesign concept by Paul Fleury. <a href="{page_href("design-notes", at_home)}">Design notes</a> · <a href="{page_href("sitemap", at_home)}">Index of every page</a></p></div></div></footer>'''

def c_shell(slug, title, desc, at_home, main_html, cur_sec, big=False):
    root = '../' if at_home else '../../'
    prefix = '' if at_home else '../'
    head = shell_head('c', title, desc, root, slug, f'<link rel="stylesheet" href="{prefix}c.css">', 'light')
    return head + f'''<a class="skip" href="#main">Skip to content</a>
{c_masthead(at_home, cur_sec, big)}
<main id="main" tabindex="-1">{main_html}</main>
{c_footer(at_home)}''' + shell_foot(root, f'<script src="{prefix}c.js" defer></script>')

def c_page(p):
    slug = p['slug']
    body, t = prose(p)
    sk = p.get('hub') or S.sec_key(p)
    prev, nxt = S.seq(slug)
    tocl = ''.join(f'<li><a href="#{i}">{e(x)}</a></li>' for i, x in t[:24])
    pn = ''
    if prev or nxt:
        pn = '<nav class="c-pn" aria-label="Continue reading">' + (f'<a href="{prev}.html"><small>← Previous</small><b>{e(S.ALL[prev]["display"])}</b></a>' if prev else '<span></span>') + (f'<a href="{nxt}.html" class="r"><small>Next →</small><b>{e(S.ALL[nxt]["display"])}</b></a>' if nxt else '<span></span>') + '</nav>'
    main = f'''<article class="c-article">
<header class="c-ahead c-wrap"><p class="c-kick"><a href="section--{sk}.html">§ {c_num(sk):02d} · {e(section_label(p))}</a></p>
<h1>{e(p["display"])}</h1>
{f'<p class="c-stand">{e(p["desc"])}</p>' if p.get('desc') and len(p['desc']) < 260 else ''}
<p class="c-by">{' <span aria-hidden="true">·</span> '.join(e(b) for b in meta_bits(p)[1:])}</p></header>
<div class="c-wrap c-agrid{' has-toc' if len(t) >= 2 else ''}">
{f'<aside class="c-toc" aria-label="In this article"><p>In this article</p><ol>{tocl}</ol></aside>' if len(t) >= 2 else ''}
<div class="c-prose x-prose">{body}</div>
</div>
<div class="c-wrap">{pn}</div>
</article>'''
    return c_shell(slug, p['display'] + ' — VideoLAN', p.get('desc'), False, main, sk)

def c_home():
    lead = S.NEWS[0]
    brief = S.NEWS[1:7]
    def nhref(n):
        r = S.resolve('https://www.videolan.org/news.html#' + n['id'])
        return S.href_for(r[0], r[1], True) if r else 'p/news.html'
    briefs = ''.join(f'<li><time>{S.nice_date(n["date"])}</time><a href="{nhref(n)}">{e(n["title"])}</a></li>' for n in brief)
    lead_body = S.rewrite(lead['html'], True)
    # yearly news counts for the timeline chart
    counts = [(y, len(S.NEWS_BY_YEAR.get(str(y), []))) for y in range(1999, 2027)]
    mx = max(c for _, c in counts) or 1
    marks = {1999: 'First news', 2001: 'Open source, GPL', 2005: 'VLC 0.8', 2009: 'Non-profit; VLC 1.0', 2012: 'VLC 2.0', 2018: 'VLC 3.0 “Vetinari”', 2026: f'VLC {S.VERSION}'}
    bars = ''
    for i, (y, c) in enumerate(counts):
        h = round(c / mx * 100)
        bars += f'<a class="c-bar{" m" if y in marks else ""}" href="p/news--{y}.html" style="--h:{h}%" aria-label="{y}: {c} news items"><span class="v">{c}</span><span class="y">{str(y)[2:] if y not in (1999, 2026) else y}</span>{f"<em>{e(marks[y])}</em>" if y in marks else ""}</a>'
    wall = ''.join(f'<span>{e(f)}</span> ' for f in FORMATS)
    desk = ''
    for key, name, rows in S.DL:
        items = ''.join(f'<li><a href="{e(u)}">{e(t)}</a><span>{e(m)}</span></li>' for t, m, u in rows[:6])
        desk += f'<section><h3>{e(name)}</h3><ul>{items}</ul></section>'
    desk = S.rewrite(desk, True)
    chapters = ''.join(f'<a class="c-ch" href="p/section--{k}.html"><span class="n">{c_num(k):02d}</span><b>{e(s["label"])}</b><p>{e(s["blurb"])}</p><small>{len(S.ordered(k)) + (len(S.YEARS) if k == "news" else 0)} pages</small></a>' for k, s in S.SECTIONS.items())
    main = f'''<section class="c-front c-wrap" aria-label="Front page">
<article class="c-lead">
<p class="c-kick">Release · {S.nice_date(lead["date"])}</p>
<h1 class="c-headline">VLC {S.VERSION} closes more than 130 security holes and moves to FFmpeg 8.1.</h1>
<p class="c-stand">The twenty-fifth update of the “{S.CODENAME}” branch refreshes 49 libraries, adds ATRAC3, ATRAC9 and CEA-708 captions in MP4, and makes Windows start faster when the clocks change.</p>
<div class="c-cols"><p class="c-drop">{lead_body}</p></div>
<div class="c-get" id="c-get"><a class="c-getbtn" id="c-dl" href="p/download.html"><span class="k">Get it now</span><b id="c-dl-t">Download VLC {S.VERSION}</b><span id="c-dl-s">Free · every platform · no ads, no tracking</span></a>
<ul class="c-getlist"><li><a href="https://get.videolan.org/vlc/{S.VERSION}/win64/vlc-{S.VERSION}-win64.exe" data-dl>Windows</a></li><li><a href="https://get.videolan.org/vlc/{S.VERSION}/macosx/vlc-{S.VERSION}-universal.dmg" data-dl>macOS</a></li><li><a href="p/section--download.html">Linux</a></li><li><a href="p/vlc--download-android.html">Android</a></li><li><a href="p/vlc--download-ios.html">iOS</a></li><li><a href="p/download.html">All</a></li></ul></div>
</article>
<aside class="c-side">
<section class="c-box"><h2>In brief</h2><ol class="c-brief">{briefs}</ol><a class="c-more" href="p/news.html">All {len(S.NEWS)} stories since 1999 →</a></section>
<section class="c-box c-facts"><h2>By the numbers</h2><dl><div><dt>1996</dt><dd>Born as a student project at École Centrale Paris</dd></div><div><dt>40+</dt><dd>Countries our developers come from</dd></div><div><dt>{len(FORMATS)}</dt><dd>Formats, codecs and protocols on the wall below</dd></div><div><dt>0</dt><dd>Ads, trackers and cookies</dd></div></dl></section>
</aside>
</section>

<section class="c-banner" aria-label="Motto"><div class="c-stripes" aria-hidden="true"></div><p class="c-wrap"><span>Plays</span> <span>everything.</span></p><div class="c-stripes" aria-hidden="true"></div></section>

<section class="c-wrap c-sec" aria-labelledby="wall-t"><header class="c-sechead"><p class="c-kick">§ 02 · VLC media player</p><h2 id="wall-t">The wall of everything it plays</h2><p>No codec packs. No plug-ins. Just these, built in. <a href="p/vlc--features.html">Read the full feature list</a>.</p></header>
<p class="c-wall" id="c-wall">{wall}</p></section>

<section class="c-wrap c-sec" aria-labelledby="tl-t"><header class="c-sechead"><p class="c-kick">§ 04 · News</p><h2 id="tl-t">Twenty-seven years of news</h2><p>Every bar is a year of announcements from videolan.org. Select a year to read it.</p></header>
<div class="c-chart" role="list">{bars}</div></section>

<section class="c-wrap c-sec" aria-labelledby="desk-t"><header class="c-sechead"><p class="c-kick">§ 01 · Download</p><h2 id="desk-t">The download desk</h2><p>Official builds only. Signed, checksummed and never bundled with anything else.</p></header>
<div class="c-desk">{desk}</div></section>

<section class="c-letter c-wrap" aria-labelledby="let-t"><div class="c-letter-in"><p class="c-kick">A letter to our readers</p><h2 id="let-t">VLC has never shown you an ad. It never will.</h2>
<p class="c-drop2">VLC is made by volunteers and run by VideoLAN, a small non-profit under French law. There are no investors to please and no data to sell. What keeps the cone turning is people: developers who give their evenings, translators, testers, and readers who chip in for servers, test hardware and meetings like VideoLAN Dev Days.</p>
<p>If VLC has played something for you that nothing else would, consider returning the favour. It takes a moment: Apple Pay, Google Pay, card, SEPA, PayPal, bank transfer or Bitcoin.</p>
<p class="c-sign">— The VideoLAN volunteers</p>
<div class="c-letter-btns"><button type="button" class="c-big" data-donate="10">Give €10</button><button type="button" class="c-big alt" data-donate="25">Give €25</button><button type="button" class="c-big alt" data-donate>Choose an amount</button><a class="c-textlink" href="p/contribute.html">Or give your time →</a></div></div></section>

<section class="c-wrap c-sec" aria-labelledby="ix-t"><header class="c-sechead"><p class="c-kick">Index</p><h2 id="ix-t">Twelve chapters, the whole of videolan.org</h2><p>{len(S.PAGES)} pages carried over, plus {len(S.NEWS)} news items. <a href="p/sitemap.html">Open the full index</a>.</p></header>
<div class="c-chapters">{chapters}</div></section>'''
    return c_shell('home', 'VideoLAN — the home of VLC media player', 'VLC is a free and open source cross-platform multimedia player.', True, main, None, True)

def build_c():
    out = DIST / 'c'; out.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / 'c' / 'c.css', out / 'c.css'); shutil.copy(ROOT / 'c' / 'c.js', out / 'c.js')
    write(out / 'index.html', c_home())
    for slug, p in S.ALL.items(): write(out / 'p' / f'{slug}.html', c_page(p))

# ================================================================ chooser
def build_chooser():
    src = (ROOT / 'chooser' / 'index.html').read_text()
    src = src.replace('{{PAGES}}', str(len(S.PAGES))).replace('{{NEWS}}', str(len(S.NEWS))).replace('{{TOTAL}}', str(len(S.ALL)))
    write(DIST / 'index.html', src)

if __name__ == '__main__':
    which = sys.argv[1:] or ['a', 'b', 'c', 'chooser']
    if 'a' in which: build_a()
    if 'b' in which: build_b()
    if 'c' in which: build_c()
    if 'chooser' in which: build_chooser()
    tot = sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file())
    print('files', sum(1 for f in DIST.rglob('*') if f.is_file()), 'size MB', round(tot / 1e6, 1))
