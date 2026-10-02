#!/usr/bin/env python3
"""Build the single VideoLAN redesign (formerly option A) into dist/.
   EN at dist/, FR/ZH/AR at dist/{fr,zh,ar}/. Content pages under p/."""
import json, re, shutil, pathlib, sys, html as H
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import vlsite as S
import i18n as I
import curated as CU
from vlsite import e

ROOT = S.ROOT
SITE = ROOT / 'site'
DIST = ROOT / 'dist'
V, CODE = S.VERSION, S.CODENAME
REL_DATE = '2026-09-22'

# ------------------------------------------------------------------ extra strings
X = {
 'x_file': ('File', 'Fichier', '文件', 'الملف'),
 'x_size': ('Size', 'Taille', '大小', 'الحجم'),
 'x_from': ('From', 'Depuis', '来源', 'المصدر'),
 'dl_p': ('Free, signed and never bundled with anything else. We’ve picked your platform; switch below if you need another one.',
          'Gratuit, signé et jamais accompagné d’autre chose. Nous avons deviné votre plateforme ; changez-la ci-dessous si besoin.',
          '免费、已签名，绝不捆绑任何其他软件。我们已为你识别平台，如需其他版本可在下方切换。',
          'مجاني وموقّع ولا يُرفق بأي برنامج آخر. لقد خمّنّا منصّتك، ويمكنك تغييرها أدناه عند الحاجة.'),
 'dl_linux_h': ('Install from your distribution', 'Installer depuis votre distribution', '从发行版安装', 'ثبّت من توزيعتك'),
 'dl_universal_pkgs': ('Universal packages', 'Paquets universels', '通用软件包', 'حزم عامة'),
 'dl_src_d': ('Build VLC yourself, on any system.', 'Compilez VLC vous-même, sur n’importe quel système.', '在任何系统上自行编译 VLC。', 'ابنِ VLC بنفسك على أي نظام.'),
 'dl_ios_h': ('iPhone, iPad and Apple TV', 'iPhone, iPad et Apple TV', 'iPhone、iPad 和 Apple TV', 'iPhone وiPad وApple TV'),
 'dl_get_on': ('Get it on', 'Disponible sur', '获取于', 'احصل عليه من'),
 'dl_download_on': ('Download on the', 'Télécharger dans l’', '下载于', 'نزّله من'),
 'dl_all_opts': ('All {os} options', 'Toutes les options {os}', '{os} 全部选项', 'كل خيارات {os}'),
 'dl_legacy': ('Older and legacy builds', 'Versions anciennes et historiques', '旧版与历史版本', 'إصدارات قديمة'),
 'dl_cmd': ('Terminal', 'Terminal', '终端', 'الطرفية'),
 'dl_verify_cmd': ('Check a file', 'Vérifier un fichier', '校验文件', 'تحقّق من ملف'),
 'news_more': ('Read more', 'Lire la suite', '阅读全文', 'اقرأ المزيد'),
 'eco_more': ('Learn more', 'En savoir plus', '了解更多', 'اعرف المزيد'),
 'js_n': ('Normal', 'Normale', '标准', 'عادي'),
 'js_l': ('Large', 'Grande', '大', 'كبير'),
 'js_xl': ('Extra large', 'Très grande', '特大', 'كبير جدًا'),
 'd_cta_pp': ('Continue to PayPal · {a}', 'Continuer vers PayPal · {a}', '前往 PayPal · {a}', 'المتابعة إلى PayPal · {a}'),
 'd_opening_pp': ('Opening PayPal…', 'Ouverture de PayPal…', '正在打开 PayPal…', 'جارٍ فتح PayPal…'),
 'd_sepa_cta': ('Continue with SEPA · {a}', 'Continuer en SEPA · {a}', '使用 SEPA 继续 · {a}', 'المتابعة عبر SEPA · {a}'),
 'd_wallet_note': ('Apple Pay and Google Pay open on Stripe’s secure checkout on supported devices.', 'Apple Pay et Google Pay s’ouvrent sur la page sécurisée de Stripe, sur les appareils compatibles.', '在支持的设备上，Apple Pay 和 Google Pay 会在 Stripe 安全结账页面中打开。', 'يفتح Apple Pay وGoogle Pay في صفحة الدفع الآمنة لدى Stripe على الأجهزة المدعومة.'),
 'd_country': ('France', 'France', '法国', 'فرنسا'),
 'mk_alt': ('VLC playing {film} on {os}', 'VLC lisant {film} sous {os}', 'VLC 正在 {os} 上播放《{film}》', 'VLC يشغّل {film} على {os}'),
 'mk_continue': ('Continue watching', 'Reprendre la lecture', '继续观看', 'تابع المشاهدة'),
 'mk_left': ('{n} min left', '{n} min restantes', '剩余 {n} 分钟', 'متبقٍ {n} د'),
 'mk_lan': ('Local network', 'Réseau local', '本地网络', 'الشبكة المحلية'),
 'mk_lan_p': ('Living-room NAS · 4 shared folders · SMB', 'NAS du salon · 4 dossiers partagés · SMB', '客厅 NAS · 4 个共享文件夹 · SMB', 'NAS غرفة المعيشة · 4 مجلدات مشتركة · SMB'),
 'mk_new': ('NEW', 'NEUF', '新', 'جديد'),
 'mk_videos': ('Videos', 'Vidéos', '视频', 'الفيديو'),
 'mk_audio': ('Audio', 'Audio', '音频', 'الصوت'),
 'mk_browse': ('Browse', 'Parcourir', '浏览', 'تصفّح'),
 'mk_playlists': ('Playlists', 'Listes', '播放列表', 'القوائم'),
 'mk_more': ('More', 'Plus', '更多', 'المزيد'),
 'mk_all': ('All', 'Tout', '全部', 'الكل'),
 'mk_movies': ('Movies', 'Films', '电影', 'أفلام'),
 'mk_shorts': ('Shorts', 'Courts', '短片', 'قصيرة'),
 'mk_menu': ('Media|Playback|Audio|Video|Subtitle|Tools|View|Help', 'Média|Lecture|Audio|Vidéo|Sous-titres|Outils|Vue|Aide', '媒体|播放|音频|视频|字幕|工具|视图|帮助', 'وسائط|تشغيل|صوت|فيديو|ترجمة|أدوات|عرض|مساعدة'),
 'mk_speed': ('Speed 1.25×', 'Vitesse 1,25×', '速度 1.25×', 'السرعة 1.25×'),
 'mk_sub_track': ('Subtitle track: {l}', 'Piste de sous-titres : {l}', '字幕轨道：{l}', 'مسار الترجمة: {l}'),
 'proposal_short': ('Redesign proposal', 'Proposition de refonte', '改版提案', 'مقترح إعادة التصميم'),
 'p_hub': ('Section', 'Rubrique', '栏目', 'القسم'),
 'p_source': ('Original page', 'Page d’origine', '原始页面', 'الصفحة الأصلية'),
 'p_pages': ('{n} pages', '{n} pages', '{n} 个页面', '{n} صفحة'),
 'p_items': ('{n} items', '{n} articles', '{n} 条', '{n} عنصرًا'),
 'sitemap_lede': ('Every page of videolan.org carried over into this proposal: {n} pages, plus new hubs.', 'Toutes les pages de videolan.org reprises dans cette proposition : {n} pages, plus de nouvelles rubriques.', '本提案收录了 videolan.org 的全部页面：共 {n} 个，另有新的栏目页。', 'كل صفحات videolan.org منقولة إلى هذا المقترح: {n} صفحة، مع صفحات أقسام جديدة.'),
 'about_board': ('Board', 'Bureau', '理事会', 'مجلس الإدارة'),
 'stat_langs': ('languages in VLC', 'langues dans VLC', '种 VLC 界面语言', 'لغة في VLC'),
 'hero_badge': ('New', 'Nouveau', '新版', 'جديد'),
 'tl_title': ('Since 1996', 'Depuis 1996', '始于 1996', 'منذ 1996'),
 'qr_scan': ('Scan with your phone', 'Scannez avec votre téléphone', '用手机扫码', 'امسح الرمز بهاتفك'),
 'qr_p': ('Point your phone’s camera at the code to open the store directly.', 'Visez le code avec l’appareil photo de votre téléphone pour ouvrir directement la boutique.', '用手机相机对准二维码，即可直接打开应用商店。', 'وجّه كاميرا هاتفك نحو الرمز لفتح المتجر مباشرة.'),
 'qr_or': ('Or open it here', 'Ou ouvrez-la ici', '或在此打开', 'أو افتحه هنا'),
 'set_title': ('Settings', 'Réglages', '设置', 'الإعدادات'),
 'set_sub': ('Search, language, appearance and accessibility, all in one place.', 'Recherche, langue, apparence et accessibilité, au même endroit.', '搜索、语言、外观与无障碍，集中在一处。', 'البحث واللغة والمظهر وسهولة الوصول في مكان واحد.'),
 'set_search': ('Search', 'Recherche', '搜索', 'البحث'),
 'set_lang': ('Language', 'Langue', '语言', 'اللغة'),
 'set_look': ('Appearance', 'Apparence', '外观', 'المظهر'),
 'set_a11y': ('Accessibility', 'Accessibilité', '无障碍', 'سهولة الوصول'),
 'set_keys': ('Shortcuts', 'Raccourcis', '快捷键', 'الاختصارات'),
 'set_popular': ('Popular pages', 'Pages populaires', '热门页面', 'صفحات شائعة'),
 'set_k1': ('Open search', 'Ouvrir la recherche', '打开搜索', 'افتح البحث'),
 'set_k2': ('Close any window', 'Fermer une fenêtre', '关闭任意窗口', 'أغلق أي نافذة'),
 'set_k3': ('Move through results', 'Parcourir les résultats', '在结果中移动', 'تنقّل بين النتائج'),
 'set_k4': ('Open the selected result', 'Ouvrir le résultat choisi', '打开所选结果', 'افتح النتيجة المحددة'),
 'set_k5': ('Skip to the content', 'Aller au contenu', '跳到正文', 'انتقل إلى المحتوى'),
 'set_preview': ('Preview', 'Aperçu', '预览', 'معاينة'),
 'set_reset': ('Reset all settings', 'Réinitialiser les réglages', '恢复默认设置', 'إعادة ضبط الإعدادات'),
 'set_saved': ('Saved on this device only. No cookies.', 'Enregistré sur cet appareil uniquement. Sans cookie.', '仅保存在本设备，不使用 Cookie。', 'يُحفظ على هذا الجهاز فقط، دون ملفات تعريف.'),
 'set_results': ('{n} results', '{n} résultats', '{n} 个结果', '{n} نتيجة'),
 'hp_dl_h': ('Get VLC for your device', 'VLC pour votre appareil', '为你的设备获取 VLC', 'احصل على VLC لجهازك'),
 'hp_dl_all': ('Open the download centre', 'Ouvrir le centre de téléchargement', '打开下载中心', 'افتح مركز التنزيل'),
 'ft_simple': ('Simple version', 'Version simple', '简易版', 'النسخة المبسّطة'),
 'dlm_q': ('What do you need?', 'Que cherchez-vous ?', '你需要什么？', 'ما الذي تحتاجه؟'),
 'i_install': ('Install on this device', 'Installer sur cet appareil', '安装到本设备', 'التثبيت على هذا الجهاز'),
 'i_portable': ('Portable, no install', 'Portable, sans installation', '便携版，免安装', 'نسخة محمولة بلا تثبيت'),
 'i_store': ('From an app store', 'Depuis une boutique', '从应用商店获取', 'من متجر تطبيقات'),
 'i_cli': ('Command line', 'En ligne de commande', '命令行安装', 'عبر سطر الأوامر'),
 'i_older': ('Older versions', 'Anciennes versions', '旧版本', 'الإصدارات القديمة'),
 'i_src': ('Source code', 'Code source', '源代码', 'الشيفرة المصدرية'),
 'dlm_h': ('Choose your download', 'Choisissez votre téléchargement', '选择要下载的版本', 'اختر ما تريد تنزيله'),
 'dlm_p': ('Every system, every format: installers, archives, app stores, packages and source code.', 'Tous les systèmes, tous les formats : installateurs, archives, boutiques, paquets et code source.', '覆盖所有系统与格式：安装程序、压缩包、应用商店、软件包和源代码。', 'كل الأنظمة وكل الصيغ: برامج التثبيت والأرشيفات والمتاجر والحزم والشيفرة المصدرية.'),
 'dl_tab_hint': ('Choose a platform', 'Choisir une plateforme', '选择平台', 'اختر منصة'),
}
I.T.update(X)
t, sec = I.t, I.sec

# ------------------------------------------------------------------ download data
GV = f'https://get.videolan.org/vlc/{V}'
F = {
 'win64':   dict(url=f'{GV}/win64/vlc-{V}-win64.exe', size=46269360, sha='d711e1e1fe52052748c39080c7dce63f6b7e4c315efedf1774a3f1957b782ff3'),
 'win64m':  dict(url=f'{GV}/win64/vlc-{V}-win64.msi', size=63389696, sha='22172095ce4c2d5f5b600bb4c142d78105db29a77fa59a931941876f3b20f6d0'),
 'win64z':  dict(url=f'{GV}/win64/vlc-{V}-win64.zip', size=82765861, sha='fcf30850371ad10c9373cc4f0f4501e7dee49e3e9ae9f20c72fb2661a1ca6323'),
 'win647':  dict(url=f'{GV}/win64/vlc-{V}-win64.7z', size=39384682, sha='1ed59c09152e78aff84663fa76efab26057716576db74332858810e5ef54ae1f'),
 'arm64':   dict(url=f'{GV}/winarm64/vlc-{V}-winarm64.exe', size=40658224, sha='1377f8a7aa8094cf73bc5a36428a652f3da41017fe16a522e0f7941723000bfb'),
 'arm64m':  dict(url=f'{GV}/winarm64/vlc-{V}-winarm64.msi', size=57282560, sha='a9f5268006d51cf593a8d20edac3cc70aa65fd87ac37fa0a62c7509531996aee'),
 'arm64z':  dict(url=f'{GV}/winarm64/vlc-{V}-winarm64.zip', size=76738526, sha='f096226211f67f8e06e50cd0d6a948d842db128ff22a676dc1ca1cc6114baba5'),
 'win32':   dict(url=f'{GV}/win32/vlc-{V}-win32.exe', size=45183808, sha='39928615829553bf71810119ea6ecd20cd2fa568e7ec5dfe2e48fd30819cf77a'),
 'win32m':  dict(url=f'{GV}/win32/vlc-{V}-win32.msi', size=61956096, sha='6a55111e19cfd4b25390fed2744eedd6f6c32d3d5bce68ec4b3c2f0f47951eb0'),
 'win32z':  dict(url=f'{GV}/win32/vlc-{V}-win32.zip', size=81365541, sha='8511356afd680817f3aea624c63032d0936f3d77b2175fb36c8fc16adf9744e8'),
 'win327':  dict(url=f'{GV}/win32/vlc-{V}-win32.7z', size=38188211, sha='80b61c03a5c7c4d4b44a79a2db34eda244ad6b09f1e0f44fcf6183f4c10e9966'),
 'macu':    dict(url=f'{GV}/macosx/vlc-{V}-universal.dmg', size=99312422, sha='2c8e89f7f42e53c2fb0e87b6dfa39b49f1364b25080aaa2e476ac74c0d7beb3c'),
 'maca':    dict(url=f'{GV}/macosx/vlc-{V}-arm64.dmg', size=56960605, sha='64a89d93cdd30b0e97131743e246373db82d6826ea882d265d46d74b136da2b7'),
 'maci':    dict(url=f'{GV}/macosx/vlc-{V}-intel64.dmg', size=63465193, sha='1ef6c903e2dc026d4e58ddf7b2a9ed0eb6f8caf80a9a9f46f96490340b962707'),
 'src':     dict(url=f'{GV}/vlc-{V}.tar.xz', size=27620304, sha='e7cab503d1d7d5849b89d2cf0e1ee60d0ef6d012407791b644b9cfc0cc225fdf'),
}
for k, f in F.items(): f['name'] = f['url'].rsplit('/', 1)[1]; f['mb'] = round(f['size'] / 1048576)
BY_URL = {f['url']: f for f in F.values()}
STORE = dict(
 ms='https://apps.microsoft.com/detail/9NBLGGH4VVNH', play='https://play.google.com/store/apps/details?id=org.videolan.vlc',
 fdroid='https://f-droid.org/en/packages/org.videolan.vlc/', apk='https://get.videolan.org/vlc-android/3.7.0/',
 ios='https://apps.apple.com/app/apple-store/id650377962', flathub='https://flathub.org/apps/org.videolan.VLC', snap='https://snapcraft.io/vlc')
LINUX = [
 ('ubuntu', 'Ubuntu', 'apt', 'sudo apt install vlc', 'vlc--download-ubuntu', ''),
 ('debian', 'Debian', 'apt', 'sudo apt install vlc', 'vlc--download-debian', ''),
 ('fedora', 'Fedora', 'dnf', 'sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm\nsudo dnf install vlc', 'vlc--download-fedora', 'dl_rpmfusion'),
 ('arch', 'Arch Linux', 'pacman', 'sudo pacman -S vlc', 'vlc--download-archlinux', ''),
 ('suse', 'openSUSE', 'zypper', 'sudo zypper install vlc', 'vlc--download-suse', ''),
 ('gentoo', 'Gentoo', 'emerge', 'sudo emerge --ask media-video/vlc', 'vlc--download-gentoo', ''),
 ('flatpak', 'Flatpak', 'flatpak', 'flatpak install flathub org.videolan.VLC', '', ''),
 ('snap', 'Snap', 'snap', 'sudo snap install vlc', '', ''),
]

FILMS = dict(bbb='Big Buck Bunny', sintel='Sintel', sintel2='Sintel', llama='Caminandes', tos='Tears of Steel', robot='Tears of Steel', ed='Elephants Dream')
SUBS = {  # in-film subtitle lines (the "subtitle demo")
 'en': ['What a beautiful morning in the meadow.', 'I’ve been looking for you.', 'We have to go back.'],
 'fr': ['Quelle belle matinée dans la prairie.', 'Je t’ai cherché partout.', 'Il faut qu’on y retourne.'],
 'zh': ['草地上的早晨真美啊。', '我一直在找你。', '我们得回去了。'],
 'ar': ['يا له من صباح جميل في المرج.', 'كنت أبحث عنك.', 'علينا أن نعود.'],
}

# ------------------------------------------------------------------ context
class Ctx:
    def __init__(s, lang, depth_in_lang):  # depth_in_lang: 0 home, 1 in p/
        s.lang = lang
        s.base = '../' * depth_in_lang                       # to language root
        s.root = s.base + ('' if lang == 'en' else '../')    # to dist root
        s.home = depth_in_lang == 0
    def ico(s, n, cls='ic'): return f'<svg class="{cls}" aria-hidden="true"><use href="{s.root}icons.svg#i-{n}"/></svg>'
    def page(s, slug, anchor=''):
        if slug == 'home': return s.base + 'index.html' + anchor
        return s.base + 'p/' + slug + '.html' + anchor
    def t(s, k, **kw): return t(s.lang, k, **kw)
    def link(s, url):
        r = S.resolve(url)
        return s.page(r[0], r[1]) if r else url

def dlattrs(f): return f' data-dl data-sha="{f["sha"]}" data-size="{f["size"]}"'

def pic(c, name, alt, sizes='(max-width: 900px) 72vw, 640px', eager=False, big=True):
    ld = 'eager" fetchpriority="high' if eager else 'lazy'
    ss = f'{c.root}media/{name}-640.webp 640w' + (f', {c.root}media/{name}-1280.webp 1280w' if big else '')
    return (f'<picture><source type="image/webp" srcset="{ss}" sizes="{sizes}">'
            f'<img src="{c.root}media/{name}-640.jpg" width="640" height="334" alt="{e(alt)}" loading="{ld}" decoding="async"></picture>')

def mmss(sec_): return f'{sec_ // 60:02d}:{sec_ % 60:02d}'
def hmmss(sec_): return f'{sec_ // 3600}:{(sec_ % 3600) // 60:02d}:{sec_ % 60:02d}'

# ------------------------------------------------------------------ mockups
def mk_win(c, img, ext='mkv', p=34, dur=596, sub=0, eager=False, cls=''):
    menu = c.t('mk_menu').split('|')
    film = FILMS[img]
    cur = int(dur * p / 100)
    return f'''<figure class="mk mk-win {cls}" data-play data-dur="{dur}" data-p="{p}" role="img" aria-label="{e(c.t('mk_alt', film=film, os='Windows 11'))}">
<div class="w-tb"><svg class="cone" viewBox="0 0 64 64" aria-hidden="true"><use href="{c.root}icons.svg#i-cone"/></svg><span class="t">{e(film)}.{ext} - VLC media player</span><i>{c.ico('minus','')}</i><i>{c.ico('square','')}</i><i>{c.ico('x','')}</i></div>
<div class="w-mb" aria-hidden="true">{''.join(f'<span>{e(m)}</span>' for m in menu)}</div>
<div class="fr">{pic(c, img, '', eager=eager)}<p class="sub" aria-hidden="true" data-subs="{e('|'.join(SUBS[c.lang]))}" lang="{I.META[c.lang]['html']}" dir="{I.META[c.lang]['dir']}">{e(SUBS[c.lang][sub])}</p><p class="osd" aria-hidden="true"></p></div>
<div class="w-cb" aria-hidden="true"><div class="w-seek"><span class="tc">{mmss(cur)}</span><div class="bar" style="--p:{p}%"><b></b></div><span>{mmss(dur)}</span></div>
<div class="w-btns"><i class="pl">{c.ico('pause','')}</i><span class="gap"></span><i>{c.ico('prev','')}</i><i>{c.ico('stop','')}</i><i>{c.ico('next','')}</i><span class="gap"></span><i>{c.ico('full','')}</i><i>{c.ico('sliders','')}</i><i>{c.ico('playlist','')}</i><i>{c.ico('loop','')}</i><i>{c.ico('shuffle','')}</i>
<span class="w-vol">{c.ico('volume','')}<span class="wedge"></span><span>74%</span></span></div></div></figure>'''

def mk_mac(c, img, p=58, dur=888, cls=''):
    film = FILMS[img]; cur = int(dur * p / 100)
    return f'''<figure class="mk mk-mac {cls}" data-play data-dur="{dur}" data-p="{p}" role="img" aria-label="{e(c.t('mk_alt', film=film, os='macOS'))}">
<div class="fr">{pic(c, img, '')}<div class="m-tb" aria-hidden="true"><span class="tl"><i></i><i></i><i></i></span>{e(film)}.mp4</div>
<p class="sub" aria-hidden="true" data-subs="{e('|'.join(SUBS[c.lang][1:] + SUBS[c.lang][:1]))}" lang="{I.META[c.lang]['html']}" dir="{I.META[c.lang]['dir']}">{e(SUBS[c.lang][1])}</p>
<div class="hud" aria-hidden="true"><div class="hud-r"><span class="side l">{c.ico('volume','')}</span>{c.ico('prev','')}<span class="pl">{c.ico('pause','')}</span>{c.ico('next','')}<span class="side r">{c.ico('cc','')}{c.ico('playlist','')}{c.ico('full','')}</span></div>
<div class="hud-s"><span class="tc">{mmss(cur)}</span><div class="bar" style="--p:{p}%"><b></b></div><span>-{mmss(dur - cur)}</span></div></div></div></figure>'''

def mk_gnome(c, img, p=22, dur=734, cls=''):
    film = FILMS[img]; cur = int(dur * p / 100); menu = c.t('mk_menu').split('|')
    return f'''<figure class="mk mk-gnome {cls}" data-play data-dur="{dur}" data-p="{p}" role="img" aria-label="{e(c.t('mk_alt', film=film, os='Linux'))}">
<div class="g-tb" aria-hidden="true">{e(film)}.webm — VLC media player<span class="gx"><i>{c.ico('minus','')}</i><i>{c.ico('square','')}</i><i>{c.ico('x','')}</i></span></div>
<div class="w-mb" aria-hidden="true">{''.join(f'<span>{e(m)}</span>' for m in menu)}</div>
<div class="fr">{pic(c, img, '')}<p class="osd" aria-hidden="true"></p></div>
<div class="w-cb" aria-hidden="true"><div class="w-seek"><span class="tc">{mmss(cur)}</span><div class="bar" style="--p:{p}%"><b></b></div><span>{mmss(dur)}</span></div>
<div class="w-btns"><i class="pl">{c.ico('pause','')}</i><span class="gap"></span><i>{c.ico('prev','')}</i><i>{c.ico('stop','')}</i><i>{c.ico('next','')}</i><span class="gap"></span><i>{c.ico('full','')}</i><i>{c.ico('sliders','')}</i><i>{c.ico('playlist','')}</i>
<span class="w-vol">{c.ico('volume','')}<span class="wedge"></span><span>100%</span></span></div></div></figure>'''

def mk_android(c, cls=''):
    tiles = [('bbb', 'Big Buck Bunny', '9:56', 62, True), ('sintel', 'Sintel', '14:48', 0, False), ('tos', 'Tears of Steel', '12:14', 30, False), ('llama', 'Caminandes', '2:26', 0, True), ('ed', 'Elephants Dream', '10:54', 0, False), ('robot', 'Tears of Steel — Robot', '12:14', 0, False)]
    NEWTAG = "<em>" + e(c.t("mk_new")) + "</em>"
    grid = ''.join(f'<div><div class="th"><img src="{c.root}media/{n}-640.jpg" alt="" loading="lazy" decoding="async" width="640" height="334">{f"<span class=pg style=width:{pg}%></span>" if pg else ""}</div>{NEWTAG if new else ""}<b>{e(tt)}</b><small>{d_}</small></div>' for n, tt, d_, pg, new in tiles)
    nav = [('film', 'mk_videos', True), ('music', 'mk_audio', False), ('folder', 'mk_browse', False), ('plist', 'mk_playlists', False), ('dots', 'mk_more', False)]
    navh = ''.join(f'<span{" class=on" if on else ""}>{c.ico(i,"")}{e(c.t(k))}</span>' for i, k, on in nav)
    return f'''<figure class="mk mk-phone {cls}" role="img" aria-label="{e(c.t('mk_alt', film='Big Buck Bunny', os='Android'))}"><div class="scr">
<div class="p-sb" aria-hidden="true"><span>9:41</span><span class="r">{c.ico('wifi','')}<i></i></span></div>
<div class="a-top" aria-hidden="true"><svg class="cone" viewBox="0 0 64 64"><use href="{c.root}icons.svg#i-cone"/></svg>{e(c.t('mk_videos'))}<span class="s">{c.ico('search','')}{c.ico('more','')}</span></div>
<div class="a-chips" aria-hidden="true"><span class="on">{e(c.t('mk_all'))}</span><span>{e(c.t('mk_movies'))}</span><span>{e(c.t('mk_shorts'))}</span></div>
<div class="a-grid" aria-hidden="true">{grid}</div>
<div class="a-mini" aria-hidden="true"><div class="th"><img src="{c.root}media/bbb-640.jpg" alt="" loading="lazy" width="640" height="334"></div><div><b>Big Buck Bunny</b><small>{e(c.t('mk_left', n=4))}</small></div>{c.ico('pause','')}</div>
<div class="a-nav" aria-hidden="true">{navh}</div></div></figure>'''

def mk_iphone(c, img='sintel2', p=41, dur=888, cls=''):
    cur = int(dur * p / 100)
    return f'''<figure class="mk mk-iph {cls}" data-play data-dur="{dur}" data-p="{p}" role="img" aria-label="{e(c.t('mk_alt', film=FILMS[img], os='iPhone'))}"><div class="scr"><span class="isl"></span>
<div class="fr">{pic(c, img, '')}</div>
<div class="i-ov" aria-hidden="true"><div class="i-top">{c.ico('x','')}<span>{e(FILMS[img])}</span><span class="r">{c.ico('airplay','')}{c.ico('cc','')}{c.ico('more','')}</span></div>
<p class="sub" aria-hidden="true" style="bottom:30%" lang="{I.META[c.lang]['html']}" dir="{I.META[c.lang]['dir']}" data-subs="{e('|'.join(SUBS[c.lang][2:] + SUBS[c.lang][:2]))}">{e(SUBS[c.lang][2])}</p>
<div class="i-bot"><div class="bar" style="--p:{p}%"><b></b></div><div class="i-tm"><span class="tc">{mmss(cur)}</span><span>-{mmss(dur - cur)}</span></div>
<div class="i-ctl"><span class="side l">{c.ico('lockscreen','')}{c.ico('aspect','')}</span>{c.ico('prev','')}<span class="pl">{c.ico('pause','')}</span>{c.ico('next','')}<span class="side r">{c.ico('gauge','')}{c.ico('playlist','')}</span></div></div></div></div></figure>'''

def mk_tv(c, cls=''):
    row = ['ed', 'bbb', 'tos', 'sintel', 'llama']
    return f'''<figure class="mk mk-tv {cls}" role="img" aria-label="{e(c.t('mk_alt', film='Tears of Steel', os='Apple TV'))}"><div class="scr"><div class="fr" style="position:absolute;inset:0">{pic(c, 'tos', '')}</div>
<div class="tv-ui" aria-hidden="true"><h4 dir="{I.META[c.lang]['dir']}">{e(c.t('mk_lan'))}</h4><p dir="{I.META[c.lang]['dir']}">{e(c.t('mk_lan_p'))}</p><div class="tv-row" data-tvrow>{''.join(f'<div{" class=f" if i == 1 else ""}><img src="{c.root}media/{n}-640.jpg" alt="" loading="lazy" width="640" height="334"></div>' for i, n in enumerate(row))}</div></div></div><div class="stand"></div></figure>'''

# ------------------------------------------------------------------ shell
NAV = [('download', 'nav_download'), ('features', 'nav_features'), ('news', 'nav_news'), ('projects', 'nav_projects'), ('support', 'nav_support'), ('contribute', 'nav_contribute'), ('about', 'nav_about')]
def nav_href(c, k):
    return {'download': c.page('download'), 'features': c.page('vlc--features'), 'news': c.page('news'),
            'projects': c.page('projects'), 'support': c.page('support'), 'contribute': c.page('contribute'), 'about': c.page('videolan')}[k]
NAV_ICO = dict(download='download', features='sparkle', news='news', projects='box', support='chat', contribute='users', about='home')

SITE_URL = 'https://vlc.paulfleury.com/'

def lang_href(lang, slug, from_ctx):
    b = from_ctx.root + ('' if lang == 'en' else lang + '/')
    return b + ('index.html' if slug == 'home' else 'p/' + slug + '.html')

def head(c, title, desc, slug, cur=''):
    m = I.META[c.lang]
    def absu(l): return SITE_URL + ('' if l == 'en' else l + '/') + ('' if slug == 'home' else 'p/' + slug + '.html')
    alts = ''.join(f'<link rel="alternate" hreflang="{I.META[l]["html"]}" href="{absu(l)}">' for l in I.LANGS) + f'<link rel="alternate" hreflang="x-default" href="{absu("en")}"><link rel="canonical" href="{absu(c.lang)}">'
    return f'''<!doctype html>
<html lang="{m['html']}" dir="{m['dir']}" data-root="{c.root}" data-base="{c.base}" data-slug="{slug}" data-lang="{c.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!--[if IE]><meta http-equiv="refresh" content="0;url={c.base}lite.html"><![endif]-->
<script>(function(w,d){{var s,ok;try{{s=w.localStorage;if(/[?&]full=1/.test(w.location.search))s.setItem('vl-full','1');ok=s.getItem('vl-full')}}catch(e){{}}if(ok)return;var C=w.CSS,n=w.navigator.userAgent;if(!(d.querySelector&&w.addEventListener&&w.Promise&&C&&C.supports&&C.supports('--a','0')&&C.supports('display','grid')&&C.supports('position','sticky'))||/Trident[/]|MSIE |Opera Mini|Presto[/]|UCBrowser[/][0-9][.]|PlayStation|Nintendo|KaiOS|BlackBerry|BB10|Windows Phone|Symbian|Android [1-4][.]|CPU (iPhone )?OS ([1-9]|1[01])_|Firefox[/]([1-4]?[0-9]|5[0-1])[.]|Chrome[/]([1-4]?[0-9]|5[0-6])[.]/.test(n))w.location.replace('{c.base}lite.html')}})(window,document)</script>
<noscript><style>.rv{{opacity:1!important;transform:none!important}}</style></noscript>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#ff8800">
<link rel="icon" href="{c.root}favicon.svg" type="image/svg+xml">
{alts}
<script>(function(d,w){{var h=d.documentElement,s;try{{s=w.localStorage}}catch(e){{}}function g(k){{try{{return s&&s.getItem('vl-'+k)}}catch(e){{return null}}}}var t=g('theme')||'auto',dk=t==='dark'||(t==='auto'&&w.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);h.setAttribute('data-theme',dk?'dark':'light');['contrast','size','motion','links','spacing'].forEach(function(k){{var v=g(k);if(v)h.setAttribute('data-'+k,v)}});var rm=w.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;if(!rm&&g('motion')!=='off'&&w.CSS&&CSS.supports&&CSS.supports('inset','0')&&'IntersectionObserver' in w)h.className+=' fx';if(g('rib')==='off')h.className+=' rib-off';h.className+=' js'}})(document,window);</script>
<link rel="stylesheet" href="{c.root}site.css">
</head>
<body>
<a class="skip" href="#main">{e(c.t('skip'))}</a>
<div class="rib" id="rib" role="region" aria-label="{e(c.t('proposal_short'))}"><div class="wrap"><p><span class="l">{e(c.t('proposal_bar'))}</span><span class="s">{e(c.t('proposal_short'))} ·</span> <a href="{c.page('design-notes')}">{e(c.t('read_notes'))}</a></p><button type="button" class="rib-x" data-rib-close aria-label="{e(c.t('hide'))}" title="{e(c.t('hide'))}">{c.ico('x')}</button></div></div>
<header class="hd"><div class="wrap">
<a class="brand" href="{c.page('home')}" aria-label="VideoLAN VLC media player — {e(c.t('home'))}"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="{c.root}icons.svg#i-cone"/></svg><span><b>VideoLAN</b><small>VLC media player</small></span></a>
<nav class="nav" aria-label="{e(c.t('menu'))}">{''.join(f'<a href="{nav_href(c, k)}"' + (' aria-current="page"' if k == cur else '') + f'>{e(c.t(l))}</a>' for k, l in NAV)}</nav>
<div class="tools">
<button type="button" class="setb" data-open="settings" aria-keyshortcuts="Control+K /"><span class="setb-i">{c.ico('search')}{c.ico('globe')}{c.ico('sun')}{c.ico('a11y')}</span><span class="setb-l">{e(c.t('set_title'))}</span><span class="setb-c">{c.lang.upper()}</span><span class="sr"> — {e(c.t('set_sub'))}</span></button>
<a class="btn btn-gh btn-sm hide-md" href="{c.page('contribute')}" data-donate>{c.ico('heart', 'ic heart')}{e(c.t('donate'))}</a>
<details class="menu"><summary class="ib" aria-label="{e(c.t('menu'))}">{c.ico('menu')}</summary><div class="drawer">{''.join(f'<a href="{nav_href(c, k)}">{c.ico(NAV_ICO[k])}{e(c.t(l))}</a>' for k, l in NAV)}<a href="{c.page('contribute')}" data-donate>{c.ico('heart', 'ic heart')}{e(c.t('donate'))}</a></div></details>
</div></div></header>
<main id="main" tabindex="-1">'''

def foot(c):
    cols = [
      ('ft_vlc', [('nav_download', c.page('download')), ('nav_features', c.page('vlc--features')), ('ft_skins', c.page('vlc--skins.php')), ('ft_ext', 'https://addons.videolan.org/'), ('dl_notes', c.page('vlc--releases--3.0.24')), ('ft_security', c.page('security'))]),
      ('ft_projects', [('eco_all', c.page('section--projects')), (None, 'libVLC', c.page('vlc--libvlc')), (None, 'dav1d', c.page('projects--dav1d')), (None, 'x264', c.page('developers--x264')), (None, 'DVBlast', c.page('projects--dvblast')), ('ft_gitlab', 'https://code.videolan.org/')]),
      ('ft_community', [('ft_forums', 'https://forum.videolan.org/'), ('ft_wiki', 'https://wiki.videolan.org/'), ('ft_faq', c.page('support--faq')), ('ft_docs', 'https://docs.videolan.me/vlc-user/'), ('nav_contribute', c.page('contribute')), ('ft_events', c.page('videolan--events'))]),
      ('ft_org', [('nav_about', c.page('videolan')), ('team', c.page('videolan--team')), ('partners', c.page('videolan--partners')), ('ft_press', c.page('press')), ('ft_legal', c.page('legal')), ('ft_privacy', c.page('privacy')), ('ft_contact', c.page('contact'))]),
    ]
    def li(x):
        if x[0] is None: return f'<li><a href="{x[2]}">{e(x[1])}</a></li>'
        return f'<li><a href="{x[1]}">{e(c.t(x[0]))}</a></li>'
    langs = ''.join(f'<a href="{lang_href(l, c.slug, c)}" hreflang="{I.META[l]["html"]}" lang="{I.META[l]["html"]}"' + (' aria-current="true"' if l == c.lang else '') + f'>{e(I.META[l]["name"])}</a>' for l in I.LANGS)
    return f'''</main>
<footer class="ft"><div class="wrap"><div class="ft-g">
<div class="ft-a"><a class="brand" href="{c.page('home')}"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="{c.root}icons.svg#i-cone"/></svg><span><b>VideoLAN</b><small>VLC media player</small></span></a>
<p>{e(c.t('ft_about'))}</p><div class="langs">{langs}<button type="button" data-open="lang">+77</button></div></div>
{''.join(f'<div><h2 class="fh">{e(c.t(h))}</h2><ul>{"".join(li(x) for x in items)}</ul></div>' for h, items in cols)}
</div>
<div class="ft-b"><p>{e(c.t('ft_tm'))} {e(c.t('ft_films'))}</p><p><a href="{c.page('sitemap')}">{e(c.t('site_index'))}</a> · <a href="{c.page('design-notes')}">{e(c.t('design_notes'))}</a> · <a href="{c.base}lite.html">{e(c.t('ft_simple'))}</a> · {e(c.t('ft_light'))}</p></div>
</div></footer>
<script src="{c.base}l10n.js" defer></script>
<script src="{c.root}site.js" defer></script>
</body></html>'''

# ------------------------------------------------------------------ download component
def file_row(c, f, title, desc, ico, tag=''):
    return f'''<div class="pf"><div class="fi">{f['name'].rsplit('.', 1)[1]}</div>
<div class="nm"><b>{e(title)}{f'<span class="tag">{e(tag)}</span>' if tag else ''}</b><span>{e(f['name'])} · {e(c.t('mb', n=f['mb']))}</span></div>
<a class="btn btn-or" href="{f['url']}"{dlattrs(f)}>{c.ico('download')}{e(c.t('cta_download'))}</a>
<div class="sha"><code title="SHA-256">SHA-256 {f['sha']}</code><button type="button" class="cp" data-copy="{f['sha']}">{c.ico('copy')}{e(c.t('dl_copy'))}</button></div></div>'''

def alt_row(c, f, title, desc):
    return f'<a class="alt" href="{f["url"]}"{dlattrs(f)}><span><b>{e(title)}</b><small>{e(desc)}</small></span><span class="sz">{e(c.t("mb", n=f["mb"]))}</span>{c.ico("download")}</a>'

def link_row(c, href, title, desc, ico='arrow'):
    return f'<a class="alt" href="{href}"><span><b>{e(title)}</b><small>{e(desc)}</small></span><span></span>{c.ico(ico, "ic flip" if ico == "arrow" else "ic")}</a>'

def badge(c, href, ico, small, big):
    return f'<a class="sbadge" href="{href}">{c.ico(ico)}<span><small>{e(small)}</small><b>{e(big)}</b></span></a>'

def qrs(c, items):
    cards = ''.join(f'<a class="qr-c" href="{STORE[k]}"><img src="{c.root}media/qr-{k}.svg" width="132" height="132" alt="QR — {e(n)}" loading="lazy"><b>{e(n)}</b></a>' for k, n in items)
    return f'<div class="qrs"><div class="qr-t">{c.ico("phone")}<div><b>{e(c.t("qr_scan"))}</b><p>{e(c.t("qr_p"))}</p></div></div><div class="qr-g">{cards}</div></div>'

def term(c, cmd, note='', label=None):
    lines = '\n'.join(f'<span class="p">$ </span>{e(x)}' for x in cmd.split('\n'))
    return f'<div class="term"><div class="tt"><i></i><i></i><i></i><span>{e(label or c.t("dl_cmd"))}</span><button type="button" class="cp" data-copy="{e(cmd)}">{c.ico("copy")}{e(c.t("dl_copy"))}</button></div><pre><code>{lines}</code></pre>{f"<p class=note>{e(note)}</p>" if note else ""}</div>'

def download_block(c, hid='download'):
    tabs = [('windows', 'windows', 'os_windows', f'x64 · ARM64 · x86'), ('mac', 'apple', 'os_mac', 'Apple Silicon · Intel'), ('linux', 'linux', 'os_linux', 'apt · dnf · pacman · Flatpak'),
            ('android', 'android', 'os_android', 'Google Play · F-Droid · APK'), ('ios', 'phone', 'dl_ios_h', 'App Store'), ('source', 'code', 'os_source', 'tar.xz · git'), ('other', 'box', 'os_other', 'ChromeOS · FreeBSD · OS/2')]
    rail = ''.join(f'<button type="button" role="tab" id="tab-{k}" aria-controls="dp-{k}" aria-selected="{"true" if k == "windows" else "false"}" data-os="{k}">{c.ico(i)}<span><b>{e(c.t(l))}</b><small>{e(s)}</small></span><span class="det">{e(c.t("dl_detected"))}</span></button>' for k, i, l, s in tabs)
    hx = 'h3' if hid == 'dlm' else 'h2'
    def ph(k, ico, title, sub, extra=''):
        return f'<div class="dp-h"><span class="big">{c.ico(ico)}</span><div><{hx} class="dp-t">{e(title)}</{hx}><p>{e(sub)}</p></div>{extra}</div>'
    def meta(*items): return '<div class="dmeta">' + ''.join(f'<span>{c.ico(i)}{x}</span>' for i, x in items) + '</div>'
    # windows: three arch variants
    def winvar(a, main, msi, zp, z7, label):
        r = file_row(c, F[main], f'{c.t("dl_installer")} · {label}', '', 'windows', c.t('dl_rec') if a == '64' else '')
        alts = alt_row(c, F[msi], c.t('dl_msi'), c.t('dl_msi_d')) + alt_row(c, F[zp], c.t('dl_zip'), c.t('dl_zip_d')) + (alt_row(c, F[z7], c.t('dl_7z'), c.t('dl_7z_d')) if z7 else '')
        return f'<div data-arch="{a}"{"" if a == "64" else " hidden"}>{r}<div class="alts">{alts}</div></div>'
    seg = f'<div class="seg" role="group" aria-label="{e(c.t("dl_arch"))}"><button type="button" data-a="64" aria-pressed="true">{e(c.t("dl_64"))}</button><button type="button" data-a="arm" aria-pressed="false">{e(c.t("dl_arm"))}</button><button type="button" data-a="32" aria-pressed="false">{e(c.t("dl_32"))}</button></div>'
    win = (ph('windows', 'windows', 'Windows', c.t('dl_req_win'), seg) + winvar('64', 'win64', 'win64m', 'win64z', 'win647', c.t('dl_64')) + winvar('arm', 'arm64', 'arm64m', 'arm64z', None, 'ARM64') + winvar('32', 'win32', 'win32m', 'win32z', 'win327', c.t('dl_32')) +
           f'<div class="badges">{badge(c, STORE["ms"], "msstore", c.t("dl_get_on"), c.t("dl_store_ms"))}</div>' +
           meta(('shield', e(c.t('trust_signed'))), ('check', e(c.t('trust_free'))), ('arrow', f'<a href="{c.page("vlc--download-windows")}">{e(c.t("dl_all_opts", os="Windows"))}</a>')))
    mac = (ph('mac', 'apple', 'macOS', c.t('dl_req_mac')) + file_row(c, F['macu'], f'{c.t("dl_universal")} · {c.t("dl_universal_d")}', '', 'apple', c.t('dl_rec')) +
           '<div class="alts">' + alt_row(c, F['maca'], c.t('dl_silicon'), c.t('dl_silicon_d')) + alt_row(c, F['maci'], c.t('dl_intel'), c.t('dl_intel_d')) + link_row(c, c.page('vlc--download-macosx'), c.t('dl_legacy'), 'PowerPC · 10.5 · 10.6') + '</div>' +
           meta(('shield', e(c.t('trust_signed'))), ('check', e(c.t('trust_free')))))
    dbtn = ''.join(f'<button type="button" data-d="{k}" aria-pressed="{"true" if k == "ubuntu" else "false"}">{e(n)}</button>' for k, n, *_ in LINUX)
    dterm = ''.join(f'<div data-dterm="{k}"{"" if k == "ubuntu" else " hidden"}>{term(c, cmd, c.t(note) if note else "", n + " · " + pm)}' + (f'<p style="margin:.6rem 0 0;font-size:.9rem"><a href="{c.page(pg)}">{e(c.t("dl_distro_page", d=n))}</a></p>' if pg else '') + '</div>' for k, n, pm, cmd, pg, note in LINUX)
    lin = (ph('linux', 'linux', 'GNU/Linux', c.t('dl_linux_p')) + f'<div class="distros" role="group" aria-label="{e(c.t("dl_linux_h"))}">{dbtn}</div>{dterm}' +
           f'<div class="badges">{badge(c, STORE["flathub"], "package", c.t("dl_get_on"), "Flathub")}{badge(c, STORE["snap"], "package", c.t("dl_get_on"), "Snap Store")}</div>' +
           '<div class="alts" style="margin-top:1rem">' + ''.join(link_row(c, c.page(s), n, '') for s, n in [('vlc--download-redhat', 'Red Hat · CentOS'), ('vlc--download-slackware', 'Slackware'), ('vlc--download-altlinux', 'ALT Linux'), ('vlc--download-crux', 'CRUX')] if s in S.ALL) + '</div>')
    andr = (ph('android', 'android', 'Android', c.t('dl_req_and')) + qrs(c, [('play', 'Google Play'), ('fdroid', 'F-Droid'), ('apk', 'APK')]) + f'<div class="badges">{badge(c, STORE["play"], "gplay", c.t("dl_get_on"), "Google Play")}{badge(c, STORE["fdroid"], "fdroid", c.t("dl_get_on"), "F-Droid")}</div>' +
            '<div class="alts" style="margin-top:1rem">' + link_row(c, STORE['apk'], c.t('dl_apk') + ' · VLC for Android 3.7.0', c.t('dl_apk_d'), 'download') + link_row(c, c.page('vlc--download-android'), c.t('dl_all_opts', os='Android'), 'Android TV · Chromebook') + '</div>')
    ios = (ph('ios', 'phone', c.t('dl_ios_h'), c.t('dl_same_app')) + qrs(c, [('ios', 'App Store')]) + f'<div class="badges">{badge(c, STORE["ios"], "applef", c.t("dl_download_on"), "App Store")}</div>' +
           meta(('phone', e(c.t('dl_req_ios'))), ('tv', e(c.t('dl_req_tv')))) +
           '<div class="alts" style="margin-top:1rem">' + link_row(c, c.page('vlc--download-ios'), 'VLC for iOS', 'iPhone · iPad · iPod touch · Vision Pro') + link_row(c, c.page('vlc--download-appletv'), 'VLC for Apple TV', 'tvOS') + '</div>')
    src = (ph('source', 'code', c.t('os_source'), c.t('dl_src_d')) + file_row(c, F['src'], c.t('dl_src_tar'), '', 'code') +
           f'<div style="margin-top:1rem">{term(c, "git clone https://code.videolan.org/videolan/vlc.git", "", c.t("dl_src_git"))}</div>' +
           '<div class="alts" style="margin-top:1rem">' + link_row(c, c.page('vlc--download-sources'), c.t('dl_src_build'), 'contribs · toolchains') + '</div>')
    others = [('vlc--download-chromeos', 'ChromeOS'), ('vlc--download-freebsd', 'FreeBSD'), ('vlc--download-os2', 'OS/2'), ('vlc--download-winrt', 'Windows RT · UWP'), ('vlc--download-windowsphone', 'Windows Phone'), ('vlc--download-beos', 'BeOS · Haiku'), ('vlc--download-skins', c.t('ft_skins'))]
    oth = ph('other', 'box', c.t('os_other'), c.t('dl_other_p')) + '<div class="alts">' + ''.join(link_row(c, c.page(s), n, '') for s, n in others if s in S.ALL) + '</div>'
    panels = dict(windows=win, mac=mac, linux=lin, android=andr, ios=ios, source=src, other=oth)
    ph_html = ''.join(f'<div class="dpanel" role="tabpanel" id="dp-{k}" aria-labelledby="tab-{k}" data-panel="{k}"{"" if k == "windows" else " hidden"}>{panels[k]}</div>' for k, *_ in tabs)
    foot_ = (f'<div class="dl-foot"><div><b>{c.ico("shield")}{e(c.t("dl_verify_h"))}</b><p>{e(c.t("dl_verify_p"))}</p>'
             f'<div style="margin-top:.7rem">{term(c, "sha256sum vlc-" + V + "-win64.exe", "", c.t("dl_verify_cmd"))}</div></div>'
             f'<a href="https://download.videolan.org/pub/videolan/vlc/"><b>{c.ico("disc")}{e(c.t("dl_older"))}</b><p>{e(c.t("dl_mirrors"))} · 0.1 → {V}</p></a>'
             f'<a href="https://artifacts.videolan.org/vlc/nightly-win64/"><b>{c.ico("zap")}{e(c.t("dl_nightly"))}</b><p>VLC 4.0 · Windows · macOS · Linux</p></a></div>')
    return f'''<div class="dlx" id="{hid}-x"><div class="rail" role="tablist" aria-label="{e(c.t('dl_choose'))}" aria-orientation="vertical">{rail}</div><div>{ph_html}</div></div>{foot_}'''

# ------------------------------------------------------------------ home
FMTS1 = 'H.264 HEVC AV1 VP9 MPEG-2 ProRes DNxHD Theora VC-1 WMV DivX MJPEG H.263 Dirac VP8 Cinepak'.split()
FMTS2 = 'MKV MP4 WebM MOV AVI FLAC Opus AAC MP3 DTS TrueHD AC-3 ATRAC9 Vorbis ALAC WAV OGG TS'.split()
FMTS3 = 'DVD Blu-ray HLS DASH RTSP SRT RIST WebVTT ASS CEA-708 HDR10 Dolby Vision 360° 8K SMB NFS UPnP'.split()

def strip(h): return ' '.join(re.sub(r'<[^>]+>', ' ', H.unescape(h)).split())

def news_cards(c):
    out = []
    for i, n in enumerate(S.NEWS[:5]):
        href = c.page(S.NEWS_ANCHOR.get(n['id'], 'news'), '#' + n['id'] if n['id'] else '')
        txt = strip(n['html']); txt = txt[:220].rsplit(' ', 1)[0] + '…' if len(txt) > 220 else txt
        tag = '' if c.lang == 'en' else f'<span class="en-tag" lang="en">EN</span>'
        out.append(f'<a class="card glow rv d{i % 3}" href="{href}"><time datetime="{n["date"]}">{e(I.date(c.lang, n["date"]))}</time><h3 lang="en" dir="ltr">{e(n["title"])}{tag}</h3>' + (f'<p lang="en" dir="ltr">{e(txt)}</p>' if i < 3 else '') + f'<span class="more">{e(c.t("news_more"))}{c.ico("arrow", "ic flip")}</span></a>')
    return ''.join(out)

def home(c):
    c.slug = 'home'
    m = I.META[c.lang]
    h = [head(c, f'VideoLAN — VLC media player · {c.t("hero_a")} {c.t("hero_b")}', strip(c.t('hero_lede')), 'home')]
    w = F['win64']
    # ---------- hero
    pop = (f'<a href="{F["arm64"]["url"]}"{dlattrs(F["arm64"])}>Windows ARM64<span>{c.t("mb", n=F["arm64"]["mb"])}</span></a>'
           f'<a href="{F["win32"]["url"]}"{dlattrs(F["win32"])}>Windows {e(c.t("dl_32"))}<span>{c.t("mb", n=F["win32"]["mb"])}</span></a>'
           f'<a href="{F["macu"]["url"]}"{dlattrs(F["macu"])}>macOS · {e(c.t("dl_universal"))}<span>{c.t("mb", n=F["macu"]["mb"])}</span></a>'
           f'<a href="{c.page("download", "#download-linux")}">Linux<span>apt · dnf · Flatpak</span></a>'
           f'<a href="{STORE["play"]}">Android<span>Google Play</span></a><a href="{STORE["ios"]}">iPhone · iPad · Apple TV<span>App Store</span></a>'
           f'<hr><a href="{c.page("download")}">{e(c.t("cta_all"))}<span>{c.ico("arrow", "ic flip")}</span></a>')
    hero_sub = f'{c.t("cta_for", os="Windows")} · {c.t("dl_64")} · {c.t("mb", n=w["mb"])}'
    h.append(f'''<section class="hero"><div class="wrap hero-g">
<div>
<p class="kick"><a href="{c.page('vlc--releases--3.0.24')}" style="color:inherit">{e(c.t('hero_eyebrow', v=V, date=I.date(c.lang, REL_DATE)))}</a></p>
<h1><span class="l">{e(c.t('hero_a'))} <em>{e(c.t('hero_b'))}</em></span><span class="l">{e(c.t('hero_c'))}</span></h1>
<p class="lede">{e(c.t('hero_lede'))}</p>
<div class="cta">
<div class="cta-row">
<a class="cta-main" id="cta" href="{w['url']}"{dlattrs(w)}><span class="cta-os"><svg class="ic" aria-hidden="true"><use id="cta-ico" href="{c.root}icons.svg#i-windows"/></svg></span><span class="cta-t"><b id="cta-b">{e(c.t('cta_download'))}</b><span id="cta-s">{e(hero_sub)}</span></span><span class="cta-dl">{c.ico('download')}</span></a>
<button type="button" class="cta-alt" data-open="dl"><span class="cta-alt-i" aria-hidden="true">{c.ico('windows')}{c.ico('apple')}{c.ico('linux')}{c.ico('android')}</span><span>{e(c.t('cta_other'))}</span></button>
</div>
<div class="stores"><span>{e(c.t('cta_alsoon'))}</span><a class="store" href="{STORE['ms']}">{c.ico('msstore')}Microsoft Store</a><a class="store" href="{STORE['ios']}">{c.ico('applef')}App Store</a><a class="store" href="{STORE['play']}">{c.ico('gplay')}Google Play</a><a class="store" href="{STORE['flathub']}">{c.ico('package')}Flathub</a></div>
<ul class="trust"><li>{c.ico('check')}{e(c.t('trust_free'))}</li><li>{c.ico('shield')}{e(c.t('trust_signed'))}</li><li>{c.ico('lock')}{e(c.t('trust_sha'))}</li></ul>
</div></div>
<div class="stage" aria-label="{e(c.t('show_h'))}"><div class="tilt">{mk_win(c, 'bbb', eager=True)}</div>{mk_android(c)}</div>
</div></section>''')
    # ---------- platform strip
    plats = [('windows', 'windows', 'Windows'), ('apple', 'mac', 'macOS'), ('linux', 'linux', 'Linux'), ('android', 'android', 'Android'), ('phone', 'ios', 'iOS · iPadOS'), ('tv', 'ios', 'tvOS'), ('code', 'source', c.t('os_source'))]
    h.append(f'<div class="plat"><div class="wrap"><b>{e(c.t("os_other").split()[0] if False else c.t("dl_choose"))}</b>' + ''.join(f'<a href="{c.page("download", "#download-" + k)}" data-open="dl" data-os="{k}">{c.ico(i)}{e(n)}</a>' for i, k, n in plats) + '</div></div>')
    # ---------- showcase
    tabs = [('win', 'windows', 'os_windows'), ('mac', 'apple', 'os_mac'), ('lin', 'linux', 'os_linux'), ('and', 'android', 'os_android'), ('ios', 'phone', 'os_ios'), ('tv', 'tv', 'os_tv')]
    shows = {
      'win': (mk_win(c, 'sintel', 'mkv', 61, 888, 1), 'os_windows', 'win', 'windows'),
      'mac': (mk_mac(c, 'llama'), 'os_mac', 'mac', 'mac'),
      'lin': (mk_gnome(c, 'robot'), 'os_linux', 'lin', 'linux'),
      'and': (f'<div class="duo">{mk_win(c, "ed", "avi", 12, 654, 2)}{mk_android(c)}</div>', 'os_android', 'and', 'android'),
      'ios': (mk_iphone(c), 'os_ios', 'ios', 'ios'),
      'tv': (mk_tv(c), 'os_tv', 'tv', 'ios'),
    }
    tabh = ''.join(f'<button type="button" role="tab" id="st-{k}" aria-controls="sp-{k}" aria-selected="{"true" if k == "win" else "false"}" data-show="{k}">{c.ico(i)}{e(c.t(l))}</button>' for k, i, l in tabs)
    panes = ''
    for k, (mk, lk, pre, dk) in shows.items():
        pts = ''.join(f'<li>{c.ico("check")}<span>{e(c.t(pre + "_" + str(n)))}</span></li>' for n in (1, 2, 3))
        panes += f'<div class="show" role="tabpanel" id="sp-{k}" aria-labelledby="st-{k}"{"" if k == "win" else " hidden"}><div>{mk}</div><div><h3>VLC · {e(c.t(lk))}</h3><ul class="pts">{pts}</ul><a class="btn btn-gh" href="{c.page("download", "#download-" + dk)}">{c.ico("download")}{e(c.t("get_for", os=c.t(lk)))}</a></div></div>'
    h.append(f'''<section class="band" id="platforms"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('show_k'))}</p><h2>{e(c.t('show_h'))}</h2></div><p>{e(c.t('show_p'))}</p></div>
<div class="tabs" role="tablist" aria-label="{e(c.t('show_k'))}">{tabh}</div>{panes}
</div></section>''')
    # ---------- features bento
    marq = lambda xs: '<div>' + ''.join(f'<span>{x}</span>' for x in xs + xs) + '</div>'
    h.append(f'''<section class="band band-alt" id="features"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('feat_k'))}</p><h2>{e(c.t('feat_h'))}</h2></div><a class="more" href="{c.page('vlc--features')}">{e(c.t('all_features'))}{c.ico('arrow', 'ic flip')}</a></div>
<div class="bento">
<article class="tile b1 glow rv">{c.ico('film')}<h3>{e(c.t('f1_h'))}</h3><p>{e(c.t('f1_p'))}</p><div class="fmts" aria-hidden="true">{marq(FMTS1)}{marq(FMTS2)}{marq(FMTS3)}</div></article>
<article class="tile b2 glow rv d1">{c.ico('gauge')}<h3>{e(c.t('f2_h'))}</h3><p>{e(c.t('f2_p'))}</p><div class="meter" aria-hidden="true"><div>4K60<i><b style="--v:28%"></b></i>28%</div><div>8K30<i><b style="--v:41%"></b></i>41%</div><div>HDR10<i><b style="--v:19%"></b></i>19%</div></div></article>
<article class="tile b3 glow rv">{c.ico('cc')}<h3>{e(c.t('f3_h'))}</h3><p>{e(c.t('f3_p'))}</p><div class="subdemo" aria-hidden="true"><img src="{c.root}media/sintel-640.jpg" alt="" loading="lazy" width="640" height="334"><span class="dly" data-delay>+250 ms</span><p class="sub" aria-hidden="true" lang="{m['html']}" dir="{m['dir']}">{e(SUBS[c.lang][1])}</p></div></article>
<article class="tile b4 glow rv d1">{c.ico('stream')}<h3>{e(c.t('f4_h'))}</h3><p>{e(c.t('f4_p'))}</p><div class="lan" aria-hidden="true"><div>{c.ico('folder')}<b>NAS</b><span>SMB · NFS</span><i></i></div><div>{c.ico('tv')}<b>Chromecast</b><span>1080p · HDR</span><i></i></div><div>{c.ico('stream')}<b>SRT listener</b><span>:9000</span><i></i></div></div><div class="net" aria-hidden="true">{''.join(f'<span>{x}</span>' for x in 'HLS DASH RTSP SRT RIST UDP SMB NFS UPnP SFTP'.split())}</div></article>
<article class="tile b5 glow rv">{c.ico('shield')}<h3>{e(c.t('f5_h'))}</h3><p>{e(c.t('f5_p'))}</p><div class="badge-0"><b>0</b><span>{e(c.t('stat_ads'))}</span></div></article>
<article class="tile b6 glow rv d1">{c.ico('heart')}<h3>{e(c.t('f6_h'))}</h3><p>{e(c.t('f6_p'))}</p></article>
<article class="tile b7 glow rv d2">{c.ico('palette')}<h3>{e(c.t('f7_h'))}</h3><p>{e(c.t('f7_p'))}</p></article>
</div></div></section>''')
    # ---------- what's new
    wn = ''.join(f'<li class="rv d{i % 3}">{c.ico("check")}<span>{e(c.t("new_" + str(i)))}</span></li>' for i in range(1, 7))
    h.append(f'''<section class="band" id="new"><div class="wrap wn">
<div class="wn-big rv"><p class="kick" style="color:#ffb366">{e(c.t('new_k'))} · {V}</p><b data-count="130">130+</b><span>{e(c.t('new_fixes'))}</span><a class="btn btn-or" href="{c.page('vlc--releases--3.0.24')}">{e(c.t('dl_notes'))}{c.ico('arrow', 'ic flip')}</a></div>
<div><h2 style="font-size:clamp(1.7rem,1.2rem + 1.8vw,2.5rem);margin-bottom:1.5rem">{e(c.t('new_h', v=V))}</h2><ul>{wn}</ul></div>
</div></section>''')
    # ---------- download (compact; full centre lives on its own page)
    cards = [('windows', 'windows', 'Windows', f'{c.t("dl_installer")} · MSI · ZIP', F['win64']), ('mac', 'apple', 'macOS', c.t('dl_universal_d'), F['macu']),
             ('linux', 'linux', 'Linux', 'apt · dnf · pacman · Flatpak · Snap', None), ('android', 'android', 'Android', 'Google Play · F-Droid · APK', None),
             ('ios', 'phone', c.t('dl_ios_h'), 'App Store', None), ('source', 'code', c.t('os_source'), 'tar.xz · git', F['src'])]
    ch = ''.join(f'<a class="pc glow rv d{i % 3}" href="{c.page("download", "#download-" + k)}" data-pc="{k}" data-open="dl" data-os="{k}"><span class="fic">{c.ico(ic)}</span><b>{e(n)}</b><small>{e(sub)}</small>' + (f'<span class="sz">{e(c.t("mb", n=f_["mb"]))}</span>' if f_ else '<span class="sz"></span>') + f'{c.ico("arrow", "ic flip go")}</a>' for i, (k, ic, n, sub, f_) in enumerate(cards))
    h.append(f'''<section class="band band-alt" id="download"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('dl_k'))}</p><h2>{e(c.t('hp_dl_h'))}</h2></div><p>{e(c.t('dl_p'))}<br><span style="color:var(--tx-3);font-size:.9rem">VLC {V} · {e(c.t('dl_meta', code=CODE, date=I.date(c.lang, REL_DATE)))}</span></p></div>
<div class="pcs">{ch}</div>
<p class="center"><a class="btn btn-or" href="{c.page('download')}">{c.ico('download')}{e(c.t('hp_dl_all'))}</a></p>
</div></section>''')
    # ---------- tips
    tips = [('convert', 't1'), ('record', 't2'), ('bandage', 't3'), ('gauge', 't4'), ('camera', 't5'), ('cast', 't6')]
    def kb(s): return re.sub(r'(Shift\+S|⌥⌘S|Maj\+S|\[|\]|G|H)(?=[\s,，、.。)）و]|$)', lambda m_: f'<kbd>{m_.group(1)}</kbd>', e(s))
    h.append(f'''<section class="band" id="tips"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('tips_k'))}</p><h2>{e(c.t('tips_h'))}</h2></div><a class="more" href="{c.page('support--faq')}">{e(c.t('ft_faq'))}{c.ico('arrow', 'ic flip')}</a></div>
<div class="tips">{''.join(f'<div class="tip rv d{i % 3}">{c.ico(ic)}<div><h3>{e(c.t(k + "_h"))}</h3><p>{kb(c.t(k + "_p"))}</p></div></div>' for i, (ic, k) in enumerate(tips))}</div>
</div></section>''')
    # ---------- news
    h.append(f'''<section class="band band-alt" id="news"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('news_k'))}</p><h2>{e(c.t('news_h'))}</h2></div><a class="more" href="{c.page('news')}">{e(c.t('news_all', n=len(S.NEWS)))}{c.ico('arrow', 'ic flip')}</a></div>
<div class="news">{news_cards(c)}</div></div></section>''')
    # ---------- ecosystem
    eco = [('libVLC', 'eco_libvlc', 'vlc--libvlc', 'code'), ('dav1d', 'eco_dav1d', 'projects--dav1d', 'zap'), ('x264', 'eco_x264', 'developers--x264', 'film'),
           ('DVBlast', 'eco_dvblast', 'projects--dvblast', 'tv'), ('libbluray · libdvdcss', 'eco_bluray', 'developers--libbluray', 'disc'), ('multicat', 'eco_multicat', 'projects--multicat', 'stream')]
    h.append(f'''<section class="band" id="projects"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('eco_k'))}</p><h2>{e(c.t('eco_h'))}</h2></div><a class="more" href="{c.page('section--projects')}">{e(c.t('eco_all'))}{c.ico('arrow', 'ic flip')}</a></div>
<div class="grid-3">{''.join(f'<a class="card glow rv d{i % 3}" href="{c.page(s)}"><h3>{c.ico(ic)}<span dir="ltr">{e(n)}</span></h3><p>{e(c.t(k))}</p><span class="more">{e(c.t("eco_more"))}{c.ico("arrow", "ic flip")}</span></a>' for i, (n, k, s, ic) in enumerate(eco))}</div>
</div></section>''')
    # ---------- community + donate
    com = [('code', 'c1', 'developers'), ('globe', 'c2', 'developers--i18n' if 'developers--i18n' in S.ALL else 'contribute'), ('chat', 'c3', 'support'), ('bug', 'c4', 'contribute')]
    h.append(f'''<section class="band band-alt" id="contribute"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('com_k'))}</p><h2>{e(c.t('com_h'))}</h2></div><p>{e(c.t('com_p'))}</p></div>
<div class="grid-4">{''.join(f'<a class="card glow rv d{i % 3}" href="{c.page(s)}"><h3>{c.ico(ic)}{e(c.t(k + "_h"))}</h3><p>{e(c.t(k + "_p"))}</p><span class="more">{e(c.t("eco_more"))}{c.ico("arrow", "ic flip")}</span></a>' for i, (ic, k, s) in enumerate(com))}</div>
<div class="dband rv"><div><p class="kick">{e(c.t('don_k'))}</p><h2>{e(c.t('don_h'))}</h2><p>{e(c.t('don_p'))}</p><small>{e(c.t('don_ways'))}</small></div><div><a class="btn btn-or" href="{c.page('contribute')}" data-donate>{c.ico('heart')}{e(c.t('don_btn'))}</a></div></div>
</div></section>''')
    # ---------- about
    tl = [('1996', 'y1996'), ('2001', 'y2001'), ('2009', 'y2009'), ('2018', 'y2018'), ('2026', 'y2026')]
    partners = 'Free · Gandi · MacStadium · Videolabs · MetaBrainz · École Centrale · EPITECH · Puget Systems · Panasonic · TASCAM'.split(' · ')
    stats = [('30', 'stat_years'), ('40+', 'stat_countries'), (str(len(S.PAGES)), 'stat_pages'), ('0', 'stat_ads')]
    h.append(f'''<section class="band" id="about"><div class="wrap">
<div class="sh"><div><p class="kick">{e(c.t('about_k'))} · {e(c.t('tl_title'))}</p><h2>{e(c.t('about_h'))}</h2></div><p>{e(c.t('about_p'))} <a href="{c.page('videolan--team')}">{e(c.t('team'))}</a></p></div>
<ol class="tl">{''.join(f'<li class="rv d{i % 3}"><b>{y}</b><span>{e(c.t(k, v=V))}</span></li>' for i, (y, k) in enumerate(tl))}</ol>
<div class="stats">{''.join(f'<div class="rv"><b data-count="{re.sub(r"[^0-9]", "", n)}">{n}</b><span>{e(c.t(k))}</span></div>' for n, k in stats)}</div>
<h3 style="margin-top:3rem;font-size:1.1rem">{e(c.t('partners_h'))}</h3>
<div class="partners" dir="ltr">{''.join(f'<span>{e(p)}</span>' for p in partners)}</div>
<p style="margin-top:1rem"><a class="more" href="{c.page('videolan--partners')}">{e(c.t('partners'))}{c.ico('arrow', 'ic flip')}</a></p>
</div></section>''')
    intents = ''.join(f'<button type="button" class="chip" data-go="{g}" data-sel="{sel}">{c.ico(ic)}{e(c.t(k))}</button>' for k, ic, g, sel in [
        ('i_install', 'download', 'auto', '.file'), ('i_portable', 'box', 'windows', '[data-arch]:not([hidden]) .alts > :nth-child(2)'),
        ('i_store', 'phone', 'store', '.badges'), ('i_cli', 'code', 'linux', '.distros'), ('i_older', 'disc', '', 'older'), ('i_src', 'code', 'source', '.file')])
    h.append(f'<template id="dlt"><div class="ly dlm" id="dlm" aria-hidden="true"><div class="scrim" data-x></div><div class="dlg" role="dialog" aria-modal="true" aria-labelledby="dlm-t"><div class="st-h"><span class="st-logo"><svg viewBox="0 0 64 64" aria-hidden="true"><use href="{c.root}icons.svg#i-cone"/></svg></span><div><h2 id="dlm-t">{e(c.t("dlm_h"))}</h2><p>VLC {V} · {e(c.t("dlm_p"))}</p></div><button type="button" class="x" data-x aria-label="{e(c.t("close"))}">{c.ico("x")}</button></div><div class="dlm-int" role="group" aria-label="{e(c.t("dlm_q"))}"><span>{e(c.t("dlm_q"))}</span>{intents}</div><div class="dlm-b">{download_block(c, "dlm")}</div></div></div></template>')
    h.append(foot(c))
    return '\n'.join(h)

# ------------------------------------------------------------------ content pages
def page_display(c, p):
    if p.get('hub'): return sec(c.lang, p['hub'], 0)
    s = p['slug']
    if s == 'download': return c.t('dl_h', v=V)
    if s == 'news': return c.t('nav_news')
    if s.startswith('news--'):
        y = s[6:]; return c.t('news_year', y=y) if y != 'undated' else c.t('undated')
    if s == 'sitemap': return c.t('site_index')
    if s == 'design-notes': return c.t('design_notes')
    if s in CU.CUR_TITLE: return CU.P(c, CU.CUR_TITLE[s])
    return H.unescape(p['display'])

def localized_body(c, p):
    """Return (html, translated?)"""
    s = p['slug']
    if s == 'download':
        return f'<p class="x-lede">{e(c.t("dl_p"))}</p>' + download_block(c, 'dlp'), True
    if p.get('hub'):
        return CU.section_hub(c, p['hub']), True
    if s == 'news': return CU.news_hub(c), c.lang == 'en'
    if s.startswith('news--'): return CU.news_year(c, s[6:]), c.lang == 'en'
    if s in CU.CURATED: return CU.CURATED[s](c, p), True
    if False:
        k = p['hub']; items = S.ordered(k)
        hh = [f'<p class="x-lede">{e(sec(c.lang, k, 1))}</p><div class="x-list">']
        for q in items: hh.append(f'<a class="x-li" href="{q["slug"]}.html" lang="en"><b>{e(q["display"])}</b><span>{e(q["path"])}</span></a>')
        if k == 'news':
            for y in S.YEARS: hh.append(f'<a class="x-li" href="news--{y}.html"><b>{e(c.t("news_year", y=y))}</b><span>{e(c.t("p_items", n=len(S.NEWS_BY_YEAR[y])))}</span></a>')
        hh.append('</div>'); return '\n'.join(hh), True
    if s == 'news' or s.startswith('news--'):
        ys = S.YEARS + (['undated'] if 'undated' in S.NEWS_BY_YEAR else [])
        cur = s[6:] if s != 'news' else None
        nav = f'<nav class="x-years" aria-label="{e(c.t("news_by_year"))}">' + ''.join(f'<a href="news--{y}.html"' + (' aria-current="page"' if y == cur else '') + f'>{y if y != "undated" else e(c.t("undated"))} <small>{len(S.NEWS_BY_YEAR[y])}</small></a>' for y in ys) + '</nav>'
        items = S.NEWS[:24] if cur is None else S.NEWS_BY_YEAR[cur]
        body = ''.join(f'<article class="x-item" id="{e(n["id"])}"><time datetime="{e(n["date"])}">{e(I.date(c.lang, n["date"]) if n["date"][:4] not in ("", "1970") else c.t("undated"))}</time><div lang="en" dir="ltr"><h3>{e(n["title"])}</h3><div>{n["html"]}</div></div></article>' for n in items)
        lede = f'<p class="x-lede">{e(c.t("news_lede", n=len(S.NEWS)))}</p>' if cur is None else ''
        return lede + nav + '<div class="x-news">' + S.rewrite(body) + '</div>', c.lang == 'en'
    if s == 'sitemap':
        hh = [f'<p class="x-lede">{e(c.t("sitemap_lede", n=len(S.PAGES)))}</p><div class="x-map">']
        for k in S.SECTIONS:
            items = S.ordered(k)
            hh.append(f'<section><h2 id="map-{k}"><a href="section--{k}.html">{e(sec(c.lang, k, 0))}</a> <small>{len(items)}</small></h2><ul lang="en">' + ''.join(f'<li><a href="{q["slug"]}.html">{e(q["display"])}</a></li>' for q in items) + '</ul></section>')
        hh.append('</div>'); return '\n'.join(hh), True
    if s == 'design-notes':
        return NOTES.get(c.lang, NOTES['en']), True
    return S.rewrite(p['html']), c.lang == 'en'

def add_sha(htm):
    def rep(m):
        u = H.unescape(m.group(1)); f = BY_URL.get(u)
        return m.group(0) + (f' data-sha="{f["sha"]}" data-size="{f["size"]}"' if f else '')
    return re.sub(r'href="([^"]*)" data-dl', rep, htm)

SEC_ICON = CU.SEC_ICON
def content_page(c, p):
    slug = p['slug']; c.slug = slug
    title = page_display(c, p)
    k = p['hub'] if p.get('hub') else S.sec_key(p)
    if slug == 'vlc--features': k = 'vlc'
    body, tr = localized_body(c, p)
    body = add_sha(body)
    wide = bool(p.get('hub')) or slug in CU.CURATED or slug in ('download', 'news', 'sitemap', 'design-notes') or slug.startswith('news--')
    body, toc = S.toc(body) if not slug in CU.CURATED else (body, [])
    cur = {'download': 'download', 'news': 'news', 'projects': 'projects', 'support': 'support', 'contribute': 'contribute', 'videolan': 'about', 'vlc': 'features'}.get(k, '')
    if slug == 'vlc--features': cur = 'features'
    desc = p.get('desc') or (strip(sec(c.lang, k, 1)) if k in S.SECTIONS else 'VideoLAN')
    out = [head(c, f'{title} — VideoLAN', desc, slug, cur)]
    seclabel = sec(c.lang, k, 0) if k in S.SECTIONS else p['section']
    chips = [f'<span>{c.ico(SEC_ICON.get(k, "book"))}{e(seclabel)}</span>']
    if not p.get('virtual') and not slug in CU.CURATED: chips.append(f'<span>{c.ico("book")}{e(c.t("min_read", n=S.read_min(p["words"])))}</span>')
    if p.get('path') and not p.get('virtual'): chips.append(f'<a href="https://www.videolan.org{e(p["path"])}">{c.ico("ext")}{e(c.t("p_source"))}</a>')
    note = '' if tr else f'<p class="untr">{c.ico("info")}<span>{e(c.t("untranslated"))}</span></p>'
    lang_attr = '' if tr or c.lang == 'en' else ' lang="en" dir="ltr"'
    h1_lang = ' lang="en" dir="ltr"' if (not tr and c.lang != 'en' and title == p['display']) else ''
    lede = ''
    if not wide and p.get('desc') and len(p['desc']) < 240: lede = f'<p class="lede"{lang_attr}>{e(p["desc"])}</p>'
    icon = CU.CUR_ICON.get(slug) or SEC_ICON.get(k, 'book')
    # sidebar: siblings in section
    side = ''; bandhtml = ''
    projmode = (not wide or slug == 'projects') and CU.in_dir(slug, p) and slug != 'section--projects'
    if projmode:
        k = 'projects'; seclabel = sec(c.lang, 'projects', 0)
        side = CU.directory(c, slug)
        if slug == 'projects': side = ''
        bandhtml = CU.band(c, slug) if slug != 'projects' else ''
    elif not wide and k in S.SECTIONS:
        sib = S.ordered(k); idx = next((i for i, q in enumerate(sib) if q['slug'] == slug), 0)
        lo = max(0, idx - 10); win = sib[lo:lo + 22]
        side = (f'<aside class="side"><details open><summary>{c.ico(SEC_ICON.get(k, "book"))}<span>{e(CU.P(c, CU.U["in_section"]))}</span><small>{len(sib)}</small></summary><ul{lang_attr}>' +
                ''.join(f'<li><a href="{q["slug"]}.html"' + (' aria-current="page"' if q['slug'] == slug else '') + f'>{e(page_display(c, q))}</a></li>' for q in win) +
                f'</ul><a class="all" href="section--{k}.html">{e(CU.P(c, CU.U["everything"]).replace("{s}", seclabel))}{c.ico("arrow", "ic flip")}</a></details></aside>')
    tochtml = ''
    if len(toc) >= 3 and not wide:
        tochtml = f'<aside class="toc" aria-label="{e(c.t("on_page"))}"><p class="kick">{e(c.t("on_page"))}</p><ul{lang_attr}>' + ''.join(f'<li><a href="#{i}">{e(x)}</a></li>' for i, x in toc[:18]) + '</ul></aside>'
    prev, nxt = S.seq(slug)
    pn = ''
    if (prev or nxt) and not wide and not projmode:
        pn = f'<nav class="pn" aria-label="{e(seclabel)}">' + (f'<a href="{prev}.html"><small>{c.ico("arrow", "ic back")}{e(c.t("previous"))}</small><b lang="en">{e(page_display(c, S.ALL[prev]))}</b></a>' if prev else '<span></span>') + (f'<a class="r" href="{nxt}.html"><small>{e(c.t("next"))}{c.ico("arrow", "ic flip")}</small><b lang="en">{e(page_display(c, S.ALL[nxt]))}</b></a>' if nxt else '<span></span>') + '</nav>'
    crumb_extra = ''
    own = CU.owner(slug) if projmode else None
    if own and own != slug and own in S.ALL: crumb_extra = f'<span aria-hidden="true">/</span><a href="{own}.html" dir="ltr">{e(page_display(c, S.ALL[own]))}</a>'
    if projmode and not tochtml == '' and slug != 'projects': pass
    lay = 'pw3 wide' if wide else 'pw3' + (' has-side' if side else '') + (' has-toc' if tochtml else '')
    out.append(f'''<div class="rprog" aria-hidden="true"><i></i></div>
<section class="ph"><div class="wrap ph-g"><div>
<nav class="crumbs" aria-label="Breadcrumb"><a href="{c.page('home')}">{e(c.t('home'))}</a><span aria-hidden="true">/</span><a href="{'projects' if k == 'projects' else 'section--' + k}.html">{e(seclabel)}</a>{crumb_extra}</nav>
<h1{h1_lang}>{e(title)}</h1>{lede}
<div class="ph-meta">{''.join(chips)}</div></div>
<span class="ph-ic" aria-hidden="true">{c.ico(icon)}</span>
</div></section>
<div class="wrap pgw">{bandhtml}{note}<div class="{lay}">{side}<article class="prose{' pz' if wide else ''}"{lang_attr}>{body}</article>{tochtml}</div>{pn}</div>''')
    out.append(foot(c))
    return '\n'.join(out)

NOTES = {
 'en': '''<p class="x-lede">An independent proposal for videolan.org: the whole current site, rebuilt as one fast, accessible, static HTML5 bundle, in four languages to start.</p>
<h2>What changes</h2><ul>
<li><b>One settings hub.</b> Search, language, theme, text size, contrast, motion and shortcuts live behind a single Settings button that opens a full-screen panel.</li>
<li><b>Real landing pages.</b> Features, Projects, Team, About, Contribute, Support, libVLC and News each have their own redesigned page, with section hubs, sidebars and on-page navigation for the 300 carried-over pages.</li>

<li><b>One download button that knows your device.</b> It picks the right file for Windows (x64, ARM64 or 32-bit), macOS, Linux, Android or iOS, shows its size, and keeps every other option one click away.</li>
<li><b>A real download centre.</b> Every platform in one place: installers, MSI, portable ZIP and 7z, Apple Silicon and Intel builds, copy-ready commands for eight Linux distributions, store badges, source code, SHA-256 fingerprints and verification help.</li>
<li><b>Honest exits.</b> Downloads come straight from get.videolan.org, after a short confirmation that shows the file and its fingerprint. VideoLAN services that are not redesigned yet, and third-party sites, are announced before you leave.</li>
<li><b>Donations in one click.</b> A full-screen checkout with Apple Pay, Google Pay, card and SEPA through VideoLAN’s Stripe checkout, PayPal once or monthly, bank transfer and Bitcoin.</li>
<li><b>VLC, shown for real.</b> Player mockups for Windows, macOS, Linux, Android, iPhone and Apple TV, playing open films from the Blender Foundation.</li>
<li><b>Languages.</b> English, French, Simplified Chinese and Arabic (right-to-left) are written; the selector already lists 81 languages.</li>
<li><b>Accessible and light.</b> No framework, no web fonts, no cookies, no trackers. Text size, contrast, motion, link and spacing settings; full keyboard support. Effects only run on modern browsers that allow motion; older browsers get the same content, statically.</li>
</ul><p>Unofficial concept by Paul Fleury, offered to VideoLAN under the MIT licence. VLC, VideoLAN and the cone are trademarks of VideoLAN. Content is adapted from videolan.org.</p>''',
 'fr': '''<p class="x-lede">Une proposition indépendante pour videolan.org : tout le site actuel, reconstruit en un seul ensemble HTML5 statique, rapide et accessible, en quatre langues pour commencer.</p>
<h2>Ce qui change</h2><ul>
<li><b>Un seul centre de réglages.</b> Recherche, langue, thème, taille du texte, contraste, animations et raccourcis sont réunis derrière un bouton Réglages qui ouvre un panneau plein écran.</li>
<li><b>De vraies pages d’accueil.</b> Fonctionnalités, Projets, Équipe, À propos, Contribuer, Assistance, libVLC et Actualités ont chacune leur page repensée, avec des rubriques, une barre latérale et une navigation interne pour les 300 pages reprises.</li>

<li><b>Un bouton de téléchargement qui reconnaît votre appareil.</b> Il choisit le bon fichier pour Windows (x64, ARM64 ou 32 bits), macOS, Linux, Android ou iOS, affiche sa taille et garde toutes les autres options à portée de clic.</li>
<li><b>Un vrai centre de téléchargement.</b> Toutes les plateformes au même endroit : installateurs, MSI, ZIP portable et 7z, versions Apple Silicon et Intel, commandes prêtes à copier pour huit distributions Linux, badges des boutiques, code source, empreintes SHA-256 et aide à la vérification.</li>
<li><b>Des sorties annoncées.</b> Les téléchargements viennent directement de get.videolan.org, après une courte confirmation qui affiche le fichier et son empreinte. Les services VideoLAN pas encore redessinés et les sites tiers sont signalés avant de partir.</li>
<li><b>Des dons en un clic.</b> Un paiement plein écran avec Apple Pay, Google Pay, carte et SEPA via le Stripe de VideoLAN, PayPal ponctuel ou mensuel, virement et Bitcoin.</li>
<li><b>VLC, montré pour de vrai.</b> Des maquettes du lecteur sous Windows, macOS, Linux, Android, iPhone et Apple TV, avec des films libres de la Blender Foundation.</li>
<li><b>Les langues.</b> L’anglais, le français, le chinois simplifié et l’arabe (de droite à gauche) sont rédigés ; le sélecteur liste déjà 81 langues.</li>
<li><b>Accessible et léger.</b> Ni framework, ni police web, ni cookie, ni pisteur. Réglages de taille du texte, de contraste, d’animations, de liens et d’espacement ; navigation complète au clavier. Les effets ne s’activent que sur les navigateurs récents qui autorisent les animations ; les anciens affichent le même contenu, sans mouvement.</li>
</ul><p>Concept non officiel de Paul Fleury, offert à VideoLAN sous licence MIT. VLC, VideoLAN et le cône sont des marques de VideoLAN. Le contenu est adapté de videolan.org.</p>''',
 'zh': '''<p class="x-lede">这是一份为 videolan.org 准备的独立提案：把现有网站的全部内容重建为一个快速、无障碍的静态 HTML5 站点，首批提供四种语言。</p>
<h2>有哪些改变</h2><ul>
<li><b>统一的设置中心。</b>搜索、语言、主题、文字大小、对比度、动画和快捷键都收进一个“设置”按钮，点开即是全屏面板。</li>
<li><b>真正的栏目首页。</b>功能、项目、团队、关于、参与贡献、支持、libVLC 和新闻都有重新设计的独立页面；迁移过来的 300 个页面也配有栏目页、侧边栏和页内导航。</li>

<li><b>一个能识别设备的下载按钮。</b>它会为 Windows（x64、ARM64 或 32 位）、macOS、Linux、Android 或 iOS 自动选择正确的文件并显示大小，其他选项也只需一次点击。</li>
<li><b>真正的下载中心。</b>所有平台集中在一处：安装程序、MSI、便携 ZIP 与 7z、Apple 芯片和 Intel 版本、八个 Linux 发行版的可复制命令、应用商店徽章、源代码、SHA-256 指纹及校验说明。</li>
<li><b>离开前明确提示。</b>下载文件直接来自 get.videolan.org，下载前会显示文件名和指纹。尚未改版的 VideoLAN 服务和第三方网站，都会在跳转前提示。</li>
<li><b>一键捐赠。</b>全屏结账页面：通过 VideoLAN 的 Stripe 支持 Apple Pay、Google Pay、银行卡和 SEPA，另有 PayPal（单次或按月）、银行转账和比特币。</li>
<li><b>真实呈现 VLC。</b>Windows、macOS、Linux、Android、iPhone 和 Apple TV 上的播放器样机，播放的是 Blender 基金会的开放影片。</li>
<li><b>多语言。</b>英文、法文、简体中文和阿拉伯文（从右到左）已完成；语言选择器已列出 81 种语言。</li>
<li><b>无障碍且轻量。</b>不用框架、不用网络字体、没有 Cookie、没有追踪。可调节文字大小、对比度、动画、链接与间距，全程支持键盘操作。动效只在允许动画的新式浏览器中运行，旧浏览器会看到同样的内容，只是静态呈现。</li>
</ul><p>本方案为 Paul Fleury 的非官方设计概念，以 MIT 许可证赠予 VideoLAN。VLC、VideoLAN 及路锥标志均为 VideoLAN 的商标。内容改编自 videolan.org。</p>''',
 'ar': '''<p class="x-lede">مقترح مستقل لموقع videolan.org: الموقع الحالي كاملًا، أُعيد بناؤه حزمةً واحدة من HTML5 الثابت، سريعة وسهلة الوصول، بأربع لغات كبداية.</p>
<h2>ما الذي يتغيّر</h2><ul>
<li><b>مركز إعدادات واحد.</b> البحث واللغة والسمة وحجم النص والتباين والحركة والاختصارات كلها خلف زر «الإعدادات» الذي يفتح لوحة بملء الشاشة.</li>
<li><b>صفحات رئيسية حقيقية.</b> للميزات والمشاريع والفريق ومن نحن والمساهمة والدعم وlibVLC والأخبار صفحات أُعيد تصميمها، مع صفحات أقسام وشريط جانبي وتنقّل داخلي للصفحات الـ300 المنقولة.</li>

<li><b>زر تنزيل واحد يتعرّف على جهازك.</b> يختار الملف المناسب لـ Windows (x64 أو ARM64 أو 32 بت) أو macOS أو Linux أو Android أو iOS، ويعرض حجمه، ويُبقي كل الخيارات الأخرى على بُعد نقرة.</li>
<li><b>مركز تنزيل حقيقي.</b> كل المنصّات في مكان واحد: برامج التثبيت وMSI وZIP المحمول و7z، وإصدارات Apple Silicon وIntel، وأوامر جاهزة للنسخ لثماني توزيعات Linux، وشارات المتاجر، والشيفرة المصدرية، وبصمات SHA-256 وطريقة التحقّق.</li>
<li><b>مغادرة واضحة.</b> تأتي التنزيلات مباشرة من get.videolan.org بعد تأكيد قصير يعرض الملف وبصمته. ويُنبَّه الزائر قبل الانتقال إلى خدمات VideoLAN التي لم يُعَد تصميمها بعد أو إلى مواقع خارجية.</li>
<li><b>تبرّع بنقرة واحدة.</b> صفحة دفع بملء الشاشة تدعم Apple Pay وGoogle Pay والبطاقة وSEPA عبر Stripe الخاص بـ VideoLAN، وPayPal لمرة واحدة أو شهريًا، والتحويل البنكي والبيتكوين.</li>
<li><b>VLC كما هو فعلًا.</b> نماذج للمشغّل على Windows وmacOS وLinux وAndroid وiPhone وApple TV، تعرض أفلامًا مفتوحة من مؤسسة Blender.</li>
<li><b>اللغات.</b> الإنجليزية والفرنسية والصينية المبسّطة والعربية (من اليمين إلى اليسار) مكتملة، وتضم قائمة اللغات 81 لغة.</li>
<li><b>سهل الوصول وخفيف.</b> بلا أُطر عمل، ولا خطوط ويب، ولا ملفات تعريف ارتباط، ولا متتبّعات. إعدادات لحجم النص والتباين والحركة والروابط والتباعد، ودعم كامل للوحة المفاتيح. لا تعمل المؤثرات إلا في المتصفحات الحديثة التي تسمح بالحركة، أما المتصفحات القديمة فتعرض المحتوى نفسه بلا حركة.</li>
</ul><p>تصوّر غير رسمي من Paul Fleury، مُهدى إلى VideoLAN برخصة MIT. ‏VLC وVideoLAN والمخروط علامات تجارية لـ VideoLAN. المحتوى مقتبس من videolan.org.</p>''',
}

# ------------------------------------------------------------------ l10n.js per language
JS_KEYS = [k for k in I.T if k.startswith(('js_', 'x_', 'd_', 'dl_copy', 'dl_copied', 'search', 'close', 'language', 'display', 'theme_', 'mb', 'cta_', 'dl_64', 'dl_32', 'dl_arm', 'dl_universal', 'os_', 'mk_sub', 'mk_speed', 'osd_vol', 'mk_alt', 'qr_', 'set_'))]

def l10n_js(lang):
    o = {k: t(lang, k) for k in JS_KEYS}
    o['_lang'] = lang; o['_dir'] = I.META[lang]['dir']
    o['_secs'] = {k: sec(lang, k, 0) for k in S.SECTIONS}
    o['_avail'] = {'en': '', 'fr': 'fr', 'zh-Hans': 'zh', 'ar': 'ar'}
    o['_dl'] = {k: dict(url=F[k]['url'], sha=F[k]['sha'], size=F[k]['size']) for k in ('win64', 'arm64', 'win32', 'macu')}
    o['_store'] = STORE
    return 'window.VL=' + json.dumps(o, ensure_ascii=False, separators=(',', ':')) + ';'

# ------------------------------------------------------------------ minify helpers
def min_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([{};,>])\s*', r'\1', s)
    s = re.sub(r':\s+', ':', s)
    return s.replace(';}', '}').strip()

def write(path, txt):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.html':
        txt = re.sub(r'<a [^>]*>\s*</a>', '', txt)                       # empty legacy links
        txt = re.sub(r'<pre(?![^>]*tabindex)', '<pre tabindex="0"', txt)  # scrollable code is keyboard-reachable
    path.write_text(txt)

HTACCESS = r"""# VideoLAN redesign — server rules (Apache / SiteGround)
Options -Indexes
AddDefaultCharset utf-8
AddType image/svg+xml .svg
AddType image/webp .webp
DirectoryIndex index.html
<IfModule mod_rewrite.c>
RewriteEngine On
# ?full=1 opts out of the simple version for a year
RewriteCond %{QUERY_STRING} (^|&)full=1
RewriteRule ^ - [CO=vlfull:1:%{HTTP_HOST}:525600:/]
# Old or limited browsers -> simple page, per language
RewriteCond %{QUERY_STRING} !(^|&)full=1
RewriteCond %{HTTP_COOKIE} !vlfull=1
RewriteCond %{HTTP_USER_AGENT} (MSIE\ [1-9]\.|MSIE\ 10|Trident/|Opera\ Mini|Opera/[0-9]\.|UCBrowser/[0-9]\.|KaiOS|Nintendo|PlayStation\ (3|4|Vita|Portable)|BlackBerry|BB10|Windows\ Phone|Symbian|Series60|Android\ [1-4]\.|CPU\ (iPhone\ )?OS\ [1-9]_|Firefox/[1-4][0-9]\.|Chrome/[1-4][0-9]\.) [NC]
RewriteCond %{REQUEST_URI} !lite\.html$
RewriteCond %{REQUEST_URI} \.html$|/$
RewriteRule ^(fr|zh|ar)/ /$1/lite.html [R=302,L]
RewriteCond %{QUERY_STRING} !(^|&)full=1
RewriteCond %{HTTP_COOKIE} !vlfull=1
RewriteCond %{HTTP_USER_AGENT} (MSIE\ [1-9]\.|MSIE\ 10|Trident/|Opera\ Mini|Opera/[0-9]\.|UCBrowser/[0-9]\.|KaiOS|Nintendo|PlayStation\ (3|4|Vita|Portable)|BlackBerry|BB10|Windows\ Phone|Symbian|Series60|Android\ [1-4]\.|CPU\ (iPhone\ )?OS\ [1-9]_|Firefox/[1-4][0-9]\.|Chrome/[1-4][0-9]\.) [NC]
RewriteCond %{REQUEST_URI} !lite\.html$
RewriteCond %{REQUEST_URI} \.html$|/$
RewriteRule ^ /lite.html [R=302,L]
</IfModule>
<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
<FilesMatch "\.(css|js|svg|webp|jpg|png)$">
Header set Cache-Control "public, max-age=604800"
</FilesMatch>
<FilesMatch "\.html$">
Header set Cache-Control "public, max-age=300"
Header append Vary "User-Agent"
</FilesMatch>
</IfModule>
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml
</IfModule>
"""

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    # static
    css = min_css((SITE / 'site.css').read_text())
    write(DIST / 'site.css', css)
    js = (SITE / 'site.js').read_text()
    try:
        import subprocess
        r = subprocess.run(['npx', '--yes', 'terser', '--compress', '--mangle'], input=js, capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and len(r.stdout) > 1000: js = r.stdout
    except Exception: pass
    write(DIST / 'site.js', js)
    shutil.copy(SITE / 'icons.svg', DIST / 'icons.svg')
    shutil.copy(ROOT / 'shared' / 'favicon.svg', DIST / 'favicon.svg')
    (DIST / 'media').mkdir()
    for f in (SITE / 'media').iterdir(): shutil.copy(f, DIST / 'media' / f.name)
    idx = [[k, page_display(Ctx('en', 1), p), S.sec_key(p) if not p.get('hub') else p['hub'], CU.excerpt(p, 90) if not p.get('virtual') else ''] for k, p in S.ALL.items()]
    write(DIST / 'search.js', 'window.VL_INDEX=' + json.dumps(idx, ensure_ascii=False, separators=(',', ':')) + ';')
    n = 0
    for lang in I.LANGS:
        base = DIST if lang == 'en' else DIST / lang
        write(base / 'l10n.js', l10n_js(lang))
        write(base / 'index.html', home(Ctx(lang, 0))); n += 1
        for slug, p in S.ALL.items():
            write(base / 'p' / f'{slug}.html', content_page(Ctx(lang, 1), p)); n += 1
    import lite as LT
    for lang in I.LANGS:
        base = DIST if lang == 'en' else DIST / lang
        write(base / 'lite.html', LT.page(lang, F, V, STORE, LINUX))
    write(DIST / '.htaccess', HTACCESS)
    # redirects from previous option URLs
    for lang in I.LANGS:
        base = DIST if lang == 'en' else DIST / lang
        write(base / 'p' / 'section--developers.html', '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=projects.html"><link rel="canonical" href="projects.html"><title>VideoLAN</title><a href="projects.html">VideoLAN</a>')
    for o in ('a', 'b', 'c'):
        write(DIST / o / 'index.html', '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../index.html"><link rel="canonical" href="../index.html"><title>VideoLAN</title><a href="../index.html">VideoLAN</a>')
    print('pages', n)

if __name__ == '__main__':
    main()
