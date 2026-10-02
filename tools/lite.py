"""Simple, dependency-free page for old browsers / slow devices (HTML 4-safe CSS, no JS)."""
from html import escape as e
import i18n as I
LS = {
 'title': ('VLC media player — simple version', 'VLC media player — version simple', 'VLC 媒体播放器 — 简易版', 'مشغّل الوسائط VLC — النسخة المبسّطة'),
 'note': ('You are seeing the simple version of this site, made for older browsers, older devices and slow connections.', 'Vous voyez la version simple de ce site, conçue pour les anciens navigateurs, les anciens appareils et les connexions lentes.', '你正在浏览本站的简易版，专为旧版浏览器、旧设备和慢速网络设计。', 'أنت تتصفح النسخة المبسّطة من هذا الموقع، المصمّمة للمتصفحات والأجهزة القديمة والاتصالات البطيئة.'),
 'full': ('Open the full site', 'Ouvrir le site complet', '打开完整版网站', 'افتح الموقع الكامل'),
 'lead': ('VLC is a free and open source cross-platform multimedia player that plays most multimedia files, DVDs, Audio CDs, VCDs and streaming protocols.', 'VLC est un lecteur multimédia libre et gratuit, multiplateforme, qui lit la plupart des fichiers multimédias, les DVD, CD audio, VCD et protocoles de streaming.', 'VLC 是一款自由、开源的跨平台多媒体播放器，可播放大多数多媒体文件、DVD、音频 CD、VCD 以及各种流媒体协议。', 'VLC مشغّل وسائط حرّ ومفتوح المصدر ومتعدد المنصّات، يشغّل معظم ملفات الوسائط وأقراص DVD والأقراص الصوتية وVCD وبروتوكولات البث.'),
 'dl': ('Download VLC {v}', 'Télécharger VLC {v}', '下载 VLC {v}', 'تنزيل VLC {v}'),
 'free': ('Free, no ads, no tracking. Files come from the official VideoLAN servers.', 'Gratuit, sans publicité ni pistage. Les fichiers proviennent des serveurs officiels de VideoLAN.', '免费、无广告、无追踪。文件来自 VideoLAN 官方服务器。', 'مجاني بلا إعلانات ولا تتبّع. الملفات من خوادم VideoLAN الرسمية.'),
 'w64': ('Windows 64-bit', 'Windows 64 bits', 'Windows 64 位', 'ويندوز 64 بت'),
 'w32': ('Windows 32-bit (older PCs, Windows XP SP3 and later)', 'Windows 32 bits (anciens PC, Windows XP SP3 et plus)', 'Windows 32 位（旧电脑，Windows XP SP3 及以上）', 'ويندوز 32 بت (الحواسيب القديمة، ويندوز XP SP3 فما فوق)'),
 'warm': ('Windows on ARM', 'Windows sur ARM', 'ARM 版 Windows', 'ويندوز على ARM'),
 'mac': ('macOS', 'macOS', 'macOS', 'macOS'),
 'inst': ('Installer', 'Installateur', '安装程序', 'برنامج التثبيت'), 'msi': ('MSI package', 'Paquet MSI', 'MSI 安装包', 'حزمة MSI'),
 'zip': ('Portable ZIP', 'ZIP portable', '便携版 ZIP', 'ZIP محمول'), '7z': ('7-Zip archive', 'Archive 7-Zip', '7-Zip 压缩包', 'أرشيف 7-Zip'),
 'uni': ('Universal (Apple Silicon and Intel)', 'Universel (Apple Silicon et Intel)', '通用版（Apple 芯片与 Intel）', 'عالمي (Apple Silicon وIntel)'),
 'as': ('Apple Silicon only', 'Apple Silicon uniquement', '仅 Apple 芯片', 'Apple Silicon فقط'), 'intel': ('Intel only', 'Intel uniquement', '仅 Intel', 'Intel فقط'),
 'linux': ('GNU/Linux', 'GNU/Linux', 'GNU/Linux', 'GNU/Linux'),
 'linux_p': ('Install VLC from your distribution with one command:', 'Installez VLC depuis votre distribution en une commande :', '用一条命令从你的发行版安装 VLC：', 'ثبّت VLC من توزيعتك بأمر واحد:'),
 'mobile': ('Phones, tablets and TV', 'Téléphones, tablettes et TV', '手机、平板和电视', 'الهواتف والأجهزة اللوحية والتلفاز'),
 'src': ('Source code', 'Code source', '源代码', 'الشيفرة المصدرية'),
 'older': ('Older versions and other systems', 'Anciennes versions et autres systèmes', '旧版本与其他系统', 'الإصدارات القديمة والأنظمة الأخرى'),
 'verify': ('Check a file with its SHA-256 fingerprint, listed under each link.', 'Vérifiez un fichier avec son empreinte SHA-256, indiquée sous chaque lien.', '可用每个链接下方的 SHA-256 指纹校验文件。', 'تحقّق من الملف ببصمة SHA-256 المذكورة تحت كل رابط.'),
 'more': ('More', 'Plus', '更多', 'المزيد'),
 'donate': ('Donate to VideoLAN', 'Faire un don à VideoLAN', '向 VideoLAN 捐款', 'تبرّع لـ VideoLAN'),
 'help': ('Help and forum', 'Aide et forum', '帮助与论坛', 'المساعدة والمنتدى'),
 'about': ('About VideoLAN', 'À propos de VideoLAN', '关于 VideoLAN', 'عن VideoLAN'),
 'news': ('News', 'Actualités', '新闻', 'الأخبار'),
 'lang': ('Language', 'Langue', '语言', 'اللغة'),
 'mb': ('{n} MB', '{n} Mo', '{n} MB', '{n} م.ب'),
 'np': ('VideoLAN is a non-profit organization. VLC is free software, released under the GPLv2.', 'VideoLAN est une association à but non lucratif. VLC est un logiciel libre, publié sous licence GPLv2.', 'VideoLAN 是非营利组织。VLC 是以 GPLv2 发布的自由软件。', 'VideoLAN منظمة غير ربحية. VLC برنامج حرّ صادر بترخيص GPLv2.'),
}
LI = {'en': 0, 'fr': 1, 'zh': 2, 'ar': 3}
CSS = ('body{margin:0;padding:0;background:#fff;color:#1a1a1a;font-family:Arial,Helvetica,"Noto Sans",sans-serif;font-size:18px;line-height:1.55}'
 '.w{max-width:760px;margin:0 auto;padding:16px 18px 40px}'
 '.n{background:#fff4e5;border:1px solid #f0b46a;padding:12px 14px;margin:0 0 18px;font-size:16px}'
 'h1{font-size:30px;line-height:1.2;margin:8px 0 10px}h2{font-size:22px;margin:30px 0 8px;padding-top:14px;border-top:1px solid #ddd}h3{font-size:18px;margin:18px 0 6px}'
 'a{color:#a63c00}a:visited{color:#7a2e00}a:focus{outline:3px solid #1a1a1a;outline-offset:2px}'
 'ul{padding-left:22px;padding-right:22px;margin:6px 0}li{margin:0 0 10px}'
 '.s{display:block;text-align:left;color:#555;font-size:13px;font-family:"Courier New",monospace;word-wrap:break-word;overflow-wrap:anywhere}'
 'pre{background:#f3f3f3;border:1px solid #ddd;padding:8px 10px;font-size:15px;white-space:pre-wrap;word-wrap:break-word;margin:4px 0 12px}'
 '.b{display:inline-block;background:#ff8800;color:#000;font-weight:bold;padding:12px 18px;text-decoration:none;font-size:19px;margin:6px 0}'
 '.f{margin-top:36px;padding-top:14px;border-top:1px solid #ddd;font-size:15px;color:#444}'
 '@media (prefers-color-scheme:dark){body{background:#111;color:#eee}.n{background:#2a1c08;border-color:#7a4a10}a,a:visited{color:#ffad5c}h2,.f{border-color:#333}pre{background:#1d1d1d;border-color:#333}.s,.f{color:#bbb}a:focus{outline-color:#fff}}')

def page(lang, F, V, STORE, LINUX):
    i = LI[lang]; L = lambda k, **kw: LS[k][i].format(**kw)
    m = I.META[lang]; base = ''; root = '' if lang == 'en' else '../'
    def f(k, label):
        x = F[k]; return f'<li><a href="{x["url"]}">{e(label)}</a> — <bdi dir="ltr">{e(x["name"])}</bdi>{"،" if lang == "ar" else ","} {L("mb", n=x["mb"])}<span class="s" dir="ltr">SHA-256 {x["sha"]}</span></li>'
    win = lambda p, ks: ''.join(f(k, L(n)) for k, n in ks)
    linux = ''.join(f'<li>{e(n)}<pre dir="ltr">{e(cmd)}</pre></li>' for _, n, _, cmd, _, _ in LINUX)
    langs = ' · '.join(f'<a href="{root}{"" if l == "en" else l + "/"}lite.html" hreflang="{I.META[l]["html"]}" lang="{I.META[l]["html"]}">{e(I.META[l]["name"])}</a>' for l in I.LANGS)
    return f'''<!DOCTYPE html>
<html lang="{m['html']}" dir="{m['dir']}">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{e(L('title'))}</title>
<link rel="canonical" href="{base}index.html">
<style>{CSS}</style>
</head>
<body>
<div class="w">
<p class="n">{e(L('note'))} <a href="{base}index.html?full=1"><b>{e(L('full'))}</b></a></p>
<h1>VLC media player</h1>
<p>{e(L('lead'))}</p>
<p><a class="b" href="{F['win64']['url']}">{e(L('dl', v=V))} — Windows</a></p>
<p>{e(L('free'))} {e(L('verify'))}</p>
<h2 id="windows">Windows</h2>
<h3>{e(L('w64'))}</h3><ul>{win(0, [('win64', 'inst'), ('win64m', 'msi'), ('win64z', 'zip'), ('win647', '7z')])}</ul>
<h3>{e(L('w32'))}</h3><ul>{win(0, [('win32', 'inst'), ('win32m', 'msi'), ('win32z', 'zip'), ('win327', '7z')])}</ul>
<h3>{e(L('warm'))}</h3><ul>{win(0, [('arm64', 'inst'), ('arm64m', 'msi'), ('arm64z', 'zip')])}</ul>
<p><a href="{STORE['ms']}">Microsoft Store</a></p>
<h2 id="macos">{e(L('mac'))}</h2><ul>{win(0, [('macu', 'uni'), ('maca', 'as'), ('maci', 'intel')])}</ul>
<h2 id="linux">{e(L('linux'))}</h2><p>{e(L('linux_p'))}</p><ul>{linux}</ul>
<p><a href="{STORE['flathub']}">Flathub</a> · <a href="{STORE['snap']}">Snap Store</a></p>
<h2 id="mobile">{e(L('mobile'))}</h2>
<ul><li>Android, Android TV, Chromebook: <a href="{STORE['play']}">Google Play</a> · <a href="{STORE['fdroid']}">F-Droid</a> · <a href="{STORE['apk']}">APK</a></li>
<li>iPhone, iPad, Apple TV: <a href="{STORE['ios']}">App Store</a></li></ul>
<h2 id="source">{e(L('src'))}</h2><ul>{f('src', 'tar.xz')}<li><a href="https://code.videolan.org/videolan/vlc">code.videolan.org/videolan/vlc</a></li></ul>
<h2>{e(L('more'))}</h2>
<ul><li><a href="https://download.videolan.org/pub/videolan/vlc/">{e(L('older'))}</a></li>
<li><a href="https://www.videolan.org/contribute.html">{e(L('donate'))}</a></li>
<li><a href="https://forum.videolan.org/">{e(L('help'))}</a></li>
<li><a href="https://www.videolan.org/news.html">{e(L('news'))}</a></li>
<li><a href="https://www.videolan.org/videolan/">{e(L('about'))}</a></li></ul>
<p><b>{e(L('lang'))}:</b> {langs}</p>
<p class="f">{e(L('np'))}</p>
</div>
</body>
</html>'''
