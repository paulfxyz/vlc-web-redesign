"""Common content model, link rewriting and curated hub pages shared by options A, B and C."""
import json, re, html as H, pathlib
from collections import OrderedDict, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / 'content/pages.json'))
NEWS = json.load(open(ROOT / 'content/news.json'))
PAGES = DATA['pages']
INDEX = DATA['index']
e = H.escape
VERSION = '3.0.24'
CODENAME = 'Vetinari'

# ------------------------------------------------------------------ sections
SECTIONS = OrderedDict([
    ('download',   dict(label='Download', blurb='Official builds of VLC for every platform, past and present.', match=['Download'])),
    ('vlc',        dict(label='VLC media player', blurb='Features, screenshots, skins, goodies and the libVLC framework.', match=['VLC', 'Customise', 'Skin Editor', 'Statistics'])),
    ('releases',   dict(label='Release notes', blurb='Every VLC release since 1.1, with highlights and changelogs.', match=['Releases'])),
    ('news',       dict(label='News', blurb='Announcements from VideoLAN since 1999.', match=['News'])),
    ('security',   dict(label='Security', blurb='Advisories and bulletins, and how to report a vulnerability.', match=['Security'])),
    ('projects',   dict(label='Projects', blurb='DVBlast, x264, dav1d, multicat, VLMC, VLMa and the libraries behind VLC.', match=['Projects', 'VLMa'])),
    ('developers', dict(label='Developers', blurb='Developer documentation, libraries, mailing lists and translation.', match=['Developers', 'Translation'])),
    ('support',    dict(label='Support', blurb='FAQ, documentation, forums, IRC and mailing lists.', match=['Support'])),
    ('contribute', dict(label='Contribute', blurb='Give time, hardware or money. VLC is made by people like you.', match=['Contribute'])),
    ('events',     dict(label='Events', blurb='VideoLAN Dev Days, FOSDEM and 25 years of photos and stories.', match=['Events'])),
    ('press',      dict(label='Press', blurb='Press releases and official statements.', match=['Press'])),
    ('videolan',   dict(label='VideoLAN', blurb='The organisation, team, partners, legal and privacy.', match=['VideoLAN'])),
])
SEC_OF = {}
for k, v in SECTIONS.items():
    for m in v['match']: SEC_OF[m] = k

def sec_key(p): return SEC_OF.get(p['section'], 'videolan')

def vkey(slug):
    m = re.search(r'releases--(\d+)\.(\d+)\.(\d+)(.*)$', slug)
    if not m: return (0, 0, 0, slug)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4))

def ordered(sec):
    items = [p for p in PAGES.values() if sec_key(p) == sec]
    if sec == 'releases': items.sort(key=lambda p: vkey(p['slug']), reverse=True)
    elif sec == 'security': items.sort(key=lambda p: (p['slug'] != 'security', p['slug']), reverse=False); items = [x for x in items if x['slug'] == 'security'] + sorted([x for x in items if x['slug'] != 'security'], key=lambda p: p['slug'], reverse=True)
    elif sec == 'events': items = [x for x in items if x['slug'] == 'videolan--events'] + sorted([x for x in items if x['slug'] != 'videolan--events'], key=lambda p: p['slug'], reverse=True)
    else:
        hub = {'download': 'vlc', 'vlc': 'vlc--features', 'projects': 'projects', 'developers': 'developers', 'support': 'support', 'contribute': 'contribute', 'press': 'press', 'videolan': 'videolan'}.get(sec)
        items.sort(key=lambda p: (p['slug'] != hub, p['slug']))
    return items

# ------------------------------------------------------------------ news years
def year_of(n): y = n['date'][:4]; return y if y and y != '1970' and y.isdigit() else 'undated'
NEWS_BY_YEAR = OrderedDict()
for n in NEWS: NEWS_BY_YEAR.setdefault(year_of(n), []).append(n)
YEARS = [y for y in NEWS_BY_YEAR if y != 'undated']
NEWS_ANCHOR = {n['id']: 'news--' + year_of(n) for n in NEWS if n['id']}

def nice_date(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    if not m or m.group(1) == '1970': return 'Undated'
    mon = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()[int(m.group(2)) - 1]
    return f'{int(m.group(3))} {mon} {m.group(1)}'

# ------------------------------------------------------------------ links
OWNED_DIRECT = re.compile(r'^https?://(get|download|downloads|images|artifacts|nightlies|mirror)\.videolan\.org', re.I)

def resolve(url):
    """Return (slug, anchor) for a videolan.org URL that we host, else None."""
    m = re.match(r'^https?://(?:www\.)?videolan\.org(/[^#?]*)?(?:\?[^#]*)?(#.*)?$', url)
    if not m: return None
    path = m.group(1) or '/'
    anchor = m.group(2) or ''
    if path in ('/', '/index.html'): return ('home', anchor)
    if path == '/news.html':
        if anchor[1:] in NEWS_ANCHOR: return (NEWS_ANCHOR[anchor[1:]], anchor)
        return ('news', '')
    cands = [path, path + '/', path.rstrip('/'), path.rstrip('/') + '/', re.sub(r'\.php$', '.html', path), path + 'index.html']
    if path in ('/vlc/', '/vlc', '/vlc/index.html') and anchor in ('#download', '#d'): return ('download', '')
    for c in cands:
        if c in INDEX: return (INDEX[c], anchor)
    return None

def href_for(slug, anchor, at_home):
    if slug == 'home': return ('index.html' if at_home else '../index.html') + anchor
    return ('p/' if at_home else '') + slug + '.html' + anchor

HREF_RE = re.compile(r'href="([^"]*)"')
def rewrite(htm, at_home=False):
    def rep(m):
        u = H.unescape(m.group(1))
        if u.startswith('//'): u = 'https:' + u
        if u.startswith('/') and not u.startswith('//'): u = 'https://www.videolan.org' + u
        r = resolve(u)
        if r:
            return 'href="%s"' % e(href_for(r[0], r[1], at_home))
        if OWNED_DIRECT.match(u) or re.match(r'^https?://(www\.)?videolan\.org/.*\.(pdf|png|jpe?g|gif|zip|vlt|lua|patch|asc|sha\d*|md5|txt|tar\.\w+|exe|dmg|sxi|asf|odp|ppt|ogg|avi|mp4|mkv)([?#].*)?$', u, re.I) or 'download-skins2-go.php' in u:
            return 'href="%s" data-dl' % e(u)
        return 'href="%s"' % e(u)
    return HREF_RE.sub(rep, htm)

def toc(htm):
    """Add ids to h2/h3 and return (html, [(id, text)])."""
    out, seen = [], set()
    def rep(m):
        tag, inner = m.group(1), m.group(2)
        txt = ' '.join(re.sub(r'<[^>]+>', ' ', inner).split())
        if not txt: return m.group(0)
        sid = re.sub(r'[^a-z0-9]+', '-', txt.lower()).strip('-')[:48] or 'section'
        base, i = sid, 2
        while sid in seen: sid = f'{base}-{i}'; i += 1
        seen.add(sid)
        if tag == 'h2': out.append((sid, txt))
        return f'<{tag} id="{sid}">{inner}</{tag}>'
    htm = re.sub(r'<(h2|h3)>(.*?)</\1>', rep, htm, flags=re.S)
    return htm, out

def read_min(words): return max(1, round(words / 220))

# ------------------------------------------------------------------ curated hubs (shared markup, styled per option)
DL = [
  ('windows', 'Windows', [
     ('Windows 64-bit installer', f'.exe · {VERSION} · recommended', f'https://get.videolan.org/vlc/{VERSION}/win64/vlc-{VERSION}-win64.exe'),
     ('Windows 64-bit MSI package', '.msi · for deployment', f'https://get.videolan.org/vlc/{VERSION}/win64/vlc-{VERSION}-win64.msi'),
     ('Windows 64-bit portable', '.zip · no installation', f'https://get.videolan.org/vlc/{VERSION}/win64/vlc-{VERSION}-win64.zip'),
     ('Windows ARM64', '.exe · Snapdragon and other ARM PCs', f'https://get.videolan.org/vlc/{VERSION}/winarm64/vlc-{VERSION}-winarm64.exe'),
     ('Windows 32-bit', '.exe · older PCs', f'https://get.videolan.org/vlc/{VERSION}/win32/vlc-{VERSION}-win32.exe'),
     ('All Windows options', 'Store, 7z archives, checksums', 'https://www.videolan.org/vlc/download-windows.html'),
  ]),
  ('apple', 'macOS', [
     ('macOS Universal', f'.dmg · Apple Silicon and Intel · {VERSION}', f'https://get.videolan.org/vlc/{VERSION}/macosx/vlc-{VERSION}-universal.dmg'),
     ('macOS Apple Silicon', '.dmg · smaller download', f'https://get.videolan.org/vlc/{VERSION}/macosx/vlc-{VERSION}-arm64.dmg'),
     ('macOS Intel 64-bit', '.dmg', f'https://get.videolan.org/vlc/{VERSION}/macosx/vlc-{VERSION}-intel64.dmg'),
     ('Older Macs and all options', 'Legacy builds back to PowerPC', 'https://www.videolan.org/vlc/download-macosx.html'),
  ]),
  ('mobile', 'Phones, tablets & TV', [
     ('Android', 'Google Play · F-Droid · APK', 'https://www.videolan.org/vlc/download-android.html'),
     ('iPhone & iPad', 'App Store', 'https://www.videolan.org/vlc/download-ios.html'),
     ('Apple TV', 'App Store', 'https://www.videolan.org/vlc/download-appletv.html'),
     ('ChromeOS', 'Google Play', 'https://www.videolan.org/vlc/download-chromeos.html'),
     ('Windows Phone', 'Legacy', 'https://www.videolan.org/vlc/download-windowsphone.html'),
     ('Windows RT / UWP', 'Microsoft Store', 'https://www.videolan.org/vlc/download-winrt.html'),
  ]),
  ('linux', 'GNU/Linux', [
     ('Ubuntu', 'apt · Snap', 'https://www.videolan.org/vlc/download-ubuntu.html'),
     ('Debian', 'apt', 'https://www.videolan.org/vlc/download-debian.html'),
     ('Fedora', 'dnf · RPM Fusion', 'https://www.videolan.org/vlc/download-fedora.html'),
     ('Arch Linux', 'pacman', 'https://www.videolan.org/vlc/download-archlinux.html'),
     ('openSUSE', 'zypper', 'https://www.videolan.org/vlc/download-suse.html'),
     ('Gentoo', 'emerge', 'https://www.videolan.org/vlc/download-gentoo.html'),
     ('Red Hat', 'RHEL · CentOS', 'https://www.videolan.org/vlc/download-redhat.html'),
     ('Slackware', '', 'https://www.videolan.org/vlc/download-slackware.html'),
     ('ALT Linux', '', 'https://www.videolan.org/vlc/download-altlinux.html'),
     ('Mandriva', 'Legacy', 'https://www.videolan.org/vlc/download-mandriva.html'),
     ('CRUX', '', 'https://www.videolan.org/vlc/download-crux.html'),
     ('Flatpak', 'Flathub', 'https://flathub.org/apps/org.videolan.VLC'),
  ]),
  ('other', 'Other systems', [
     ('FreeBSD', 'ports · pkg', 'https://www.videolan.org/vlc/download-freebsd.html'),
     ('OS/2', '', 'https://www.videolan.org/vlc/download-os2.html'),
     ('BeOS / Haiku', 'Legacy', 'https://www.videolan.org/vlc/download-beos.html'),
     ('Syllable', 'Legacy', 'https://www.videolan.org/vlc/download-syllable.html'),
     ('Maemo', 'Legacy', 'https://www.videolan.org/vlc/download-maemo.html'),
     ('Familiar Linux', 'Legacy', 'https://www.videolan.org/vlc/download-familiar.html'),
     ('Windows CE', 'Legacy', 'https://www.videolan.org/vlc/download-wince.html'),
     ('EyeTV plugin', 'Legacy', 'https://www.videolan.org/vlc/download-eyetv.html'),
     ('Skins', 'For the desktop player', 'https://www.videolan.org/vlc/download-skins.html'),
  ]),
  ('source', 'Source code', [
     (f'VLC {VERSION} source', '.tar.xz', f'https://get.videolan.org/vlc/{VERSION}/vlc-{VERSION}.tar.xz'),
     ('Building from source', 'Instructions and contribs', 'https://www.videolan.org/vlc/download-sources.html'),
     ('Git repository', 'code.videolan.org', 'https://code.videolan.org/videolan/vlc'),
     ('All releases on our mirrors', 'download.videolan.org', 'https://download.videolan.org/pub/videolan/vlc/'),
  ]),
]

def dl_hub_html():
    h = [f'<p class="x-lede">VLC {VERSION} “{CODENAME}” is the current release. Always download VLC from videolan.org or your platform’s official store: our builds are free, signed and never bundled with anything else.</p>']
    h.append('<div class="x-dl">')
    for key, name, rows in DL:
        h.append(f'<section class="x-dlg" data-os="{key}"><h2 id="dl-{key}">{e(name)}</h2><div class="x-rows">')
        for t, meta, url in rows:
            h.append(f'<a class="x-row" href="{e(url)}"><b>{e(t)}</b><span>{e(meta)}</span></a>')
        h.append('</div></section>')
    h.append('</div>')
    h.append('<div class="x-note"><b>Verify your download.</b> Each release ships with SHA-256 checksums and a GPG signature on our mirrors. VLC 3.0.24 checks updates with a new RSA-4096 key. See the <a href="https://www.videolan.org/security/">security centre</a>.</div>')
    return '\n'.join(h)

def news_item_html(n, full=True):
    body = n['html'] if full else re.sub(r'<[^>]+>', '', n['html'])
    return f'<article class="x-item" id="{e(n["id"])}"><time datetime="{e(n["date"])}">{nice_date(n["date"])}</time><div><h3>{e(n["title"])}</h3><div class="x-item-b">{body}</div></div></article>'

def news_years_nav(cur=None):
    ys = YEARS + (['undated'] if 'undated' in NEWS_BY_YEAR else [])
    return '<nav class="x-years" aria-label="News by year">' + ''.join(
        f'<a href="news--{y}.html"' + (' aria-current="page"' if y == cur else '') + f'>{y if y != "undated" else "Undated"} <small>{len(NEWS_BY_YEAR[y])}</small></a>' for y in ys) + '</nav>'

def news_hub_html():
    h = [f'<p class="x-lede">{len(NEWS)} announcements from VideoLAN, from 1999 to today. Browse by year, or read the latest below.</p>', news_years_nav(), '<div class="x-news">']
    h += [news_item_html(n) for n in NEWS[:24]]
    h.append('</div>')
    return '\n'.join(h)

def news_year_html(y):
    return '\n'.join([news_years_nav(y), '<div class="x-news">'] + [news_item_html(n) for n in NEWS_BY_YEAR[y]] + ['</div>'])

def section_hub_html(key):
    sec = SECTIONS[key]; items = ordered(key)
    h = [f'<p class="x-lede">{e(sec["blurb"])}</p>']
    if key == 'download':
        h.append('<p><a class="x-btn" href="download.html">Get VLC — all platforms at a glance</a></p>')
    h.append('<div class="x-list">')
    for p in items:
        h.append(f'<a class="x-li" href="{p["slug"]}.html"><b>{e(p["display"])}</b><span>{e(p["path"])}</span></a>')
    if key == 'news':
        for y in YEARS: h.append(f'<a class="x-li" href="news--{y}.html"><b>News from {y}</b><span>{len(NEWS_BY_YEAR[y])} items</span></a>')
    h.append('</div>')
    return '\n'.join(h)

def sitemap_html():
    h = [f'<p class="x-lede">Every page of videolan.org covered by this proposal: {len(PAGES)} pages carried over from the current site, plus new hubs. Links to VideoLAN services that are not redesigned yet (wiki, forums, GitLab, add-ons) show a short notice first.</p><div class="x-map">']
    for k, s in SECTIONS.items():
        items = ordered(k)
        h.append(f'<section><h2 id="map-{k}"><a href="section--{k}.html">{e(s["label"])}</a> <small>{len(items) + (len(YEARS) if k == "news" else 0)}</small></h2><ul>')
        for p in items: h.append(f'<li><a href="{p["slug"]}.html">{e(p["display"])}</a></li>')
        if k == 'news':
            for y in YEARS: h.append(f'<li><a href="news--{y}.html">News {y}</a></li>')
        h.append('</ul></section>')
    h.append('</div>')
    return '\n'.join(h)

NOTES_HTML = '''<p class="x-lede">Three independent design directions for videolan.org, built on the same content: every page of the current site, carried over into one static HTML5 bundle.</p>
<h2 id="what">What all three options share</h2>
<ul>
<li><b>The whole site, carried over.</b> {n} pages from videolan.org (downloads, release notes since 1.1, 50+ security bulletins, press, events since 2002, developer libraries, VLMa docs, skin editor help) plus {k} news items since 1999, regenerated as static pages.</li>
<li><b>One-click donations.</b> A full-screen checkout with Apple Pay, Google Pay, card and SEPA through VideoLAN’s existing Stripe checkout, PayPal one-time or monthly, bank transfer and Bitcoin. Setting a Stripe publishable key turns on embedded payment fields and the native wallet sheet.</li>
<li><b>Honest edges.</b> Links to VideoLAN services that are not redesigned yet (wiki, forums, GitLab, add-ons, documentation) open a short notice first. Direct downloads go straight to get.videolan.org.</li>
<li><b>Ready for {l} languages.</b> Each language is listed in its own script, with right-to-left support. Only English is written for now.</li>
<li><b>Accessible and light.</b> Static files, no framework, no web fonts, no cookies, no analytics. Text size, contrast, motion, underlined links and reading spacing settings. Pages work without JavaScript.</li>
</ul>
<h2 id="options">The three directions</h2>
<ul>
<li><b>A · Clean.</b> A warm, modern product site: clear hierarchy, CSS device mockups and a smart download button.</li>
<li><b>B · Player.</b> The website is VLC itself: the classic menu bar, a playlist sidebar, a seek bar that scrubs the page, VLC hotkeys, an “Open Media” search and switchable skins.</li>
<li><b>C · Almanac.</b> An editorial broadsheet: big type, numbered chapters, a 27-year news timeline and a wall of every format VLC plays.</li>
</ul>
<p>Unofficial concept by Paul Fleury, offered to VideoLAN under the MIT licence. VLC, VideoLAN and the cone are trademarks of VideoLAN. Content is adapted from videolan.org.</p>'''

def notes_html():
    return NOTES_HTML.format(n=len(PAGES), k=len(NEWS), l=81)

def virtual_pages():
    v = OrderedDict()
    v['download'] = dict(slug='download', display=f'Download VLC {VERSION}', title='Download VLC', section='Download', desc='Official downloads of VLC media player for every platform.', html=dl_hub_html(), words=300, path='/vlc/#download', virtual=True)
    v['news'] = dict(slug='news', display='News', title='News', section='News', desc='Announcements from VideoLAN.', html=news_hub_html(), words=1800, path='/news.html', virtual=True)
    for y in NEWS_BY_YEAR:
        v['news--' + y] = dict(slug='news--' + y, display=f'News from {y}' if y != 'undated' else 'Undated news', title=f'News {y}', section='News', desc='', html=news_year_html(y), words=sum(len(re.sub('<[^>]+>', ' ', n['html']).split()) for n in NEWS_BY_YEAR[y]), path='/news.html', virtual=True)
    for k, s in SECTIONS.items():
        v['section--' + k] = dict(slug='section--' + k, display=s['label'], title=s['label'], section=s['match'][0], desc=s['blurb'], html=section_hub_html(k), words=100, path='', virtual=True, hub=k)
    v['sitemap'] = dict(slug='sitemap', display='Site index', title='Site index', section='VideoLAN', desc='Every page on videolan.org.', html=sitemap_html(), words=400, path='', virtual=True)
    v['design-notes'] = dict(slug='design-notes', display='About this redesign', title='Design notes', section='VideoLAN', desc='Three design directions for videolan.org.', html=notes_html(), words=400, path='', virtual=True)
    return v

VIRTUAL = virtual_pages()

def all_pages():
    out = OrderedDict()
    for k, p in PAGES.items():
        if k == 'news': continue  # replaced by structured hub
        out[k] = p
    out.update(VIRTUAL)
    return out

ALL = all_pages()

def seq(slug):
    """prev/next within section"""
    p = ALL[slug]
    k = sec_key(p) if not p.get('virtual') else p.get('hub') or sec_key(p)
    items = [x['slug'] for x in ordered(k)] if k in SECTIONS else []
    if slug not in items: return None, None
    i = items.index(slug)
    return (items[i - 1] if i > 0 else None), (items[i + 1] if i < len(items) - 1 else None)

def search_index():
    idx = [['home', 'Home', 'Home']]
    for k, p in ALL.items():
        label = SECTIONS.get(sec_key(p), {}).get('label', p['section'])
        idx.append([k, p['display'], label])
    return idx

def latest_news(n=6): return NEWS[:n]
