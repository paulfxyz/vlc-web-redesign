#!/usr/bin/env python3
"""Extract every crawled videolan.org page into normalized content JSON."""
import json, re, hashlib, pathlib
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import urljoin, urlparse

CRAWL = pathlib.Path('/tmp/crawl')
OUT = pathlib.Path('/home/user/workspace/vlc-web-redesign/content/pages.json')
OUT.parent.mkdir(exist_ok=True)
paths = [l.strip() for l in open('/tmp/paths_all.txt') if l.strip()]

SKIP = {'/vlc/skins.html"', '/vlc/skins2-create.html"', '/403.html', '/404.html', '/apc.html', '/googleb9159c603101d049.html', '/test.html', '/js/index.html',
        '/include/index.html', '/news-rss.html', '/', '/index.html', '/webirc/'}
ALLOWED = {'h1','h2','h3','h4','h5','p','ul','ol','li','a','b','strong','em','i','code','pre','img','table','thead','tbody',
           'tr','td','th','blockquote','br','dl','dt','dd','hr','figure','figcaption','small','sup','sub','kbd','abbr'}

def fname(p):
    return CRAWL / (re.sub(r'[^A-Za-z0-9._-]', '_', p.strip('/')) or 'index')

def canon(p):
    p = re.sub(r'/index\.html$', '/', p)
    return p

def slug_of(p):
    p = canon(p)
    s = p.strip('/')
    s = re.sub(r'\.html$', '', s)
    s = s.replace('/', '--')
    return s or 'home'

def section_of(p):
    rules = [('/vlc/download-', 'Download'), ('/vlc/releases', 'Releases'), ('/vlc/skinedhlp', 'Skin Editor'),
             ('/vlc/skin', 'Customise'), ('/vlc/stats', 'Statistics'), ('/vlc/contest', 'Customise'), ('/vlc/', 'VLC'),
             ('/security', 'Security'), ('/press', 'Press'), ('/videolan/events', 'Events'), ('/videolan', 'VideoLAN'),
             ('/developers/i18n', 'Translation'), ('/developers', 'Developers'), ('/projects/vlma', 'VLMa'),
             ('/projects', 'Projects'), ('/vlmc', 'Projects'), ('/support', 'Support'), ('/doc', 'Support'),
             ('/contribute', 'Contribute'), ('/goodies', 'VLC'), ('/legal', 'VideoLAN'), ('/privacy', 'VideoLAN'),
             ('/contact', 'VideoLAN'), ('/news', 'News'), ('/streaming', 'VLC'), ('/thank_you', 'Contribute')]
    for pre, sec in rules:
        if p.startswith(pre): return sec
    return 'VideoLAN'

def abs_url(u, base):
    if not u: return ''
    u = u.strip()
    if u.startswith('//'): u = 'https:' + u
    return urljoin(base, u)

def clean(node, base):
    """Return sanitized HTML string of children."""
    out = []
    for c in node.children:
        if isinstance(c, Comment): continue
        if isinstance(c, NavigableString):
            t = str(c)
            out.append(t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
            continue
        name = c.name
        st = (c.get('style') or '').replace(' ', '').lower()
        if 'display:none' in st and name not in ('div',): continue
        if name in ('script', 'style', 'form', 'input', 'button', 'select', 'iframe', 'noscript', 'svg', 'object', 'embed', 'video', 'audio', 'source'):
            continue
        if name == 'img':
            src = c.get('data-lazy') or c.get('data-src') or c.get('src') or ''
            if not src: continue
            src = abs_url(src, base)
            alt = (c.get('alt') or '').replace('"', '&quot;')
            out.append(f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async">')
            continue
        inner = clean(c, base)
        if name == 'a':
            href = c.get('href') or ''
            if not href or href.startswith('javascript'):
                out.append(inner); continue
            if href.startswith('#'):
                out.append(inner); continue
            href = abs_url(href, base)
            out.append(f'<a href="{href.replace(chr(34), "%22")}">{inner}</a>')
            continue
        if name in ALLOWED:
            if name == 'center': name = 'div'
            attrs = ''
            if name in ('td', 'th'):
                for k in ('colspan', 'rowspan'):
                    if c.get(k): attrs += f' {k}="{c.get(k)}"'
            if name in ('i',): name = 'em'
            if name == 'b': name = 'strong'
            out.append(f'<{name}{attrs}>{inner}</{name}>' if name not in ('br', 'hr') else f'<{name}>')
        else:
            # flatten divs/sections/spans; keep block separation
            if name in ('div', 'section', 'article', 'header', 'center', 'main', 'aside', 'footer'):
                out.append(' \u2042 ' + inner + ' \u2042 ')
            else:
                out.append(inner)
    return ''.join(out)

MARK = '\u2042'
BLOCKS = {'h1','h2','h3','h4','h5','p','ul','ol','pre','table','blockquote','dl','hr','figure'}
INLINE_OK_PARENT = {'li','td','th','dd','dt','p','h1','h2','h3','h4','h5','blockquote','figcaption','a','strong','em','code','small'}
def tidy(h):
    pres = []
    def keep(m):
        pres.append(m.group(1).replace(MARK, '\n').strip('\n'))
        return '<pre>\u27e6PRE%d\u27e7</pre>' % (len(pres) - 1)
    h = re.sub(r'<pre>(.*?)</pre>', keep, h, flags=re.S)
    h = re.sub(r'[ \t\r\n\f\v]+', ' ', h)
    frag = BeautifulSoup('<div id="r">' + h + '</div>', 'html.parser').find(id='r')
    # inside nested elements, markers become spaces (or <br> in cells)
    for t in list(frag.find_all(string=True)):
        if MARK in t and t.parent is not frag:
            t.replace_with(t.replace(MARK, ' '))
    # unwrap paragraphs nested in p
    for p_ in frag.find_all('p'):
        if p_.find_parent('p'): p_.unwrap()
    out, buf = [], []
    def flush():
        s_ = ''.join(buf).strip()
        buf.clear()
        if s_ and re.sub(r'<[^>]+>', '', s_).strip() or '<img' in s_:
            out.append('<p>' + s_ + '</p>')
    for c in list(frag.children):
        if isinstance(c, NavigableString):
            parts = str(c).split(MARK)
            for i, part in enumerate(parts):
                if i: flush()
                buf.append(part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        elif c.name in BLOCKS or c.name == 'li':
            flush(); out.append(str(c))
        else:
            buf.append(str(c))
    flush()
    h = '\n'.join(out)
    # unwrap layout tables (tables that contain headings, lists or images)
    fr2 = BeautifulSoup('<div id="r">' + h + '</div>', 'html.parser')
    for tb in fr2.find_all('table'):
        if tb.find(['h1','h2','h3','ul','img']):
            for x in tb.find_all(['tr','td','th','tbody','thead']): x.name = 'div'
            tb.name = 'div'
    for im in fr2.find_all('img'):
        if 'downloadVLC.png' in (im.get('src') or ''): im.decompose()
    h = ''.join(str(x) for x in fr2.find(id='r').children)
    h = re.sub(r'<p>\s*(<br/?>\s*)*</p>', '', h)
    h = re.sub(r'<(strong|em|p|li|h\d)>\s*</\1>', '', h)
    h = re.sub(r'<br/>', '<br>', h)
    # drop near-duplicate consecutive paragraphs (desktop/mobile variants on the old site)
    paras = re.findall(r'<p>(.*?)</p>', h, flags=re.S)
    seenp = set()
    def dedupe(m):
        key = re.sub(r'<[^>]+>|\W', '', m.group(1)).lower()[:70]
        if len(key) > 40 and key in seenp: return ''
        seenp.add(key); return m.group(0)
    h = re.sub(r'<p>(.*?)</p>', dedupe, h, flags=re.S)
    # group image-only paragraphs into galleries
    h = re.sub(r'(?:<p>\s*(?:<img [^>]+>\s*)+</p>\s*){1,}', lambda m: '<div class="gallery">' + ''.join(re.findall(r'<img [^>]+>', m.group(0))) + '</div>\n', h)
    # junk from download CTAs
    h = re.sub(r'<p>\s*(Get VLC now!|Version [0-9.]+)\s*</p>', '', h)
    h = h.replace('<img src="https://www.videolan.org/images/downloadVLC.png" alt="Download VLC icon" loading="lazy" decoding="async">', '')
    h = re.sub('\u27e6PRE(\\d+)\u27e7', lambda m: pres[int(m.group(1))], h)
    return h

pages, seen = {}, {}
ALIAS = {}
for p in paths:
    if p in SKIP: continue
    f = fname(p)
    if not f.exists(): continue
    raw = f.read_bytes()
    try:
        soup = BeautifulSoup(raw, 'html.parser')
    except Exception:
        continue
    body = soup.find(id='bodyInner')
    if not body: continue
    for x in body.select('nav, #footer, script, style, #nonprofitOrganizationDiv2, #nonprofitOrganizationDiv, #translation, .navbar, .header.container, #wscounter, .donate, #donate, .sidebar-donate'):
        x.decompose()
    cp = canon(p)
    title = (soup.title.string or '').strip() if soup.title else cp
    title = re.sub(r'\s*-\s*VideoLAN\s*$', '', title)
    desc = ''
    m = soup.find('meta', attrs={'name': 'description'})
    if m: desc = (m.get('content') or '').strip()
    base = 'https://www.videolan.org' + p
    html = tidy(clean(body, base))
    text = ' '.join(BeautifulSoup(html, 'html.parser').get_text(' ').split())
    h = hashlib.md5((text + ''.join(re.findall(r'src="([^"]+)"', html))).encode()).hexdigest()
    if h in seen:
        ALIAS[cp] = seen[h]; continue
    seen[h] = cp
    slug = slug_of(cp)
    if slug in pages: continue
    m1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    display = ''
    if m1:
        display = ' '.join(re.sub(r'<[^>]+>', ' ', m1.group(1)).split())
        html = html[:m1.start()] + html[m1.end():]
    html = re.sub(r'<(/?)h1>', r'<\1h2>', html)
    html = re.sub(r'<p>\s*Get VLC now!\s*Version [0-9.]+\s*</p>', '', html)
    imgs = len(re.findall(r'<img ', html))
    pages[slug] = dict(slug=slug, path=cp, title=title or cp, display=display or title or cp, desc=desc, section=section_of(cp), html=html,
                       words=len(text.split()), images=imgs)

# Path -> slug index (including aliases)
index = {}
for s, pg in pages.items():
    index[pg['path']] = s
    if pg['path'].endswith('/'):
        index[pg['path'] + 'index.html'] = s; index[pg['path'].rstrip('/')] = s
for a, target in ALIAS.items():
    if target in index and a not in index: index[a] = index[target]
for a, t in {'/vlc/download.html': '/vlc/', '/streaming/': '/vlc/streaming.html', '/streaming': '/vlc/streaming.html', '/support/lists.php': '/support/lists.html', '/vlc/changelog.html': None}.items():
    if t and t in index: index[a] = index[t]
json.dump(dict(pages=pages, index=index), open(OUT, 'w'), ensure_ascii=False)
from collections import Counter
print(len(pages), 'pages'); print(Counter(p['section'] for p in pages.values()))
print('total words', sum(p['words'] for p in pages.values()), 'size', OUT.stat().st_size // 1024, 'KB')

# ---------------- News items ----------------
raw = (CRAWL / 'news.html').read_bytes()
soup = BeautifulSoup(raw, 'html.parser')
items = []
for it in soup.select('div[class^=item]'):
    a = it.find('a', id=True)
    t = it.select_one('.title'); dt = it.select_one('.date'); ds = it.select_one('.news-descr')
    if not (t and dt): continue
    body = tidy(clean(ds, 'https://www.videolan.org/news.html')) if ds else ''
    body = re.sub(r'^<p>(.*)</p>$', r'\1', body.strip(), flags=re.S) if body.count('<p>') == 1 else body
    items.append(dict(id=a.get('id') if a else '', title=' '.join(t.get_text(' ').split()), date=dt.get_text(strip=True), html=body))
json.dump(items, open(OUT.parent / 'news.json', 'w'), ensure_ascii=False)
print('news items', len(items), items[0]['date'], items[-1]['date'])
