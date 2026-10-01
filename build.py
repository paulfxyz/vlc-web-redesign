#!/usr/bin/env python3
"""Build the static single-page site: inject sprite + pre-render all content
so the page is fully readable with JavaScript disabled."""
import re, html, pathlib, gzip

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "dist"
OUT.mkdir(exist_ok=True)
e = html.escape

def ico(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} aria-hidden="true"><use href="#i-{name}"/></svg>'

ARROW = ico("arrow")

# ---------------- News ----------------
NEWS = [
    ("Sep 2026", "VLC 3.0.24 “Vetinari”", "Desktop",
     "A large update to VLC’s 3.0 branch: more than 130 security fixes across VLC and bundled libraries, 49 third-party libraries updated, FFmpeg moved from 4.4 to 8.1, ATRAC3 and ATRAC9 decoding, CEA-708 captions in MP4, SRT listener mode and SFTP public-key authentication. Update checks now use a new RSA-4096 key.",
     "https://www.videolan.org/vlc/releases/3.0.24.html"),
    ("Jan 2026", "VLC 3.0.23", "Desktop",
     "A maintenance and security release fixing several vulnerabilities in the handling of various media formats.",
     "https://www.videolan.org/security/"),
    ("2024", "VideoLAN Dev Days 2024 in South Korea", "Community",
     "Two days of technical talks with multimedia hackers from around the globe, hosted with the support of Kwangwoon University.",
     "https://www.videolan.org/videolan/events/"),
    ("2024", "VLC for Android 3.6", "Mobile",
     "The new Remote Access feature, parental control and a lot of fixes.",
     "https://www.videolan.org/vlc/download-android.html"),
    ("2024", "VLC 3.0.21", "Desktop",
     "The 22nd update to the 3.0 branch: codec updates, Super Resolution and VQ Enhancement filtering with AMD GPUs, NVIDIA TrueHDR for SDR sources, and improved subtitle rendering, notably on macOS with Asian languages. Also fixes a security issue.",
     "https://www.videolan.org/vlc/releases/3.0.21.html"),
    ("2024", "Major update of VLC for iOS, iPadOS and tvOS", "Mobile",
     "Playback history, A to B playback, Siri integration, external subtitles and audio tracks, favourite folders on local network servers, and improved CarPlay integration.",
     "https://www.videolan.org/vlc/download-ios.html"),
    ("2023", "VLC 3.0.20", "Desktop",
     "Codec updates, a FLAC quality fix, improved subtitle rendering and a fix for a freeze during frame-by-frame actions. Audio layout problems on macOS are resolved, and interface translations are updated. Also fixes two security issues.",
     "https://www.videolan.org/vlc/releases/3.0.20.html"),
    ("2023", "VLC for iOS, iPadOS and tvOS: new audio interface and CarPlay", "Mobile",
     "A new audio playback interface, CarPlay integration, local media library improvements, and tvOS support for the Apple Remote’s single click mode.",
     "https://www.videolan.org/press/"),
    ("2022", "VLC 3.0.18", "Desktop",
     "Support for a few more formats, improved adaptive streaming, crash fixes and many updated third-party libraries, plus multiple security fixes.",
     "https://www.videolan.org/vlc/releases/3.0.18.html"),
    ("2022", "VideoLAN supports the UNHCR", "Community",
     "VideoLAN is a de-facto pacifist organisation that believes in cooperation across countries and in the power of knowledge and sharing. In response to Russia’s invasion of Ukraine, it decided to financially support the United Nations High Commissioner for Refugees.",
     "https://www.videolan.org/press/"),
    ("2022", "A new major version of VLC for Android", "Mobile",
     "New widgets, network media indexation, better tablet and foldable support, a redesigned audio screen, improved accessibility and performance.",
     "https://www.videolan.org/vlc/download-android.html"),
]

def news_item(n):
    d, t, cat, body, url = n
    return (f'<article class="news-item" data-cat="{cat}"><time>{d}</time><div>'
            f'<h3><a href="{url}" style="color:inherit">{e(t)}</a></h3><p>{e(body)}</p>'
            f'<div class="tags"><span class="tag{" hot" if n is NEWS[0] else ""}">{cat}</span></div></div></article>')

news_list = "".join(news_item(n) for n in NEWS)
home_news = ""
for n in NEWS[:3] if False else [NEWS[0], NEWS[3], NEWS[5], NEWS[2], NEWS[4]]:
    d, t, cat, body, url = n
    short = body if n is NEWS[0] else (body[:120].rsplit(" ", 1)[0] + "…" if len(body) > 120 else body)
    home_news += (f'<a class="card" href="{url}"><time>{d} · {cat}</time><h3>{e(t)}</h3>'
                  f'<p>{e(short)}</p><span class="more">Read more {ARROW}</span></a>')

# ---------------- Specs ----------------
SPECS = [
    ("film", "Video codecs", "MPEG-1/2; DivX® (1/2/3/4/5/6); MPEG-4 ASP; XviD; 3ivX D4; H.261; H.263 / H.263i; H.264 / MPEG-4 AVC; H.265 / HEVC; AV1 (dav1d); VP8; VP9; Cinepak; Theora; Dirac / VC-2; MJPEG (A/B); WMV 1/2; WMV 3 / WMV-9 / VC-1; Sorenson 1/3; DV; On2 VP3/VP5/VP6; Indeo Video v3 (IV32); Real Video (1/2/3/4)"),
    ("volume", "Audio codecs", "MPEG Layer 1/2; MP3; AAC; Vorbis; Opus; AC3 - A/52; E-AC-3; MLP / TrueHD; DTS; WMA 1/2; WMA 3; FLAC; ALAC; Speex; Musepack / MPC; ATRAC 3; ATRAC 9; Wavpack; Mod; TrueAudio; APE; Real Audio; Alaw/µlaw; AMR (3GPP); MIDI; LPCM; ADPCM; QCELP; DV Audio; QDM2/QDMC; MACE"),
    ("cc", "Subtitles", "DVD; MicroDVD; SubRip; SubViewer; SSA 1-5; SAMI; VPlayer; WebVTT; Closed captions; CEA-708; Vobsub; Universal Subtitle Format (USF); SVCD / CVD; DVB; OGM; CMML; Kate"),
    ("box", "Containers & formats", "MPEG (ES, PS, TS, PVA, MP3); AVI; ASF / WMV / WMA; MP4 / MOV / 3GP; OGG / OGM / Annodex; Matroska (MKV); WebM; Real; WAV (incl. DTS); Raw audio: DTS, AAC, AC3/A52; Raw DV; FLAC; FLV (Flash); MXF; Nut; Standard MIDI / SMF; Creative™ Voice"),
    ("stream", "Inputs & sources", "UDP/RTP Unicast; UDP/RTP Multicast; HTTP / FTP; HLS; DASH; MMS; TCP/RTP Unicast; DCCP/RTP Unicast; SRT; RIST; SMB; SFTP; NFS; UPnP; File; DVD Video; Blu-ray; Video CD / VCD; SVCD; Audio CD (no DTS-CD); DVB (Satellite, Digital TV, Cable TV); MPEG encoder; Video acquisition"),
    ("news", "Metadata", "ID3 tags; APEv2; Vorbis comment; MusicBrainz; Cover Art Archive"),
    ("sparkle", "Other features", "Hardware decoding; 0-copy GPU; HDR10; 360° video; Ambisonics; Chromecast; SAP/SDP announces; Bonjour protocol; SVCD menus; Localisation; CD-Text; CDDB CD info; IGMPv3; IPv6; MLDv2; CPU acceleration"),
]
spec_html = ""
for i, (ic, title, items) in enumerate(SPECS):
    lst = [x.strip() for x in items.split(";")]
    chips = "".join(f'<span class="chip">{e(x)}</span>' for x in lst)
    op = " open" if i == 0 else ""
    spec_html += (f'<details class="spec"{op}><summary>{ico(ic, "ico")}{e(title)}<span class="count">{len(lst)}</span>'
                  f'{ico("chev", "chev")}</summary><div class="chips">{chips}</div></details>')

# ---------------- Projects ----------------
PROJ = [
    ("For everyone", [
        ("play", "VLC media player", "A powerful media player playing most of the media codecs and video formats out there.", "#download", "Flagship"),
        ("film", "VLMC", "VideoLAN Movie Creator, a non-linear editing software for video creation.", "https://www.videolan.org/vlmc/", ""),
        ("palette", "VLC Skin Editor", "Create your own skins for VLC media player.", "https://www.videolan.org/vlc/skineditor.html", ""),
    ]),
    ("For professionals", [
        ("stream", "DVBlast", "A simple and powerful MPEG-2/TS demux and streaming application.", "https://www.videolan.org/projects/dvblast.html", ""),
        ("film", "x264", "A free application for encoding video streams into the H.264/MPEG-4 AVC format.", "https://www.videolan.org/developers/x264.html", "Industry standard"),
        ("film", "x262 & x265", "Encoders for MPEG-2 and H.265/HEVC video.", "https://www.videolan.org/developers/x265.html", ""),
        ("wifi", "multicat", "A set of tools to easily and efficiently manipulate multicast streams and TS.", "https://www.videolan.org/projects/multicat.html", ""),
        ("tv", "VLMa", "Manage broadcasts of TV channels received through digital terrestrial or satellite.", "https://www.videolan.org/projects/", ""),
    ]),
    ("For developers", [
        ("code", "libVLC", "The cross-platform multimedia framework. Bring VLC power into your app.", "https://www.videolan.org/vlc/libvlc.html", "Popular"),
        ("zap", "dav1d", "An AV1 cross-platform decoder, open source, focused on speed, size and correctness.", "https://code.videolan.org/videolan/dav1d", "Popular"),
        ("box", "vlc-unity", "VLC for the Unity game engine.", "https://code.videolan.org/videolan/vlc-unity", ""),
        ("disc", "libdvdcss", "The reference open source cross-platform library for DVD CSS decryption.", "https://www.videolan.org/developers/libdvdcss.html", ""),
        ("disc", "libdvdnav", "The reference library for DVD menu handling.", "https://www.videolan.org/developers/libdvdnav.html", ""),
        ("disc", "libdvdread", "The reference library for reading DVD video images.", "https://www.videolan.org/developers/libdvdnav.html", ""),
        ("disc", "libbluray", "The reference open source cross-platform library for Blu-ray disc access.", "https://www.videolan.org/developers/libbluray.html", ""),
        ("lock", "libaacs & libbdplus", "Research projects implementing the AACS and BD+ standards.", "https://www.videolan.org/developers/libaacs.html", ""),
        ("lock", "libdvbcsa", "Decrypt and encrypt using the DVB-CSA algorithm.", "https://www.videolan.org/developers/libdvbcsa.html", ""),
        ("stream", "libdvbpsi", "Parse TS and DVB tables without headaches.", "https://www.videolan.org/developers/libdvbpsi.html", ""),
        ("code", "biTStream", "Abstract access to binary structures such as those found in MPEG or DVB.", "https://www.videolan.org/developers/bitstream.html", ""),
        ("volume", "libdca", "Decode the DTS Coherent Acoustics audio codec.", "https://www.videolan.org/developers/libdca.html", ""),
    ]),
]
proj_html = ""
for group, items in PROJ:
    cards = ""
    for ic, name, desc, url, tag in items:
        t = f'<span class="tag hot" style="margin-bottom:.8rem">{tag}</span>' if tag else ""
        cards += (f'<a class="card" href="{url}">{t}<h3>{ico(ic)}{e(name)}</h3><p>{e(desc)}</p>'
                  f'<span class="more">Learn more {ARROW}</span></a>')
    proj_html += (f'<div style="margin-bottom:3rem"><p class="eyebrow">{group}</p><div class="grid-3">{cards}</div></div>')

# ---------------- People ----------------
PEOPLE = [
    ("Jean-Baptiste Kempf", "President · VLC maintainer"),
    ("Christophe Massiot", "Co-founder · DVBlast, multicat"),
    ("Rémi Denis-Courmont", "Core developer"),
    ("Felix Paul Kühne", "macOS, iOS &amp; tvOS"),
    ("Thomas Guillem", "Core &amp; Android"),
    ("Steve Lhomme", "Windows &amp; Matroska"),
    ("François Cartegnie", "Demux &amp; streaming"),
    ("Hugo Beauzée-Luyssen", "Media library"),
    ("Martin Storsjö", "Toolchains &amp; ARM"),
    ("Laurent Aimar", "Core &amp; codecs"),
    ("Marvin Scholz", "macOS &amp; infrastructure"),
    ("Pierre d’Herbemont", "Early macOS &amp; iOS"),
]
def initials(n):
    p = [x for x in re.split(r"[\s-]", n) if x]
    return (p[0][0] + p[-1][0]).upper()
people_html = "".join(f'<div class="person"><span class="avatar" aria-hidden="true">{initials(n)}</span><span><b>{e(n)}</b><span>{r}</span></span></div>' for n, r in PEOPLE)

# ---------------- Partners ----------------
PARTNERS = [
    ("Free", "French ISP hosting 3 VideoLAN servers near Paris; sponsored the 2008 and 2013 Dev Days."),
    ("Gandi", "Manages VideoLAN domain names and helps with administrative tasks."),
    ("MacStadium", "Provides a Mac mini for continuous integration builds."),
    ("Videolabs", "Founded by VideoLAN members; editor of the VLC mobile apps."),
    ("MetaBrainz", "MusicBrainz and Cover Art Archive data enrich VLC."),
    ("École Centrale Paris", "Historic partner where the project was born."),
    ("EPITECH", "Hosted and sponsored the second Dev Days in 2009."),
    ("Anevia", "Founded by four VideoLAN team members; professional video servers."),
    ("Puget Systems", "Donated an Echo II for Intel GPU acceleration work."),
    ("Panasonic", "Lent a 5.1 setup to fix optical audio output on macOS."),
    ("TASCAM", "Lent a MIDI interface for multi-buffer audio output support."),
    ("ZF Electronics", "Donated Cherry keyboards for media hotkey support."),
    ("WD", "Donated wireless drives to improve UPnP and network discovery."),
    ("Andrew Beveridge", "Donated a virtual server to help build each release."),
]
partner_html = "".join(f'<div class="partner"><span class="wm">{e(n)}</span><span>{e(d)}</span></div>' for n, d in PARTNERS)

# ---------------- Donate band ----------------
def donate(idp):
    return f'''<div style="position:relative">
<p class="eyebrow">Support VideoLAN</p>
<h2>Keep VLC free, for everyone, forever.</h2>
<p>VLC has no ads and no tracking because it does not need them. It is made by volunteers and run by a non-profit. Your donation pays for servers, bandwidth, test hardware and developer meetings.</p>
</div>
<form class="amounts" action="https://www.videolan.org/contribute.html#money" method="get" aria-label="Choose a donation amount">
<fieldset class="freq" style="border:0;padding:0;margin:0 0 .2rem"><legend class="sr-only">Frequency</legend>
<label><input type="radio" name="f{idp}" value="once" checked> One time</label>
<label><input type="radio" name="f{idp}" value="monthly"> Monthly</label></fieldset>
<button type="button" aria-pressed="false" data-amt="5">€5</button>
<button type="button" aria-pressed="true" data-amt="10">€10</button>
<button type="button" aria-pressed="false" data-amt="25">€25</button>
<button type="button" aria-pressed="false" data-amt="50">€50</button>
<button type="button" aria-pressed="false" data-amt="100">€100</button>
<button type="button" aria-pressed="false" data-amt="other">Other</button>
<a class="btn btn-primary" href="https://www.videolan.org/contribute.html#money" data-donate>{ico("heart")}<span>Donate <span data-amt-label>€10</span></span></a>
<small>Secure payment via PayPal, bank transfer, Monero or Bitcoin.</small>
</form>'''

# ---------------- Ticker ----------------
FORMATS = "H.264 HEVC AV1 VP9 MPEG-2 MKV WebM MP4 MOV AVI FLAC Opus AAC MP3 DTS TrueHD AC-3 WMV OGG DVD Blu-ray HLS DASH RTSP SRT WebVTT ASS 4K 8K HDR10 360°".split()
ticker = "".join(f"<span>{e(f)}</span>" for f in FORMATS) * 2

# ---------------- Languages ----------------
LANGS = [
 ("en","English","English"),("fr","Français","French"),("de","Deutsch","German"),("es","Español","Spanish"),
 ("pt-PT","Português (Portugal)","Portuguese"),("pt-BR","Português (Brasil)","Brazilian Portuguese"),("it","Italiano","Italian"),
 ("nl","Nederlands","Dutch"),("pl","Polski","Polish"),("ru","Русский","Russian"),("uk","Українська","Ukrainian"),
 ("cs","Čeština","Czech"),("sk","Slovenčina","Slovak"),("hu","Magyar","Hungarian"),("ro","Română","Romanian"),
 ("bg","Български","Bulgarian"),("el","Ελληνικά","Greek"),("tr","Türkçe","Turkish"),("ar","العربية","Arabic"),
 ("he","עברית","Hebrew"),("fa","فارسی","Persian"),("ur","اردو","Urdu"),("ps","پښتو","Pashto"),("hi","हिन्दी","Hindi"),
 ("bn","বাংলা","Bengali"),("pa","ਪੰਜਾਬੀ","Punjabi"),("gu","ગુજરાતી","Gujarati"),("mr","मराठी","Marathi"),
 ("ta","தமிழ்","Tamil"),("te","తెలుగు","Telugu"),("kn","ಕನ್ನಡ","Kannada"),("ml","മലയാളം","Malayalam"),
 ("si","සිංහල","Sinhala"),("ne","नेपाली","Nepali"),("th","ไทย","Thai"),("vi","Tiếng Việt","Vietnamese"),
 ("id","Bahasa Indonesia","Indonesian"),("ms","Bahasa Melayu","Malay"),("fil","Filipino","Filipino"),
 ("zh-Hans","简体中文","Chinese (Simplified)"),("zh-Hant","繁體中文","Chinese (Traditional)"),("ja","日本語","Japanese"),
 ("ko","한국어","Korean"),("sv","Svenska","Swedish"),("nb","Norsk bokmål","Norwegian"),("da","Dansk","Danish"),
 ("fi","Suomi","Finnish"),("is","Íslenska","Icelandic"),("et","Eesti","Estonian"),("lv","Latviešu","Latvian"),
 ("lt","Lietuvių","Lithuanian"),("sl","Slovenščina","Slovenian"),("hr","Hrvatski","Croatian"),("sr","Српски","Serbian"),
 ("bs","Bosanski","Bosnian"),("mk","Македонски","Macedonian"),("sq","Shqip","Albanian"),("ca","Català","Catalan"),
 ("eu","Euskara","Basque"),("gl","Galego","Galician"),("cy","Cymraeg","Welsh"),("ga","Gaeilge","Irish"),
 ("br","Brezhoneg","Breton"),("oc","Occitan","Occitan"),("eo","Esperanto","Esperanto"),("sw","Kiswahili","Swahili"),
 ("af","Afrikaans","Afrikaans"),("zu","isiZulu","Zulu"),("am","አማርኛ","Amharic"),("ha","Hausa","Hausa"),
 ("yo","Yorùbá","Yoruba"),("kk","Қазақ тілі","Kazakh"),("uz","Oʻzbekcha","Uzbek"),("az","Azərbaycanca","Azerbaijani"),
 ("ka","ქართული","Georgian"),("hy","Հայերեն","Armenian"),("mn","Монгол","Mongolian"),("km","ភាសាខ្មែរ","Khmer"),
 ("lo","ລາວ","Lao"),("my","မြန်မာ","Burmese"),("ku","Kurdî","Kurdish"),
]
RTL = {"ar","he","fa","ur","ps"}
lang_html = ""
for code, native, eng in LANGS:
    d = ' dir="rtl"' if code in RTL else ""
    st = '<span class="st">Available</span>' if code == "en" else '<span>' + e(eng) + '</span>'
    lang_html += (f'<button type="button" lang="{code}" data-lang="{code}" data-native="{e(native)}" data-en="{e(eng)}"'
                  f' aria-pressed="{"true" if code=="en" else "false"}"><b{d}>{e(native)}</b>{st}</button>')
assert len(LANGS) == 81, len(LANGS)

# ---------------- Assemble ----------------
src = (ROOT / "index.src.html").read_text()
sprite = (ROOT / "sprite.svg.part").read_text()
sprite = re.sub(r'^<g fill="none"[^>]*>\n|^</g>\n', "", sprite, flags=re.M)
src = src.replace("<!--SPRITE-->", sprite)
def fill(id_, content):
    global src
    pat = re.compile(r'(<div [^>]*id="%s"[^>]*>)(</div>)' % id_)
    assert pat.search(src), id_
    src = pat.sub(lambda m: m.group(1) + content + m.group(2), src, count=1)
fill("home-news", home_news)
fill("spec-list", spec_html)
fill("project-list", proj_html)
fill("news-list", news_list)
fill("people", people_html)
fill("partner-list", partner_html)
fill("donate-home", donate("h"))
fill("donate", donate("c"))
fill("ticker", ticker)
fill("lang-grid", lang_html)
# xlink fallback for older WebKit
src = re.sub(r'<use href="([^"]+)"', r'<use href="\1" xlink:href="\1"', src)

(OUT / "index.html").write_text(src)
for f in ["styles.css", "app.js", "favicon.svg"]:
    (OUT / f).write_bytes((ROOT / f).read_bytes())
tot = sum(len(gzip.compress((OUT / f).read_bytes(), 9)) for f in ["index.html", "styles.css", "app.js", "favicon.svg"])
raw = sum(len((OUT / f).read_bytes()) for f in ["index.html", "styles.css", "app.js", "favicon.svg"])
print(f"raw {raw/1024:.1f} KB, gzip {tot/1024:.1f} KB")
