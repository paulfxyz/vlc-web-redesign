"""English source strings for the VideoLAN landing (org_home), the Projects menu and the brand line.

Translations live in content/org_i18n.json ({key: {fr, zh, ar}}), produced by tools/translate_org.py
(OpenRouter: translate, then native-speaker proofread). Placeholders in {braces} must be kept.
"""
import json, pathlib

EN = {
    # brand + head
    'brand_sub': 'Open source multimedia',
    'title': 'VideoLAN — Open source multimedia, for everyone',
    'desc': 'VideoLAN is the non-profit behind VLC media player and a family of open source multimedia projects: dav1d, x264, libVLC, libdvdcss, libbluray, DVBlast and more.',
    # hero
    'kick': 'VideoLAN · non-profit · 30 years of open source',
    'h1a': 'Open source multimedia,',
    'h1b': 'for everyone.',
    'lede_a': 'VideoLAN is a non-profit and a community of volunteers building free multimedia software since 1996:',
    'lede_vlc': 'VLC media player',
    'lede_b': ', and the codecs, disc libraries and broadcast tools inside the browsers, phones and TV networks you use every day.',
    'explore': 'Explore all {n} projects',
    'trust1': 'Free and open source',
    'trust2': 'Non-profit, independent',
    'trust3': 'No ads, no tracking',
    'bento_label': 'VideoLAN projects',
    'flagship_v': 'Our flagship · {v}',
    'discover': 'Discover',
    'more_projects': 'more projects',
    'b_dav1d': 'AV1 decoder in your browser',
    'b_x264': 'The H.264 encoder',
    'b_libvlc': 'Engine for your app',
    'b_libbluray': 'Blu-ray playback',
    'b_dvblast': 'Streams for TV networks',
    # numbers
    'nums_label': 'VideoLAN in numbers',
    'n_1996': 'a student project at École Centrale Paris',
    'n_dl_v': '7 billion+',
    'n_dl': 'VLC downloads counted since 2005',
    'n_pj': 'open source projects',
    'n_ppl': 'named contributors',
    'n_vdd': 'Dev Days in seven cities',
    'n_zero': 'ads, trackers or investors',
    # stack
    'st_kick': 'Inside the video you watch',
    'st_h': 'You already use VideoLAN',
    'st_p': 'Even if you have never opened VLC, chances are VideoLAN code decoded, encoded or carried the last video you watched. Here is how the pieces fit together.',
    'st_label': 'The VideoLAN software stack',
    'l_apps': 'Apps', 'l_apps_d': 'What people install', 'your_app': 'Your app',
    'l_engine': 'Engine', 'l_engine_d': 'Embed it anywhere', 'engine_note': 'LGPL since 2011 · bindings for most languages',
    'l_codecs': 'Codecs', 'l_codecs_d': 'Decode and encode',
    'l_discs': 'Discs', 'l_discs_d': 'DVD and Blu-ray',
    'l_bcast': 'Broadcast', 'l_bcast_d': 'TV networks and studios',
    'f_dav1d': 'The fastest AV1 software decoder, built with the FFmpeg community for the Alliance for Open Media.',
    'f_x264': 'The most popular software video encoder in the world, behind a huge share of online video.',
    'f_libvlc': 'The engine of VLC, ready to embed in your own app on desktop, mobile and TV.',
    # VLC band
    'v_kick': 'Our flagship',
    'v_lede': 'The free, cross-platform player that plays just about anything, used by hundreds of millions of people. Built on libVLC, the same engine developers embed in their own apps.',
    'vp1': 'Plays everything', 'vp1_d': 'Files, discs, webcams, devices and streams, with no codec packs to install.',
    'vp2': 'Fast everywhere', 'vp2_d': 'Hardware decoding on most platforms, from 8K HDR to old laptops.',
    'vp3': 'On every screen', 'vp3_d': 'Windows, macOS, Linux, Android, iOS, Apple TV, ChromeOS and more.',
    'vp4': 'Private by design', 'vp4_d': 'No ads, no tracking, no accounts. Ever.',
    'discover_vlc': 'Discover VLC', 'all_dl': 'All downloads', 'features': 'Features',
    # about
    'a_kick': 'About VideoLAN',
    'a_h': 'A project, and a non-profit',
    'a_p': 'VideoLAN started as a student project in Paris and grew into one of the largest open source multimedia communities in the world. Today it is run by volunteers and a small board, funded by donations and partners, and accountable to no one but its users.',
    'val1': 'Independent', 'val1_d': 'No investors and no company behind it. An autonomous non-profit association under French law since 2009.',
    'val2': 'Open', 'val2_d': 'Every line of code is free software, released under the GPL, LGPL, BSD and other open licences.',
    'val3': 'Private', 'val3_d': 'No ads, no tracking, no data sold. Not now, not ever.',
    'val4': 'Worldwide', 'val4_d': 'Developers from more than 40 countries; VLC translated into more than 100 languages.',
    'tl_h': 'Thirty years, 1996–2026',
    'tl_label': 'VideoLAN timeline, 1996 to 2026',
    'earlier': 'Earlier', 'later': 'Later',
    't1996': 'Campus TV', 't1996_d': 'Students at École Centrale Paris start VideoLAN to stream video across the campus network.',
    't1998': 'A fresh start', 't1998_d': 'The code is rewritten from scratch, laying the foundations of today’s VLC.',
    't2001': 'Free software', 't2001_d': 'On 1 February, the École agrees to release everything under the GNU GPL.',
    't2004': 'x264', 't2004_d': 'Work starts on x264, which becomes the reference H.264 encoder.',
    't2008': 'First Dev Days', 't2008_d': 'The community meets in Paris for the first VideoLAN Dev Days.',
    't2009': 'Independent', 't2009_d': 'VideoLAN separates from the École and is run by its own non-profit.',
    't2011': 'libVLC goes LGPL', 't2011_d': 'The engine is relicensed so any app, free or not, can embed it.',
    't2012': 'Backed by 3,080 people', 't2012_d': 'A Kickstarter raises £47,056 to bring VLC to Windows 8, RT and Phone.',
    't2013': 'Back on iPhone', 't2013_d': 'VLC for iOS returns to the App Store, free in every country.',
    't2016': 'Apple TV', 't2016_d': 'VLC arrives on the living-room screen.',
    't2017': 'AV1', 't2017_d': 'VideoLAN joins the Alliance for Open Media to build a royalty-free codec.',
    't2018': 'dav1d', 't2018_d': 'The AV1 decoder starts with the FFmpeg community and soon ships in browsers.',
    't2021': '20 years open', 't2021_d': 'Two decades of free software and more than 3.5 billion downloads.',
    't2025': 'AI subtitles', 't2025_d': 'At CES, VideoLAN demos on-device subtitle generation and translation for VLC 4.0.',
    't2026': 'Thirty years', 't2026_d': 'The 15th Dev Days in Rome, VLC {v} with 130+ security fixes, and 7 billion downloads.',
    'about_org': 'About the organisation',
    # projects
    'p_kick': 'Projects',
    'p_h': 'Much more than a media player',
    'p_p': 'VLC is the best known, but VideoLAN maintains {n} open source projects: codecs, disc libraries and broadcast tools that power browsers, operating systems, streaming services and TV networks.',
    'since_y': 'since {y}',
    'p_btn': 'Projects & developers',
    # people
    'pe_kick': 'People',
    'pe_h': 'Made by a community',
    'pe_p': '{n} named contributors in code, translation, artwork and documentation, from more than 40 countries, meeting every year at the VideoLAN Dev Days.',
    'photo_alt': 'VideoLAN Dev Days 2014 group photo',
    'board': 'The board',
    'meet_team': 'Meet the team',
    'events_vdd': 'Events & Dev Days',
    'vdd_h': '{n} editions, from Paris to Rome',
    'vdd_p': 'Every year the community meets for two or three days of talks and hacking, together with FFmpeg, x264, Kodi and friends. VideoLAN also has a booth at FOSDEM, CES, SCaLE, COSCUP and Open Source Experience.',
    'all_events': 'All events',
    'partners': 'Partners and supporters',
    'all_partners': 'All partners & consultants',
    'c_paris': 'Paris', 'c_dublin': 'Dublin', 'c_berlin': 'Berlin', 'c_tokyo': 'Tokyo', 'c_seoul': 'Seoul', 'c_london': 'London', 'c_rome': 'Rome',
    # news / involved / org
    'nw_kick': 'News', 'nw_h': 'Latest from VideoLAN',
    'gi_kick': 'Get involved',
    'gi_h': 'VideoLAN is made by people like you',
    'gi_p': 'Everyone can help, whether you write code, speak another language, design, test or simply donate.',
    'gi1': 'Write code', 'gi1_d': 'Fix a bug or build a feature in VLC, dav1d, x264 or any other project.',
    'gi2': 'Translate', 'gi2_d': 'Bring VLC and its website to your language.',
    'gi3': 'Help users', 'gi3_d': 'Answer questions on the forum, the wiki and IRC.',
    'gi4': 'Test and report', 'gi4_d': 'Try nightly builds and report what breaks.',
    'o_kick': 'The organisation', 'o_h': 'Everything else, in one place',
    'o_press': 'Press', 'o_legal': 'Legal', 'o_privacy': 'Privacy', 'o_security': 'Security', 'o_mirrors': 'Mirrors', 'o_contact': 'Contact',
    # projects menu
    'mg_lede': '{n} open source projects, one non-profit.',
    'mg_all': 'All projects & developers',
    'mg_src': 'Source code',
    'r_vlc': 'Media player', 'r_libvlc': 'Embeddable media engine', 'r_dav1d': 'AV1 decoder', 'r_x264': 'H.264 encoder',
    'r_dvblast': 'DVB streaming', 'r_multicat': 'Multicast tools', 'r_vlmc': 'Video editor', 'r_libdvdcss': 'DVD access',
    'r_libdvdnav': 'DVD menus', 'r_libbluray': 'Blu-ray playback', 'r_libaacs': 'AACS and BD+', 'r_libdvbpsi': 'MPEG TS tables',
    'r_bitstream': 'Stream headers', 'r_libdvbcsa': 'DVB scrambling', 'r_libdca': 'DTS decoder', 'r_vlma': 'TV broadcast manager',
}

# where each string appears, for translator context
CONTEXT = {
    'brand_sub': 'tagline under the VideoLAN logo in the header, max ~24 chars',
    'kick': 'small uppercase eyebrow above the homepage headline',
    'h1a': 'homepage headline, first line', 'h1b': 'homepage headline, second line (highlighted)',
    'lede_a': 'hero paragraph, part before the linked words "VLC media player"', 'lede_vlc': 'link text (product name, usually unchanged)',
    'lede_b': 'hero paragraph, part right after the link; starts with a comma in English — adapt punctuation to the language',
    'more_projects': 'shown under a big "+10" on a tile', 'n_dl_v': 'big number in a statistics strip',
    'l_apps': 'layer name in a software stack diagram (short)', 'your_app': 'chip in the diagram meaning the reader\'s own application',
    'earlier': 'button label (screen readers) to scroll a timeline back', 'later': 'button label to scroll a timeline forward',
    'since_y': 'small meta line after a licence name, e.g. "GPLv2 · since 2001"',
    'board': 'heading: board of directors of the association',
    'mg_lede': 'heading at the top of the Projects menu panel; {n} = 16',
    'explore': 'button; {n} = 16', 'p_p': '{n} = 16', 'pe_p': '{n} = 1,062 (number of people)', 'vdd_h': '{n} = 15 (editions)',
    'n_pj': 'label shown under the big number 16 — must agree grammatically with 16', 'n_ppl': 'label under the big number 1,062 — agree with that number',
    'n_vdd': 'label under the big number 15 — agree with 15', 'n_dl': 'label under the big figure "7 billion+" — agree with it',
    'n_zero': 'label under the big number 0 (zero ads, trackers or investors)', 'n_1996': 'label under the big year 1996',
}
def _ctx_news():
    pass
for k in list(EN):
    if k.startswith('r_'): CONTEXT.setdefault(k, 'one-line role of a software project in a menu, 1-4 words')
    if k.startswith('c_'): CONTEXT.setdefault(k, 'city name (Video Dev Days host city)')
    if k.startswith('t') and k[1:5].isdigit(): CONTEXT.setdefault(k, 'timeline card ' + ('text' if k.endswith('_d') else 'title (short)'))

def news_src():
    """Titles and card excerpts of the five latest news posts shown on the homepages."""
    import re, html, vlsite as S
    out = {}
    for n in S.NEWS[:5]:
        txt = ' '.join(re.sub(r'<[^>]+>', ' ', html.unescape(n['html'])).split())
        txt = txt[:220].rsplit(' ', 1)[0] + '…' if len(txt) > 220 else txt
        out[f"nw_{n['id']}_t"] = n['title']
        out[f"nw_{n['id']}_x"] = txt
    return out

def source():
    d = dict(EN); d.update(news_src()); return d

def news_tr(lang, nid, part):
    if lang == 'en': return None
    import i18n as I
    if lang not in I.BASE: return I.CAT.get(lang, {}).get(f'o:nw_{nid}_{part}')
    return tr().get(f'nw_{nid}_{part}', {}).get(lang)

_TR = None
def tr():
    global _TR
    if _TR is None:
        p = pathlib.Path(__file__).resolve().parent.parent / 'content' / 'org_i18n.json'
        _TR = json.loads(p.read_text()) if p.exists() else {}
    return _TR

def ot(lang, key, **kw):
    import i18n as I
    if lang not in I.BASE: s = I.cat(lang, 'o:' + key)
    else: s = EN[key] if lang == 'en' else tr().get(key, {}).get(lang)
    if s is None: raise KeyError(f'missing {lang} translation for {key}')
    return s.format(**kw) if kw else s
