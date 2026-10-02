# -*- coding: utf-8 -*-
"""Curated, translated landing pages (EN / FR / ZH / AR).
   Each renderer returns body HTML for the content-page shell. Original videolan.org text
   is kept underneath in a collapsible 'complete reference' block, so nothing is lost."""
import re, json, html as H
import vlsite as S
import i18n as I
e = H.escape
LI = {'en': 0, 'fr': 1, 'zh': 2, 'ar': 3}

FACTW = {'All': ('All platforms', 'Toutes plateformes', '全平台', 'كل المنصّات'), 'Desktop': ('Desktop', 'Ordinateur', '桌面端', 'سطح المكتب'), 'Desktop · Mobile · TV': ('Desktop · Mobile · TV', 'Ordinateur · Mobile · TV', '桌面 · 移动 · 电视', 'سطح المكتب · الجوّال · التلفاز')}
def FW(c, v): return P(c, FACTW[v]) if v in FACTW else v
def P(c, x):
    """pick translation from a 4-tuple"""
    return x[LI[c.lang]] if isinstance(x, tuple) else x

# ---------------------------------------------------------------- shared strings
U = {
 'ref': ('Complete reference from videolan.org', 'Référence complète issue de videolan.org', '来自 videolan.org 的完整原文', 'المرجع الكامل من videolan.org'),
 'ref_p': ('The full original text of this page, kept as is.', 'Le texte d’origine complet de cette page, conservé tel quel.', '本页完整原文，未作改动。', 'النص الأصلي الكامل لهذه الصفحة كما هو.'),
 'open': ('Open', 'Ouvrir', '打开', 'افتح'),
 'learn': ('Learn more', 'En savoir plus', '了解更多', 'اعرف المزيد'),
 'code': ('Source code', 'Code source', '源代码', 'الشيفرة المصدرية'),
 'license': ('Licence', 'Licence', '许可证', 'الرخصة'),
 'language': ('Language', 'Langage', '语言', 'اللغة'),
 'platforms': ('Platforms', 'Plateformes', '平台', 'المنصّات'),
 'since': ('Since', 'Depuis', '始于', 'منذ'),
 'filter': ('Filter {n} pages…', 'Filtrer {n} pages…', '筛选 {n} 个页面…', 'صفِّ {n} صفحة…'),
 'filter_news': ('Search {n} stories…', 'Rechercher parmi {n} articles…', '搜索 {n} 条新闻…', 'ابحث في {n} خبرًا…'),
 'no_match': ('Nothing matches. Try another word.', 'Aucun résultat. Essayez un autre mot.', '没有匹配结果，换个词试试。', 'لا نتائج. جرّب كلمة أخرى.'),
 'all': ('All', 'Tout', '全部', 'الكل'),
 'in_section': ('In this section', 'Dans cette rubrique', '本栏目', 'في هذا القسم'),
 'featured': ('Start here', 'Pour commencer', '从这里开始', 'ابدأ من هنا'),
 'everything': ('Everything in {s}', 'Tout dans {s}', '{s} 全部内容', 'كل ما في {s}'),
 'latest': ('Latest', 'À la une', '最新', 'الأحدث'),
 'archive': ('Archive', 'Archives', '归档', 'الأرشيف'),
 'read_story': ('Read the story', 'Lire l’article', '阅读全文', 'اقرأ الخبر'),
 'stories': ('{n} stories', '{n} articles', '{n} 条', '{n} خبرًا'),
 'en_only': ('in English', 'en anglais', '英文', 'بالإنجليزية'),
 'show_more': ('Show more stories', 'Afficher plus d’articles', '显示更多', 'عرض المزيد من الأخبار'),
 'back_news': ('All news', 'Toutes les actualités', '全部新闻', 'كل الأخبار'),
}
NEWS_CATS = [
 ('release', ('Releases', 'Versions', '版本发布', 'الإصدارات')),
 ('libs', ('Libraries', 'Bibliothèques', '开发库', 'المكتبات')),
 ('mobile', ('Mobile', 'Mobile', '移动端', 'الجوّال')),
 ('security', ('Security', 'Sécurité', '安全', 'الأمان')),
 ('events', ('Events', 'Événements', '活动', 'الفعاليات')),
 ('org', ('VideoLAN', 'VideoLAN', 'VideoLAN', 'VideoLAN')),
]
def news_cat(n):
    t = n['title'].lower()
    if re.search(r'secur|vulnerab|advisor|cve', t): return 'security'
    if re.search(r'android|ios|iphone|ipad|apple tv|tvos|windows phone|winrt|uwp|mobile|chromeos|xbox', t): return 'mobile'
    if re.search(r'\blib|dav1d|x264|x262|dvblast|multicat|bitstream|vlmc|vlma|libvlc', t): return 'libs'
    if re.search(r'vlc\s*\d|vlc media player \d|release|\d+\.\d+\.\d+', t): return 'release'
    if re.search(r'dev days|vdd|fosdem|conference|event|meeting|summer of code|gsoc|ces|meetup|award', t): return 'events'
    return 'org'

def ref_block(c, p):
    if not p or not p.get('html'): return ''
    body = S.rewrite(p['html'])
    return (f'<details class="refx"><summary><span>{c.ico("book")}<b>{e(P(c, U["ref"]))}</b><small>{e(P(c, U["ref_p"]))}</small></span>{c.ico("chev")}</summary>'
            f'<div class="prose" lang="en" dir="ltr">{body}</div></details>')

def hero_kpis(items):
    return '<div class="kpis">' + ''.join(f'<div class="rv d{i % 3}"><b>{e(a)}</b><span>{e(b)}</span></div>' for i, (a, b) in enumerate(items)) + '</div>'

# ---------------------------------------------------------------- illustrations (inline SVG, animated under html.fx)
def illo(kind):
    if kind == 'cone':
        return '<svg class="il il-cone" viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="62" r="46" class="il-ring"/><g class="il-bob"><path class="co" d="M53 22c1.6-4.7 12.4-4.7 14 0l22 66H31z"/><path class="cw" d="M47.2 42h25.6l3 10H44.2zM40.9 62h38.2l3.3 11H37.6z"/><rect class="co" x="24" y="86" width="72" height="12" rx="5"/></g></svg>'
    if kind == 'tiles':
        cells = ''.join(f'<rect x="{12 + (i % 6) * 16}" y="{20 + (i // 6) * 16}" width="14" height="14" rx="3" style="--i:{i}"/>' for i in range(30))
        return f'<svg class="il il-tiles" viewBox="0 0 120 120" aria-hidden="true">{cells}</svg>'
    if kind == 'waves':
        return '<svg class="il il-waves" viewBox="0 0 120 120" aria-hidden="true"><path d="M60 92V54"/><path d="M48 98h24"/><circle cx="60" cy="48" r="6" class="f"/><path class="w w1" d="M44 34a22 22 0 0 1 32 0"/><path class="w w2" d="M34 24a36 36 0 0 1 52 0"/><path class="w w3" d="M24 14a50 50 0 0 1 72 0"/></svg>'
    if kind == 'disc':
        return '<svg class="il il-disc" viewBox="0 0 120 120" aria-hidden="true"><g class="spin"><circle cx="60" cy="60" r="44"/><circle cx="60" cy="60" r="30" class="g"/><circle cx="60" cy="60" r="10" class="h"/><path d="M60 16a44 44 0 0 1 38 22" class="shine"/></g></svg>'
    if kind == 'stack':
        return '<svg class="il il-stack" viewBox="0 0 120 120" aria-hidden="true"><g style="--i:0"><rect x="22" y="78" width="76" height="16" rx="5"/></g><g style="--i:1"><rect x="22" y="56" width="76" height="16" rx="5"/></g><g style="--i:2"><rect x="22" y="34" width="76" height="16" rx="5" class="o"/></g><text x="60" y="46" text-anchor="middle">libVLC</text></svg>'
    if kind == 'film':
        return '<svg class="il il-film" viewBox="0 0 120 120" aria-hidden="true"><rect x="14" y="30" width="92" height="60" rx="8"/><g class="trk"><rect x="22" y="44" width="34" height="10" rx="3" class="o"/><rect x="60" y="44" width="38" height="10" rx="3"/><rect x="22" y="62" width="52" height="10" rx="3"/><rect x="78" y="62" width="20" height="10" rx="3" class="o"/></g><path d="M50 36v48" class="head"/></svg>'
    if kind == 'streams':
        return '<svg class="il il-streams" viewBox="0 0 120 120" aria-hidden="true"><path d="M16 40h88M16 60h88M16 80h88"/><circle r="5" class="p p1" cy="40"/><circle r="5" class="p p2" cy="60"/><circle r="5" class="p p3" cy="80"/></svg>'
    if kind == 'brackets':
        return '<svg class="il il-code" viewBox="0 0 120 120" aria-hidden="true"><path d="M44 36 22 60l22 24M76 36l22 24-22 24"/><path d="M66 30 54 90" class="o"/></svg>'
    return ''

# ================================================================= FEATURES
FEAT = [
 ('film', ('Plays everything', 'Lit tout', '万物皆可播', 'يشغّل كل شيء'),
  ('Files, discs, webcams, devices and streams. VLC brings its own codecs, so there is nothing else to install.', 'Fichiers, disques, webcams, périphériques et flux. VLC embarque ses propres codecs : rien d’autre à installer.', '文件、光盘、摄像头、设备和网络流。VLC 自带解码器，无需另装任何东西。', 'ملفات وأقراص وكاميرات وأجهزة وبثّ. يأتي VLC بمرمّزاته الخاصة، فلا حاجة لتثبيت أي شيء آخر.'),
  ['MKV · MP4 · AVI · MOV · OGG · FLAC · TS · M2TS · WebM', 'DVD · Blu-ray · Audio CD · VCD', 'HEVC · AV1 · VP9 · H.264 · ProRes · DNxHD', 'Opus · AAC · FLAC · ALAC · DTS · TrueHD · ATRAC']),
 ('gauge', ('Fast, on any hardware', 'Rapide, sur tout matériel', '任何硬件都流畅', 'سريع على أي عتاد'),
  ('Hardware decoding on every platform, with zero-copy on the GPU and a software fallback when needed.', 'Décodage matériel sur toutes les plateformes, zéro copie sur le GPU et repli logiciel si nécessaire.', '各平台均支持硬件解码，GPU 零拷贝，必要时自动回退到软件解码。', 'فك ترميز عتادي على كل المنصّات، دون نسخ على المعالج الرسومي، مع بديل برمجي عند الحاجة.'),
  ['DXVA2 · D3D11 · VA-API · VDPAU · VideoToolbox · MediaCodec', '4K · 8K · HDR10 · HLG · 10-bit', 'HDR to SDR tone mapping']),
 ('cc', ('Subtitles that land on time', 'Des sous-titres au bon moment', '字幕精准同步', 'ترجمة في وقتها تمامًا'),
  ('All the common formats, closed captions and teletext. Shift them with G and H, or let VLC fetch them.', 'Tous les formats courants, sous-titres codés et télétexte. Décalez-les avec G et H, ou laissez VLC les trouver.', '支持所有常见字幕格式、隐藏字幕和图文电视。用 G 和 H 微调，或让 VLC 自动下载。', 'كل الصيغ الشائعة والتعليقات المغلقة والنصوص التلفزيونية. حرّكها بالمفتاحين G وH، أو دع VLC يجلبها.'),
  ['SRT · ASS/SSA · WebVTT · TTML · DVB · VobSub', 'CEA-608 · CEA-708 · Teletext', 'Two subtitle tracks at once']),
 ('stream', ('Networks and streams', 'Réseaux et flux', '网络与串流', 'الشبكات والبث'),
  ('Open any URL, browse shares on your network, stream to another screen or broadcast your own.', 'Ouvrez n’importe quelle URL, parcourez les partages de votre réseau, diffusez vers un autre écran ou créez votre propre flux.', '打开任意网址，浏览局域网共享，投屏到其他屏幕，或自己推流。', 'افتح أي رابط، وتصفّح المشاركات على شبكتك، وابثّ إلى شاشة أخرى أو أنشئ بثّك الخاص.'),
  ['HLS · DASH · RTSP · RTP · SRT · RIST · UDP multicast', 'SMB · NFS · FTP · SFTP · UPnP/DLNA', 'Chromecast · AirPlay audio (macOS)']),
 ('volume', ('Audio done right', 'Un son impeccable', '出色的音频', 'صوت كما يجب'),
  ('A 10-band equaliser, compressor, spatialiser and passthrough of HD audio to your receiver.', 'Égaliseur 10 bandes, compresseur, spatialiseur et passage direct de l’audio HD vers votre ampli.', '10 段均衡器、压缩器、空间化处理，并可将高清音频直通至功放。', 'معادل صوت بعشرة نطاقات، وضاغط، ومجسّم صوتي، وتمرير مباشر للصوت عالي الدقة إلى جهاز الاستقبال.'),
  ['S/PDIF · HDMI passthrough (DD+, TrueHD, DTS-HD)', 'Ambisonics · 3D audio', 'Pitch-preserving speed']),
 ('sliders', ('Video filters', 'Filtres vidéo', '视频滤镜', 'مرشّحات الفيديو'),
  ('Deinterlace, crop, rotate, sharpen, adjust colours, add a logo or a mosaic. All live, while you watch.', 'Désentrelacement, recadrage, rotation, netteté, couleurs, logo ou mosaïque. En direct, pendant la lecture.', '去隔行、裁剪、旋转、锐化、调色、加台标或马赛克，边看边调。', 'إزالة التشابك، والقص، والتدوير، والحدّة، وضبط الألوان، وإضافة شعار أو فسيفساء. كلها مباشرة أثناء المشاهدة.'),
  ['360° video navigation', 'Video wall and mosaic', 'Snapshots and A-B loop']),
 ('convert', ('Convert and record', 'Convertir et enregistrer', '转换与录制', 'التحويل والتسجيل'),
  ('Turn any file into MP4, WebM or MP3, record a stream, capture your desktop or webcam.', 'Transformez un fichier en MP4, WebM ou MP3, enregistrez un flux, capturez votre bureau ou votre webcam.', '把任意文件转为 MP4、WebM 或 MP3，录制网络流，采集桌面或摄像头。', 'حوّل أي ملف إلى MP4 أو WebM أو MP3، وسجّل بثًا، والتقط سطح المكتب أو الكاميرا.'),
  ['Media › Convert / Save', 'Screen and webcam capture', 'Stream output wizard']),
 ('palette', ('Make it yours', 'À votre image', '随心定制', 'خصّصه كما تشاء'),
  ('Skins, extensions and Lua scripts. Every shortcut can be remapped.', 'Skins, extensions et scripts Lua. Chaque raccourci est personnalisable.', '皮肤、扩展与 Lua 脚本，所有快捷键均可自定义。', 'سمات وإضافات وسكربتات Lua، ويمكن تخصيص كل اختصار.'),
  ['Skin editor', 'Lua extensions and playlist parsers', 'Web, telnet and HTTP remote control']),
 ('shield', ('Private by design', 'Respect de la vie privée', '隐私至上', 'الخصوصية أولًا'),
  ('No ads, no tracking, no account. Your media and your history stay on your device.', 'Ni publicité, ni pistage, ni compte. Vos médias et votre historique restent chez vous.', '无广告、无追踪、无需账号。你的媒体和观看记录只留在你的设备上。', 'بلا إعلانات ولا تتبّع ولا حساب. وسائطك وسجلّك يبقيان على جهازك.'),
  ['Open source, GPLv2', 'Signed updates (RSA-4096)', 'No telemetry']),
]
FEAT_H = (('Everything VLC can do', 'Tout ce que fait VLC', 'VLC 能做的一切', 'كل ما يستطيعه VLC'),
          ('Simple on the surface, deep underneath. Here is what is inside the cone.', 'Simple en surface, très riche en profondeur. Voici ce que contient le cône.', '外表简洁，内里强大。来看看这个路锥里都有什么。', 'بسيط في الظاهر، عميق في الداخل. إليك ما يحمله المخروط.'))
KB = [('Space', ('Play / pause', 'Lecture / pause', '播放 / 暂停', 'تشغيل / إيقاف مؤقت')), ('F', ('Full screen', 'Plein écran', '全屏', 'ملء الشاشة')),
      ('[ ]', ('Slower / faster', 'Plus lent / plus rapide', '减速 / 加速', 'أبطأ / أسرع')), ('G H', ('Subtitle delay', 'Décalage des sous-titres', '字幕延迟', 'تأخير الترجمة')),
      ('J K', ('Audio delay', 'Décalage audio', '音频延迟', 'تأخير الصوت')), ('V', ('Next subtitle track', 'Piste de sous-titres suivante', '切换字幕轨道', 'مسار الترجمة التالي')),
      ('B', ('Next audio track', 'Piste audio suivante', '切换音轨', 'مسار الصوت التالي')), ('E', ('Next frame', 'Image suivante', '下一帧', 'الإطار التالي'))]
KB_H = ('Keyboard shortcuts worth knowing', 'Les raccourcis à connaître', '值得记住的快捷键', 'اختصارات تستحق الحفظ')

def features(c, p):
    h = [f'<p class="x-lede">{e(P(c, FEAT_H[1]))}</p><div class="fgrid">']
    for i, (ic, t, d, chips) in enumerate(FEAT):
        h.append(f'<article class="fcard glow rv d{i % 3}"><span class="fic">{c.ico(ic)}</span><h2>{e(P(c, t))}</h2><p>{e(P(c, d))}</p><ul class="chips" dir="ltr">{"".join(f"<li>{e(x)}</li>" for x in chips)}</ul></article>')
    h.append('</div>')
    h.append(f'<section class="kbs rv"><h2>{c.ico("keyboard")}{e(P(c, KB_H))}</h2><div class="kbg">' + ''.join(f'<div><span dir="ltr">{"".join(f"<kbd>{e(k)}</kbd>" for k in ks.split())}</span><b>{e(P(c, l))}</b></div>' for ks, l in KB) + '</div></section>')
    h.append(f'<div class="ctas"><a class="btn btn-or" href="download.html">{c.ico("download")}{e(c.t("cta_download"))}</a><a class="btn btn-gh" href="vlc--screenshots.html">{c.ico("monitor")}Screenshots</a><a class="btn btn-gh" href="vlc--skins.html">{c.ico("palette")}{e(c.t("ft_skins"))}</a></div>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= PROJECTS
PJ = [
 # slug, name, illo, group, tagline, facts(lang, licence, platforms, since), code url
 ('vlc', 'VLC media player', 'cone', 'everyone',
  ('The free, cross-platform player that plays just about anything, used by hundreds of millions of people.', 'Le lecteur libre et multiplateforme qui lit à peu près tout, utilisé par des centaines de millions de personnes.', '免费、跨平台、几乎什么都能播的播放器，全球数亿人在用。', 'المشغّل الحر متعدد المنصّات الذي يشغّل كل شيء تقريبًا، ويستخدمه مئات الملايين.'),
  ('C · C++ · Qt', 'GPLv2', 'Windows · macOS · Linux · Android · iOS', '2001'), 'https://code.videolan.org/videolan/vlc'),
 ('vlc--libvlc', 'libVLC', 'stack', 'dev',
  ('VLC’s engine as a library. Embed playback, streaming and conversion in your own app, with bindings for most languages.', 'Le moteur de VLC en bibliothèque. Intégrez lecture, diffusion et conversion à votre application, avec des liaisons pour la plupart des langages.', '把 VLC 的引擎作为库使用。在你的应用中嵌入播放、串流和转码，支持大多数编程语言。', 'محرّك VLC على شكل مكتبة. أضف التشغيل والبث والتحويل إلى تطبيقك، مع روابط لمعظم لغات البرمجة.'),
  ('C', 'LGPL 2.1', 'Desktop · Mobile · TV', '2008'), 'https://code.videolan.org/videolan/vlc'),
 ('projects--dav1d', 'dav1d', 'tiles', 'dev',
  ('The fast, small AV1 decoder built with the FFmpeg community and the Alliance for Open Media, shipped in major browsers and systems.', 'Le décodeur AV1 rapide et compact, conçu avec la communauté FFmpeg et l’Alliance for Open Media, intégré aux grands navigateurs et systèmes.', '与 FFmpeg 社区和开放媒体联盟共同打造的快速、小巧的 AV1 解码器，已进入主流浏览器和操作系统。', 'مفكّك AV1 السريع والصغير، طُوِّر مع مجتمع FFmpeg وتحالف الوسائط المفتوحة، ويعمل في كبرى المتصفحات والأنظمة.'),
  ('C · Assembly', 'BSD 2-clause', 'All', '2018'), 'https://code.videolan.org/videolan/dav1d'),
 ('developers--x264', 'x264', 'tiles', 'pro',
  ('The reference H.264/AVC encoder: best-in-class quality and speed, behind a huge share of online video.', 'L’encodeur H.264/AVC de référence : qualité et vitesse inégalées, derrière une immense part de la vidéo en ligne.', '业界标杆级 H.264/AVC 编码器，质量与速度一流，支撑着大量在线视频。', 'مرمّز H.264/AVC المرجعي: جودة وسرعة لا مثيل لهما، ويقف خلف جزء كبير من الفيديو على الإنترنت.'),
  ('C · Assembly', 'GPLv2', 'All', '2004'), 'https://code.videolan.org/videolan/x264'),
 ('projects--dvblast', 'DVBlast', 'waves', 'pro',
  ('A lean MPEG-2/TS demux and streaming app for DVB and ATSC, built for extreme memory and CPU limits.', 'Un démultiplexeur et diffuseur MPEG-2/TS léger pour DVB et ATSC, conçu pour des contraintes mémoire et CPU extrêmes.', '面向 DVB 与 ATSC 的轻量 MPEG-2/TS 解复用与串流程序，为极低内存和 CPU 环境而生。', 'أداة خفيفة لفصل وبثّ MPEG-2/TS لأنظمة DVB وATSC، مصمّمة لأقسى قيود الذاكرة والمعالج.'),
  ('C', 'GPLv2', 'Linux', '2008'), 'https://code.videolan.org/videolan/dvblast'),
 ('projects--multicat', 'multicat', 'streams', 'pro',
  ('Small tools to record, replay and manipulate multicast streams and MPEG transport streams.', 'De petits outils pour enregistrer, rejouer et manipuler les flux multicast et les flux de transport MPEG.', '用于录制、回放和处理组播流及 MPEG 传输流的小工具集。', 'أدوات صغيرة لتسجيل تدفقات البث المتعدد ونقل MPEG وإعادة تشغيلها ومعالجتها.'),
  ('C', 'GPLv2', 'Linux · Unix', '2009'), 'https://code.videolan.org/videolan/multicat'),
 ('vlmc', 'VLMC', 'film', 'everyone',
  ('VideoLAN Movie Creator, a non-linear video editor built on libVLC. Still in development.', 'VideoLAN Movie Creator, un logiciel de montage non linéaire basé sur libVLC. Encore en développement.', 'VideoLAN Movie Creator，基于 libVLC 的非线性视频剪辑软件，仍在开发中。', 'VideoLAN Movie Creator، محرّر فيديو غير خطّي مبني على libVLC، ولا يزال قيد التطوير.'),
  ('C++ · Qt', 'GPLv2', 'Windows · macOS · Linux', '2008'), 'https://code.videolan.org/videolan/vlmc'),
 ('developers--libdvdcss', 'libdvdcss', 'disc', 'dev',
  ('The reference open source library for accessing DVDs.', 'La bibliothèque libre de référence pour lire les DVD.', '访问 DVD 的开源参考库。', 'المكتبة المفتوحة المرجعية للوصول إلى أقراص DVD.'), ('C', 'GPLv2', 'All', '2001'), 'https://code.videolan.org/videolan/libdvdcss'),
 ('developers--libdvdnav', 'libdvdnav · libdvdread', 'disc', 'dev',
  ('DVD menus and DVD-Video images, done right.', 'Les menus DVD et les images DVD-Vidéo, bien gérés.', '完整处理 DVD 菜单与 DVD-Video 镜像。', 'قوائم DVD وصور DVD-Video بشكل صحيح.'), ('C', 'GPLv2', 'All', '2002'), 'https://code.videolan.org/videolan/libdvdnav'),
 ('developers--libbluray', 'libbluray', 'disc', 'dev',
  ('Blu-ray disc access, playlists, menus and BD-J.', 'Accès aux disques Blu-ray, playlists, menus et BD-J.', '蓝光光盘访问、播放列表、菜单与 BD-J。', 'الوصول إلى أقراص Blu-ray وقوائم التشغيل والقوائم وBD-J.'), ('C', 'LGPL 2.1', 'All', '2009'), 'https://code.videolan.org/videolan/libbluray'),
 ('developers--libaacs', 'libaacs · libbdplus', 'disc', 'dev',
  ('Research libraries implementing the AACS and BD+ standards.', 'Bibliothèques de recherche implémentant les normes AACS et BD+.', '实现 AACS 与 BD+ 标准的研究型库。', 'مكتبات بحثية تطبّق معياري AACS وBD+.'), ('C', 'LGPL 2.1', 'All', '2010'), 'https://code.videolan.org/videolan/libaacs'),
 ('developers--libdvbpsi', 'libdvbpsi', 'brackets', 'dev',
  ('Decode and generate MPEG TS and DVB PSI tables without headaches.', 'Décoder et générer les tables MPEG TS et DVB PSI, sans prise de tête.', '轻松解码与生成 MPEG TS 和 DVB PSI 表。', 'فك وتوليد جداول MPEG TS وDVB PSI دون عناء.'), ('C', 'LGPL 2.1', 'All', '2001'), 'https://code.videolan.org/videolan/libdvbpsi'),
 ('developers--bitstream', 'biTStream', 'brackets', 'dev',
  ('Header-only C access to MPEG, DVB, IETF and SMPTE binary structures.', 'Accès en C, sous forme d’en-têtes, aux structures binaires MPEG, DVB, IETF et SMPTE.', '纯头文件的 C 库，访问 MPEG、DVB、IETF、SMPTE 等二进制结构。', 'ترويسات C للوصول إلى البنى الثنائية لمعايير MPEG وDVB وIETF وSMPTE.'), ('C', 'MIT', 'All', '2010'), 'https://code.videolan.org/videolan/bitstream'),
 ('developers--libdvbcsa', 'libdvbcsa', 'brackets', 'dev',
  ('Encrypt and decrypt with the DVB Common Scrambling Algorithm.', 'Chiffrer et déchiffrer avec l’algorithme DVB-CSA.', '使用 DVB 通用加扰算法进行加解密。', 'التشفير وفكّه بخوارزمية DVB-CSA.'), ('C', 'GPLv2', 'All', '2008'), 'https://code.videolan.org/videolan/libdvbcsa'),
 ('developers--libdca', 'libdca', 'brackets', 'dev',
  ('A decoder for DTS Coherent Acoustics audio.', 'Un décodeur audio DTS Coherent Acoustics.', 'DTS Coherent Acoustics 音频解码器。', 'مفكّك صوت DTS Coherent Acoustics.'), ('C', 'GPLv2', 'All', '2004'), 'https://code.videolan.org/videolan/libdca'),
 ('projects--vlma', 'VLMa', 'waves', 'pro',
  ('Manage TV broadcasts from satellite and terrestrial sources through a web interface. No longer maintained.', 'Gérez des diffusions TV satellite et terrestres depuis une interface web. N’est plus maintenu.', '通过网页界面管理卫星和地面电视广播。已停止维护。', 'إدارة البث التلفزيوني الفضائي والأرضي عبر واجهة ويب. لم يعد يُحدَّث.'), ('Java', 'GPL', 'Linux', '2006'), ''),
]
PJ_GROUPS = [('everyone', ('For everyone', 'Pour tout le monde', '面向所有人', 'للجميع'), ('Apps you can install today.', 'Des applications à installer dès aujourd’hui.', '今天就能安装的应用。', 'تطبيقات يمكنك تثبيتها اليوم.')),
             ('pro', ('For broadcasters and professionals', 'Pour les diffuseurs et les professionnels', '面向广电与专业人士', 'للمذيعين والمحترفين'), ('Encoding and streaming tools that run TV networks and studios.', 'Des outils d’encodage et de diffusion qui font tourner chaînes et studios.', '支撑电视网络和演播室的编码与串流工具。', 'أدوات ترميز وبثّ تشغّل شبكات التلفزيون والاستوديوهات.')),
             ('dev', ('For developers', 'Pour les développeurs', '面向开发者', 'للمطوّرين'), ('Libraries you can build on, from codecs to disc access.', 'Des bibliothèques sur lesquelles bâtir, des codecs à l’accès aux disques.', '可在其上构建的库，从编解码器到光盘访问。', 'مكتبات تبني عليها، من المرمّزات إلى الوصول إلى الأقراص.'))]
PJ_H = ('Two decades of open multimedia, all under one roof.', 'Vingt ans de multimédia libre, sous un même toit.', '二十余年的开源多媒体成果，尽在一处。', 'عقدان من الوسائط المفتوحة تحت سقف واحد.')

def projects(c, p):
    h = [f'<p class="x-lede">{e(P(c, PJ_H))}</p>', hero_kpis([(str(len(PJ)), P(c, ('projects', 'projets', '个项目', 'مشروعًا'))), ('25+', P(c, ('years', 'ans', '年', 'عامًا'))), ('GPL · LGPL · BSD · MIT', P(c, ('open licences', 'licences libres', '开源许可', 'رخص مفتوحة')))])]
    h.append(f'<div class="ntools" data-pfilter><span class="sbox">{c.ico("search")}<input class="srch" type="search" autocomplete="off" placeholder="{e(P(c, DU["find"]))}" aria-label="{e(P(c, DU["find"]))}"></span></div>')
    h.append('<nav class="jump">' + ''.join(f'<a href="#g-{g}">{e(P(c, t))}</a>' for g, t, _ in PJ_GROUPS) + f'<a href="#g-res">{e(P(c, DU["res"]))}</a><a href="#g-arch">{e(P(c, DU["arch"]))}</a></nav>')
    for g, gt, gd in PJ_GROUPS:
        items = [x for x in PJ if x[3] == g]
        h.append(f'<section class="pgrp" id="g-{g}"><h2>{e(P(c, gt))}</h2><p class="gd">{e(P(c, gd))}</p><div class="pgrid">')
        for i, (slug, name, il, _, tag, facts, code) in enumerate(items):
            big = ' big' if i < 2 else ''
            fl = [(P(c, U['language']), facts[0]), (P(c, U['license']), facts[1]), (P(c, U['platforms']), FW(c, facts[2])), (P(c, U['since']), facts[3])]
            links = (f'<a class="btn btn-or btn-sm" href="{slug}.html">{e(P(c, U["learn"]))}{c.ico("arrow", "ic flip")}</a>' if slug in S.ALL else '') + (f'<a class="btn btn-gh btn-sm" href="{code}">{c.ico("git")}{e(P(c, U["code"]))}</a>' if code else '')
            h.append(f'<article class="pcard glow rv d{i % 3}{big}" data-q="{e((name + " " + P(c, tag) + " " + " ".join(facts)).lower())}"><div class="pill">{illo(il)}</div><div class="pbody"><h3 dir="ltr">{e(name)}</h3><p>{e(P(c, tag))}</p>'
                     f'<dl class="facts">{"".join(f"<div><dt>{e(a)}</dt><dd dir=ltr>{e(b)}</dd></div>" for a, b in fl)}</dl><div class="plinks">{links}</div></div></article>')
        h.append('</div></section>')
    h.append(projects_extra(c))
    h.append(f'<p class="wall-empty" hidden>{e(P(c, U["no_match"]))}</p>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= TEAM
BOARD = [
 ('Jean-Baptiste Kempf', ('President', 'Président', '主席', 'الرئيس'), 'jbk', ('Leads VideoLAN and has maintained VLC for over fifteen years. Co-founder of Videolabs.', 'Dirige VideoLAN et maintient VLC depuis plus de quinze ans. Cofondateur de Videolabs.', '领导 VideoLAN，维护 VLC 逾十五年，Videolabs 联合创始人。', 'يقود VideoLAN ويشرف على VLC منذ أكثر من خمسة عشر عامًا. شارك في تأسيس Videolabs.')),
 ('Konstantin Pavlov', ('Vice President', 'Vice-président', '副主席', 'نائب الرئيس'), '', ('Keeps VideoLAN’s infrastructure and release machinery running.', 'Fait tourner l’infrastructure et la chaîne de publication de VideoLAN.', '维护 VideoLAN 的基础设施与发布流程。', 'يحافظ على عمل البنية التحتية وآلية الإصدارات في VideoLAN.')),
 ('Vibhoothi', ('Vice President, events', 'Vice-président, événements', '副主席（活动）', 'نائب الرئيس للفعاليات'), '', ('Organises VideoLAN Dev Days and the project’s presence at conferences.', 'Organise les VideoLAN Dev Days et la présence du projet dans les conférences.', '负责组织 VideoLAN 开发者大会及各类会议参与。', 'ينظّم أيام مطوّري VideoLAN وحضور المشروع في المؤتمرات.')),
 ('Thomas Guillem', ('Treasurer', 'Trésorier', '财务主管', 'أمين الصندوق'), '', ('Core developer of VLC and libVLC, and keeper of the accounts.', 'Développeur principal de VLC et libVLC, et gardien des comptes.', 'VLC 与 libVLC 核心开发者，兼管账目。', 'مطوّر أساسي في VLC وlibVLC، ومسؤول الحسابات.')),
 ('Felix Paul Kühne', ('Secretary', 'Secrétaire', '秘书', 'أمين السر'), '', ('Leads VLC on Apple platforms: macOS, iOS, tvOS and visionOS.', 'Dirige VLC sur les plateformes Apple : macOS, iOS, tvOS et visionOS.', '负责 Apple 平台上的 VLC：macOS、iOS、tvOS 与 visionOS。', 'يقود VLC على منصّات Apple: macOS وiOS وtvOS وvisionOS.')),
]
TEAM_T = {
 'lede': ('VLC is made by volunteers and developers from more than 40 countries, together with former students of École Centrale Paris where it all began.', 'VLC est fait par des bénévoles et des développeurs de plus de 40 pays, avec d’anciens élèves de l’École Centrale Paris, où tout a commencé.', 'VLC 由来自 40 多个国家的志愿者和开发者打造，还有当年项目起步的巴黎中央理工学院的校友。', 'يصنع VLC متطوّعون ومطوّرون من أكثر من 40 دولة، مع خرّيجي المدرسة المركزية في باريس حيث بدأ كل شيء.'),
 'board': ('The board', 'Le bureau', '理事会', 'مجلس الإدارة'),
 'board_p': ('VideoLAN is a non-profit association under French law. Its board is elected by its members.', 'VideoLAN est une association loi 1901. Son bureau est élu par ses membres.', 'VideoLAN 是依法国法律成立的非营利协会，理事会由会员选举产生。', 'VideoLAN جمعية غير ربحية وفق القانون الفرنسي، ينتخب أعضاؤها مجلس إدارتها.'),
 'photo': ('VideoLAN Dev Days 2014, Dublin', 'VideoLAN Dev Days 2014, Dublin', '2014 年 VideoLAN 开发者大会，都柏林', 'أيام مطوّري VideoLAN 2014، دبلن'),
 'people': ('The people behind VLC', 'Les personnes derrière VLC', 'VLC 背后的人们', 'الأشخاص وراء VLC'),
 'people_p': ('Everyone credited in VLC’s own list of contributors. Search for a name.', 'Toutes les personnes créditées dans la liste officielle des contributeurs de VLC. Cherchez un nom.', 'VLC 官方贡献者名单中的每一位。可搜索姓名。', 'كل من ورد اسمه في قائمة المساهمين الرسمية لـ VLC. ابحث عن اسم.'),
 'prog': ('Code', 'Code', '代码', 'البرمجة'), 'art': ('Artwork', 'Graphisme', '美术', 'التصميم'), 'doc': ('Documentation', 'Documentation', '文档', 'التوثيق'), 'loc': ('Translation', 'Traduction', '翻译', 'الترجمة'),
 'search': ('Search {n} contributors…', 'Rechercher parmi {n} contributeurs…', '搜索 {n} 位贡献者…', 'ابحث بين {n} مساهمًا…'),
 'join': ('Want your name here?', 'Envie de voir votre nom ici ?', '想让你的名字出现在这里吗？', 'تريد أن يظهر اسمك هنا؟'),
 'join_p': ('Code, translations, documentation, design and support all count.', 'Code, traductions, documentation, design et assistance : tout compte.', '代码、翻译、文档、设计和用户支持，都算贡献。', 'البرمجة والترجمة والتوثيق والتصميم والدعم، كلها مساهمات.'),
 'credit': ('Portrait: Axelle Manfrini, CC BY-SA 4.0, via Wikimedia Commons.', 'Portrait : Axelle Manfrini, CC BY-SA 4.0, via Wikimedia Commons.', '肖像：Axelle Manfrini，CC BY-SA 4.0，来自 Wikimedia Commons。', 'الصورة: Axelle Manfrini، برخصة CC BY-SA 4.0، عبر Wikimedia Commons.'),
}
def team_lists():
    h = S.PAGES['videolan--team']['html']
    t = re.sub(r'<[^>]+>', '\n', h); L = [x.strip() for x in t.split('\n') if x.strip()]
    out = {}; cur = None
    for i, x in enumerate(L):
        if i + 1 < len(L) and set(L[i + 1]) <= set('-') and x in ('Programming', 'Artwork', 'Documentation', 'Localization'):
            cur = x; out[cur] = []; continue
        if set(x) <= set('-'): continue
        if x in ('Contacting us', 'See the'): cur = None
        if cur: out[cur].append(x)
    return out
def initials(n):
    p = [w for w in re.split(r'[\s-]+', n) if w and w[0].isalpha()]
    return (p[0][0] + (p[-1][0] if len(p) > 1 else '')).upper()

def team(c, p):
    T = lambda k, **kw: P(c, TEAM_T[k]).replace("{n}", str(kw.get("n", "")))
    L = team_lists()
    h = [f'<p class="x-lede">{e(T("lede"))}</p>']
    h.append(f'<figure class="gphoto rv"><picture><source type="image/webp" srcset="{c.root}media/vdd14.webp"><img src="{c.root}media/vdd14.jpg" width="750" height="287" alt="{e(T("photo"))}" loading="lazy"></picture><figcaption>{c.ico("camera")}{e(T("photo"))}</figcaption></figure>')
    h.append(hero_kpis([(str(len(L.get('Programming', []))), T('prog')), (str(len(L.get('Localization', []))), T('loc')), ('40+', P(c, ('countries', 'pays', '个国家', 'دولة'))), ('1996', P(c, ('first line of code', 'première ligne de code', '第一行代码', 'أول سطر برمجي')))]))
    h.append(f'<section class="tsec"><h2>{e(T("board"))}</h2><p class="gd">{e(T("board_p"))}</p><div class="board">')
    for i, (n, role, ph, bio) in enumerate(BOARD):
        av = (f'<picture><source type="image/webp" srcset="{c.root}media/jbk-480.webp"><img src="{c.root}media/jbk-480.jpg" width="480" height="600" alt="{e(n)}" loading="lazy"></picture>' if ph else f'<span class="ini" aria-hidden="true">{initials(n)}</span>')
        h.append(f'<article class="person rv d{i % 3}{" lead" if ph else ""}"><div class="av">{av}</div><div><p class="role">{e(P(c, role))}</p><h3 dir="ltr">{e(n)}</h3><p>{e(P(c, bio))}</p></div></article>')
    h.append(f'</div><p class="credit">{e(T("credit"))}</p></section>')
    tabs = [('Programming', 'prog'), ('Localization', 'loc'), ('Artwork', 'art'), ('Documentation', 'doc')]
    total = sum(len(L.get(k, [])) for k, _ in tabs)
    h.append(f'<section class="tsec"><h2>{e(T("people"))}</h2><p class="gd">{e(T("people_p"))}</p>'
             f'<div class="wall" data-wall><div class="wall-bar"><label class="sr" for="wq">{e(T("search", n=total))}</label><input class="srch" id="wq" type="search" placeholder="{e(T("search", n=total))}" autocomplete="off">'
             '<div class="chipsel" role="group">' + ''.join(f'<button type="button" data-g="{k}" aria-pressed="{"true" if k == "Programming" else "false"}">{e(T(l))} <small>{len(L.get(k, []))}</small></button>' for k, l in tabs) + '</div></div>')
    for k, _ in tabs:
        h.append(f'<ul class="names" tabindex="0" aria-label="{e(k)}" data-names="{k}"{"" if k == "Programming" else " hidden"} dir="auto">' + ''.join(f'<li><span class="ini sm" aria-hidden="true">{e(initials(x) or "·")}</span>{e(x)}</li>' for x in L.get(k, [])) + '</ul>')
    h.append(f'<p class="wall-empty" hidden>{e(P(c, U["no_match"]))}</p></div></section>')
    h.append(f'<div class="dband rv"><div><h2>{e(T("join"))}</h2><p>{e(T("join_p"))}</p></div><div><a class="btn btn-or" href="contribute.html">{c.ico("users")}{e(c.t("nav_contribute"))}</a></div></div>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= ABOUT (videolan)
AB = {
 'lede': ('VideoLAN is a project and a non-profit organisation, run by volunteers who believe in the power of open source to rock the multimedia world.', 'VideoLAN est un projet et une association à but non lucratif, portés par des bénévoles convaincus que le logiciel libre peut changer le monde du multimédia.', 'VideoLAN 既是一个项目，也是一个非营利组织，由坚信开源能改变多媒体世界的志愿者们运营。', 'VideoLAN مشروع ومنظمة غير ربحية، يديرها متطوّعون يؤمنون بقدرة المصادر المفتوحة على تغيير عالم الوسائط.'),
 'v1': ('Independent', 'Indépendant', '独立', 'مستقل'), 'v1p': ('No investors and no company behind it. Since 2009 an autonomous association under French law.', 'Ni investisseurs ni entreprise derrière. Une association autonome de droit français depuis 2009.', '没有投资人，也没有公司在背后。自 2009 年起为依法国法律设立的独立协会。', 'بلا مستثمرين ولا شركة خلفه. جمعية مستقلة وفق القانون الفرنسي منذ 2009.'),
 'v2': ('Open', 'Libre', '开放', 'مفتوح'), 'v2p': ('Every line of code is free software, released under the GPL and LGPL.', 'Chaque ligne de code est un logiciel libre, publiée sous GPL et LGPL.', '每一行代码都是自由软件，以 GPL 和 LGPL 发布。', 'كل سطر برمجي برمجيات حرّة، منشورة برخص GPL وLGPL.'),
 'v3': ('Private', 'Respectueux', '尊重隐私', 'يحترم خصوصيتك'), 'v3p': ('No ads, no tracking, no data sold. Not now, not ever.', 'Pas de publicité, pas de pistage, aucune donnée vendue. Ni aujourd’hui, ni demain.', '没有广告、没有追踪、绝不出售数据。现在不会，将来也不会。', 'لا إعلانات ولا تتبّع ولا بيع للبيانات. لا اليوم ولا أبدًا.'),
 'v4': ('Worldwide', 'Mondial', '全球', 'عالمي'), 'v4p': ('Developers from more than 40 countries and translations into more than 100 languages.', 'Des développeurs de plus de 40 pays et des traductions dans plus de 100 langues.', '来自 40 多个国家的开发者，100 多种语言的翻译。', 'مطوّرون من أكثر من 40 دولة وترجمات إلى أكثر من 100 لغة.'),
 'story': ('Our story', 'Notre histoire', '我们的故事', 'قصتنا'),
 's1': ('Students at École Centrale Paris start a project to stream video across the campus network.', 'Des élèves de l’École Centrale Paris lancent un projet pour diffuser de la vidéo sur le réseau du campus.', '巴黎中央理工学院的学生发起项目，在校园网中传输视频。', 'طلاب في المدرسة المركزية في باريس يطلقون مشروعًا لبثّ الفيديو على شبكة الحرم الجامعي.'),
 's2': ('After a full rewrite, the École agrees to release the code as free software under the GPL.', 'Après une réécriture complète, l’École accepte de publier le code en logiciel libre sous GPL.', '完全重写之后，学校同意以 GPL 将代码作为自由软件发布。', 'بعد إعادة كتابة كاملة، توافق المدرسة على نشر الشيفرة برمجيات حرّة برخصة GPL.'),
 's3': ('The project opens up to developers worldwide, and VLC becomes one of the most downloaded apps ever.', 'Le projet s’ouvre aux développeurs du monde entier, et VLC devient l’une des applications les plus téléchargées.', '项目向全球开发者开放，VLC 成为下载量最高的应用之一。', 'ينفتح المشروع على مطوّري العالم، ويصبح VLC من أكثر التطبيقات تنزيلًا على الإطلاق.'),
 's4': ('VideoLAN becomes fully independent, driven by its own non-profit organisation.', 'VideoLAN devient totalement indépendant, porté par sa propre association.', 'VideoLAN 完全独立，由自己的非营利组织推动。', 'يصبح VideoLAN مستقلًا تمامًا، تقوده منظمته غير الربحية.'),
 's5': ('VLC reaches every platform: Android, iOS, Apple TV, Windows Store, Chromebooks and more.', 'VLC arrive sur toutes les plateformes : Android, iOS, Apple TV, Windows Store, Chromebook et plus.', 'VLC 登陆所有平台：Android、iOS、Apple TV、Windows 应用商店、Chromebook 等。', 'يصل VLC إلى كل المنصّات: Android وiOS وApple TV ومتجر Windows وChromebook وغيرها.'),
 's6': ('VLC 3.0.24 ships more than 130 security fixes and a new FFmpeg.', 'VLC 3.0.24 apporte plus de 130 correctifs de sécurité et un nouveau FFmpeg.', 'VLC 3.0.24 带来 130 余项安全修复和全新 FFmpeg。', 'يصدر VLC 3.0.24 بأكثر من 130 إصلاحًا أمنيًا وFFmpeg جديد.'),
 'more': ('Find out more', 'Pour aller plus loin', '了解更多', 'المزيد'),
}
ABL = [('videolan--team', 'users', ('Team & organisation', 'Équipe et organisation', '团队与组织', 'الفريق والمنظمة')), ('videolan--partners', 'sparkle', ('Partners & consultants', 'Partenaires et consultants', '合作伙伴与顾问', 'الشركاء والمستشارون')),
       ('videolan--events', 'calendar', ('Events', 'Événements', '活动', 'الفعاليات')), ('press', 'news', ('Press', 'Presse', '新闻中心', 'الصحافة')),
       ('legal', 'scale', ('Legal', 'Mentions légales', '法律信息', 'الشؤون القانونية')), ('privacy', 'lock', ('Privacy', 'Confidentialité', '隐私', 'الخصوصية')),
       ('contact', 'mail', ('Contact', 'Contact', '联系我们', 'اتصل بنا')), ('videolan--mirrors', 'disc', ('Mirrors', 'Miroirs', '镜像', 'المرايا'))]
def about(c, p):
    A = lambda k: P(c, AB[k])
    h = [f'<p class="x-lede">{e(A("lede"))}</p><div class="vals">']
    for i, (k, ic) in enumerate([('v1', 'feather'), ('v2', 'code'), ('v3', 'shield'), ('v4', 'globe')]):
        h.append(f'<div class="val glow rv d{i % 3}"><span class="fic">{c.ico(ic)}</span><h3>{e(A(k))}</h3><p>{e(A(k + "p"))}</p></div>')
    h.append(f'</div><h2>{e(A("story"))}</h2><ol class="vtl">')
    for i, (y, k) in enumerate([('1996', 's1'), ('2001', 's2'), ('2005', 's3'), ('2009', 's4'), ('2013', 's5'), ('2026', 's6')]):
        h.append(f'<li class="rv d{i % 3}"><b>{y}</b><p>{e(A(k))}</p></li>')
    h.append(f'</ol><h2>{e(P(c, TEAM_T["board"]))}</h2><div class="board mini">')
    for n, role, ph, _ in BOARD:
        av = (f'<img src="{c.root}media/jbk-160.webp" width="160" height="200" alt="" loading="lazy">' if ph else f'<span class="ini">{initials(n)}</span>')
        h.append(f'<a class="person sm" href="videolan--team.html"><div class="av">{av}</div><div><p class="role">{e(P(c, role))}</p><h3 dir="ltr">{e(n)}</h3></div></a>')
    h.append(f'</div><h2>{e(A("more"))}</h2><div class="tiles">' + ''.join(f'<a class="tl2 glow" href="{s}.html">{c.ico(ic)}<b>{e(P(c, t))}</b>{c.ico("arrow", "ic flip go")}</a>' for s, ic, t in ABL if s in S.ALL) + '</div>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= CONTRIBUTE
CT = {
 'lede': ('VLC exists because people give a little of their time, skills or money. Here is how you can help, whatever you are good at.', 'VLC existe parce que des gens donnent un peu de leur temps, de leurs compétences ou de leur argent. Voici comment aider, quel que soit votre talent.', 'VLC 之所以存在，是因为有人贡献了时间、技能或金钱。无论你擅长什么，都可以这样帮忙。', 'يوجد VLC لأن أناسًا يمنحون قليلًا من وقتهم أو مهاراتهم أو مالهم. إليك كيف تساعد، مهما كانت موهبتك.'),
 'time': ('Give time', 'Donner du temps', '贡献时间', 'امنح وقتك'),
 'mat': ('Give hardware', 'Donner du matériel', '捐赠设备', 'تبرّع بالأجهزة'),
 'mat_p': ('A disc that won’t play, a capture card or a satellite tuner VLC doesn’t support yet? Lending it to developers is the fastest way to get it working.', 'Un disque qui ne se lit pas, une carte d’acquisition ou un tuner satellite pas encore pris en charge ? Le prêter aux développeurs est le moyen le plus rapide de le faire fonctionner.', '有光盘播不了、采集卡或卫星调谐器还不支持？把它借给开发者，是让它尽快可用的最佳途径。', 'قرص لا يعمل، أو بطاقة التقاط، أو موالف فضائي لا يدعمه VLC بعد؟ إعارته للمطوّرين أسرع طريقة لتشغيله.'),
 'mat_cta': ('Contact the team', 'Contacter l’équipe', '联系团队', 'تواصل مع الفريق'),
 'money': ('Give money', 'Faire un don', '捐款', 'تبرّع بالمال'),
 'money_p': ('Donations pay for test hardware, servers and bandwidth, and developer meetings. VideoLAN is a non-profit: nothing is distributed to its members.', 'Les dons financent le matériel de test, les serveurs, la bande passante et les rencontres de développeurs. VideoLAN est une association : rien n’est distribué à ses membres.', '捐款用于测试设备、服务器与带宽以及开发者聚会。VideoLAN 是非营利组织，不向成员分配任何收益。', 'تموّل التبرعات أجهزة الاختبار والخوادم وعرض النطاق ولقاءات المطوّرين. VideoLAN منظمة غير ربحية لا توزّع شيئًا على أعضائها.'),
 'steps': ('Your first contribution in four steps', 'Votre première contribution en quatre étapes', '四步完成你的第一次贡献', 'مساهمتك الأولى في أربع خطوات'),
 'st1': ('Say hello on IRC or the forums', 'Dites bonjour sur IRC ou les forums', '在 IRC 或论坛打个招呼', 'ألقِ التحية على IRC أو في المنتديات'),
 'st2': ('Pick an issue labelled for newcomers on GitLab', 'Choisissez un ticket pour débutants sur GitLab', '在 GitLab 上挑一个新手问题', 'اختر مسألة مخصّصة للمبتدئين على GitLab'),
 'st3': ('Read the Hacker Guide and build VLC', 'Lisez le Hacker Guide et compilez VLC', '阅读 Hacker Guide 并编译 VLC', 'اقرأ دليل المطوّر وابنِ VLC'),
 'st4': ('Open a merge request and get feedback', 'Ouvrez une merge request et recevez des retours', '提交合并请求，听取反馈', 'افتح طلب دمج واحصل على الملاحظات'),
}
ROLES = [
 ('code', ('Developers', 'Développeurs', '开发者', 'المطوّرون'), ('Fix bugs and build features in C, C++, Kotlin, Swift and more.', 'Corrigez des bogues et créez des fonctionnalités en C, C++, Kotlin, Swift et d’autres.', '用 C、C++、Kotlin、Swift 等修复问题、开发功能。', 'أصلح الأخطاء وابنِ الميزات بلغات C وC++ وKotlin وSwift وغيرها.'), 'developers', ('Developer docs', 'Docs développeurs', '开发者文档', 'توثيق المطوّرين')),
 ('globe', ('Translators', 'Traducteurs', '译者', 'المترجمون'), ('Bring VLC to your language through Transifex.', 'Traduisez VLC dans votre langue via Transifex.', '通过 Transifex 把 VLC 翻译成你的语言。', 'انقل VLC إلى لغتك عبر Transifex.'), 'developers--i18n', ('Start translating', 'Commencer à traduire', '开始翻译', 'ابدأ الترجمة')),
 ('book', ('Writers', 'Rédacteurs', '写作者', 'الكتّاب'), ('Improve the user documentation and guides.', 'Améliorez la documentation et les guides utilisateurs.', '完善用户文档与指南。', 'حسّن توثيق المستخدم والأدلّة.'), 'https://docs.videolan.me/vlc-user/', ('User docs', 'Docs utilisateurs', '用户文档', 'توثيق المستخدم')),
 ('chat', ('Support heroes', 'Héros de l’assistance', '答疑达人', 'أبطال الدعم'), ('Answer questions on the forums and IRC.', 'Répondez aux questions sur les forums et IRC.', '在论坛和 IRC 上解答问题。', 'أجب عن الأسئلة في المنتديات وعلى IRC.'), 'https://forum.videolan.org/', ('Forums', 'Forums', '论坛', 'المنتديات')),
 ('bug', ('Testers', 'Testeurs', '测试者', 'المختبِرون'), ('Try nightly builds and report what breaks.', 'Testez les versions de développement et signalez ce qui casse.', '试用每日构建版，报告出问题的地方。', 'جرّب الإصدارات الليلية وأبلغ عمّا يتعطّل.'), 'https://code.videolan.org/videolan/vlc/-/issues', ('Bug tracker', 'Suivi des bogues', '问题追踪', 'متتبّع الأخطاء')),
 ('palette', ('Designers', 'Designers', '设计师', 'المصمّمون'), ('Help shape VLC’s interface and this website.', 'Aidez à façonner l’interface de VLC et ce site.', '帮助塑造 VLC 的界面与本网站。', 'ساعد في تشكيل واجهة VLC وهذا الموقع.'), 'contact', ('Get in touch', 'Nous écrire', '联系我们', 'تواصل معنا')),
]
def _href(x): return x if x.startswith('http') else x + '.html'
def contribute(c, p):
    C = lambda k: P(c, CT[k])
    h = [f'<p class="x-lede">{e(C("lede"))}</p><nav class="jump"><a href="#time">{e(C("time"))}</a><a href="#hardware">{e(C("mat"))}</a><a href="#money">{e(C("money"))}</a></nav>']
    h.append(f'<h2 id="time">{e(C("time"))}</h2><div class="roles">')
    for i, (ic, t, d, link, lt) in enumerate(ROLES):
        h.append(f'<a class="role-c glow rv d{i % 3}" href="{_href(link)}"><span class="fic">{c.ico(ic)}</span><h3>{e(P(c, t))}</h3><p>{e(P(c, d))}</p><span class="more">{e(P(c, lt))}{c.ico("arrow", "ic flip")}</span></a>')
    h.append(f'</div><section class="steps rv"><h3>{e(C("steps"))}</h3><ol>' + ''.join(f'<li><b>{i}</b><span>{e(C("st" + str(i)))}</span></li>' for i in range(1, 5)) + '</ol></section>')
    h.append(f'<div class="split"><section id="hardware" class="panel rv"><span class="fic">{c.ico("cpu")}</span><h2>{e(C("mat"))}</h2><p>{e(C("mat_p"))}</p><a class="btn btn-gh" href="contact.html">{c.ico("mail")}{e(C("mat_cta"))}</a></section>'
             f'<section id="money" class="panel dark rv d1"><span class="fic">{c.ico("heart")}</span><h2>{e(C("money"))}</h2><p>{e(C("money_p"))}</p><p class="ways">{e(c.t("don_ways"))}</p><a class="btn btn-or" href="#donate" data-donate>{c.ico("heart")}{e(c.t("don_btn"))}</a></section></div>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= SUPPORT
SP = {
 'lede': ('VLC is made by volunteers who help in their free time. Most answers are already written down; start there, and you will often have a fix in minutes.', 'VLC est fait par des bénévoles qui aident sur leur temps libre. La plupart des réponses existent déjà : commencez par là, la solution prend souvent quelques minutes.', 'VLC 由志愿者利用业余时间维护。大多数答案早已写好，先从这里找起，往往几分钟就能解决。', 'يصنع VLC متطوّعون يساعدون في أوقات فراغهم. معظم الإجابات مكتوبة بالفعل؛ ابدأ منها، وغالبًا ستجد الحل في دقائق.'),
 'q': ('What do you need?', 'De quoi avez-vous besoin ?', '你需要什么帮助？', 'ماذا تحتاج؟'),
 'a1': ('Find an answer', 'Trouver une réponse', '查找答案', 'ابحث عن إجابة'), 'a1p': ('The FAQ and the user documentation cover the most common questions.', 'La FAQ et la documentation répondent aux questions les plus courantes.', '常见问题与用户文档涵盖了大多数问题。', 'تغطي الأسئلة الشائعة وتوثيق المستخدم أكثر الأسئلة تكرارًا.'),
 'a2': ('Fix a problem', 'Résoudre un problème', '解决问题', 'أصلح مشكلة'), 'a2p': ('Playback stutters, no sound, a file won’t open: the troubleshooting guide walks you through it.', 'Lecture saccadée, pas de son, fichier qui ne s’ouvre pas : le guide de dépannage vous accompagne.', '播放卡顿、没有声音、文件打不开？故障排除指南一步步帮你。', 'تقطّع في التشغيل، أو لا صوت، أو ملف لا يُفتح: يرشدك دليل استكشاف الأخطاء خطوة بخطوة.'),
 'a3': ('Ask the community', 'Demander à la communauté', '向社区提问', 'اسأل المجتمع'), 'a3p': ('Prepare a VLC report first, then ask on the forums or in #videolan on Libera.Chat.', 'Préparez d’abord un rapport VLC, puis posez votre question sur les forums ou dans #videolan sur Libera.Chat.', '先准备好 VLC 报告，再到论坛或 Libera.Chat 的 #videolan 频道提问。', 'جهّز تقرير VLC أولًا، ثم اسأل في المنتديات أو في قناة ‎#videolan على Libera.Chat.'),
 'a4': ('Report a bug', 'Signaler un bogue', '报告问题', 'أبلغ عن خطأ'), 'a4p': ('Found something broken? Each platform has its own tracker on GitLab.', 'Quelque chose ne marche pas ? Chaque plateforme a son propre suivi sur GitLab.', '发现问题？每个平台在 GitLab 上都有独立的问题追踪。', 'وجدت عطلًا؟ لكل منصّة متتبّعها الخاص على GitLab.'),
 'trackers': ('Bug trackers by platform', 'Suivi des bogues par plateforme', '各平台问题追踪', 'متتبّعات الأخطاء حسب المنصّة'),
 'irc': ('Live chat', 'Discussion en direct', '实时聊天', 'دردشة مباشرة'),
 'irc_p': ('Server irc.libera.chat, channel #videolan. No client? Use the web chat.', 'Serveur irc.libera.chat, salon #videolan. Pas de client ? Utilisez le chat web.', '服务器 irc.libera.chat，频道 #videolan。没有客户端？用网页聊天。', 'الخادم irc.libera.chat، القناة ‎#videolan. لا يوجد عميل؟ استخدم الدردشة عبر الويب.'),
 'web_chat': ('Open web chat', 'Ouvrir le chat web', '打开网页聊天', 'افتح الدردشة عبر الويب'),
 'pro': ('Professional services', 'Services professionnels', '专业服务', 'خدمات احترافية'),
 'pro_p': ('Need guaranteed support, custom development or integration? Companies close to VideoLAN offer paid services.', 'Besoin d’assistance garantie, de développements sur mesure ou d’intégration ? Des sociétés proches de VideoLAN proposent des services payants.', '需要有保障的技术支持、定制开发或系统集成？与 VideoLAN 关系密切的公司提供付费服务。', 'تحتاج دعمًا مضمونًا أو تطويرًا مخصّصًا أو تكاملًا؟ تقدّم شركات قريبة من VideoLAN خدمات مدفوعة.'),
 'update': ('About the update warning on Windows', 'À propos de l’alerte de mise à jour sous Windows', '关于 Windows 上的更新警告', 'عن تحذير التحديث على Windows'),
 'update_p': ('VLC 3.0.12 and 3.0.13 showed an update warning on some PCs. Here is what happened and what to do.', 'VLC 3.0.12 et 3.0.13 affichaient une alerte de mise à jour sur certains PC. Voici ce qui s’est passé et quoi faire.', 'VLC 3.0.12 和 3.0.13 在部分电脑上弹出更新警告。这里说明原因和处理方法。', 'أظهر VLC 3.0.12 و3.0.13 تحذير تحديث على بعض الأجهزة. إليك ما حدث وما يجب فعله.'),
 'note': ('Nobody owes anyone an answer: be kind, be precise, and include your VLC version and system.', 'Personne ne doit de réponse à personne : soyez aimable, précis, et indiquez votre version de VLC et votre système.', '没有人有义务回答你：请友善、具体，并写明你的 VLC 版本和系统。', 'لا أحد ملزم بالإجابة: كن لطيفًا ودقيقًا، واذكر إصدار VLC ونظامك.'),
}
def support(c, p):
    Sx = lambda k: P(c, SP[k])
    paths = [('search', 'a1', [('FAQ', 'support--faq.html'), ('User docs', 'https://docs.videolan.me/vlc-user/'), ('Wiki', 'https://wiki.videolan.org/Documentation')]),
             ('bandage', 'a2', [('Common problems', 'https://wiki.videolan.org/Common_Problems'), ('User docs · Support', 'https://docs.videolan.me/vlc-user/en/index.html')]),
             ('chat', 'a3', [('VLC report', 'https://wiki.videolan.org/VLC_report'), ('Forums', 'https://forum.videolan.org/'), ('IRC', 'https://kiwiirc.com/nextclient/#ircs://irc.libera.chat/#videolan')]),
             ('bug', 'a4', [('Desktop', 'https://code.videolan.org/videolan/vlc/-/issues'), ('Android', 'https://code.videolan.org/videolan/vlc-android/-/issues'), ('Apple', 'https://code.videolan.org/videolan/vlc-ios/-/issues')])]
    h = [f'<p class="x-lede">{e(Sx("lede"))}</p><h2>{e(Sx("q"))}</h2><div class="paths">']
    for i, (ic, k, links) in enumerate(paths):
        h.append(f'<article class="path glow rv d{i % 3}"><span class="num">{i + 1}</span><span class="fic">{c.ico(ic)}</span><h3>{e(Sx(k))}</h3><p>{e(Sx(k + "p"))}</p><div class="pl" dir="ltr">' + ''.join(f'<a href="{u}">{e(t)}{c.ico("arrow")}</a>' for t, u in links) + '</div></article>')
    h.append(f'</div><p class="note">{c.ico("heart")}<span>{e(Sx("note"))}</span></p>')
    h.append(f'<div class="split"><section class="panel rv"><span class="fic">{c.ico("chat")}</span><h2>{e(Sx("irc"))}</h2><p>{e(Sx("irc_p"))}</p><div class="term"><div class="tt"><i></i><i></i><i></i><span>IRC</span><button type="button" class="cp" data-copy="/join #videolan">{c.ico("copy")}{e(c.t("dl_copy"))}</button></div><pre><code><span class="p">$ </span>/server irc.libera.chat\n<span class="p">$ </span>/join #videolan</code></pre></div><p style="margin-top:1rem"><a class="btn btn-gh btn-sm" href="https://kiwiirc.com/nextclient/#ircs://irc.libera.chat/#videolan">{e(Sx("web_chat"))}{c.ico("ext")}</a></p></section>'
             f'<section class="panel rv d1"><span class="fic">{c.ico("users")}</span><h2>{e(Sx("pro"))}</h2><p>{e(Sx("pro_p"))}</p><ul class="cons" dir="ltr"><li><b>Videolabs</b><span>VLC mobile apps · libVLC</span></li><li><b>OpenHeadend</b><span>Broadcast · DVBlast</span></li><li><b>M2X</b><span>Streaming · encoding</span></li></ul><a class="btn btn-gh btn-sm" href="videolan--partners.html">{e(P(c, U["learn"]))}{c.ico("arrow", "ic flip")}</a></section></div>')
    h.append(f'<a class="banner rv" href="vlc--releases--3.0.12-update.html">{c.ico("info")}<span><b>{e(Sx("update"))}</b><small>{e(Sx("update_p"))}</small></span>{c.ico("arrow", "ic flip")}</a>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= libVLC
LV = {
 'lede': ('libVLC is the engine inside VLC, packaged as a C library. Hundreds of plugins, every format, every platform, in your own app.', 'libVLC est le moteur de VLC, sous forme de bibliothèque C. Des centaines de modules, tous les formats, toutes les plateformes, dans votre application.', 'libVLC 是 VLC 内部的引擎，以 C 库形式提供。数百个插件、所有格式、所有平台，尽入你的应用。', 'libVLC هو المحرّك داخل VLC في هيئة مكتبة C. مئات الإضافات، وكل الصيغ، وكل المنصّات، داخل تطبيقك.'),
 'why': ('What you get', 'Ce que vous obtenez', '你能得到什么', 'ما الذي تحصل عليه'),
 'w': [('Every format and protocol', 'Tous les formats et protocoles', '所有格式与协议', 'كل الصيغ والبروتوكولات'), ('Hardware decoding up to 8K', 'Décodage matériel jusqu’en 8K', '最高 8K 硬件解码', 'فك ترميز عتادي حتى 8K'),
       ('Network browsing: SMB, NFS, SFTP, UPnP', 'Navigation réseau : SMB, NFS, SFTP, UPnP', '网络浏览：SMB、NFS、SFTP、UPnP', 'تصفّح الشبكة: SMB وNFS وSFTP وUPnP'), ('DVD and Blu-ray with menus', 'DVD et Blu-ray avec menus', '带菜单的 DVD 与蓝光', 'DVD وBlu-ray مع القوائم'),
       ('HDR with tone mapping', 'HDR avec tone mapping', 'HDR 及色调映射', 'HDR مع تعيين النغمات'), ('HD audio passthrough', 'Passage direct de l’audio HD', '高清音频直通', 'تمرير الصوت عالي الدقة'),
       ('360° video and Ambisonics', 'Vidéo 360° et Ambisonics', '360° 视频与 Ambisonics', 'فيديو 360° وAmbisonics'), ('Cast to Chromecast and UPnP', 'Diffusion vers Chromecast et UPnP', '投屏到 Chromecast 与 UPnP', 'البث إلى Chromecast وUPnP')],
 'by_vl': ('Official bindings by VideoLAN', 'Liaisons officielles de VideoLAN', 'VideoLAN 官方绑定', 'الروابط الرسمية من VideoLAN'),
 'by_com': ('Bindings by the community', 'Liaisons de la communauté', '社区绑定', 'روابط المجتمع'),
 'samples': ('Samples to start from', 'Des exemples pour démarrer', '入门示例', 'أمثلة للبدء'),
 'samples_p': ('Clone a sample, run it, and build from there.', 'Clonez un exemple, lancez-le et partez de là.', '克隆一个示例，运行起来，在此基础上开发。', 'استنسخ مثالًا وشغّله وابنِ عليه.'),
 'facts_v': ('Version', 'Version', '版本', 'الإصدار'), 'facts_vv': ('3 stable · 4 in development', '3 stable · 4 en développement', '3 稳定版 · 4 开发中', '3 مستقر · 4 قيد التطوير'),
 'gallery': ('Built with libVLC', 'Réalisé avec libVLC', '基于 libVLC 打造', 'مبني بـ libVLC'),
 'book': ('The Good Parts of LibVLC', 'The Good Parts of LibVLC', 'The Good Parts of LibVLC', 'The Good Parts of LibVLC'),
 'book_p': ('The first book about libVLC and the VideoLAN community, for developers and consultants (2022).', 'Le premier livre sur libVLC et la communauté VideoLAN, pour les développeurs et les consultants (2022).', '第一本介绍 libVLC 与 VideoLAN 社区的书，面向开发者与顾问（2022）。', 'أول كتاب عن libVLC ومجتمع VideoLAN، للمطوّرين والمستشارين (2022).'),
 'discord': ('Join the libVLC Discord', 'Rejoindre le Discord libVLC', '加入 libVLC Discord', 'انضم إلى Discord الخاص بـ libVLC'),
 'discord_p': ('Questions about the APIs and bindings? The community is there.', 'Des questions sur les API et les liaisons ? La communauté est là.', '对 API 和绑定有疑问？社区随时在线。', 'أسئلة عن الواجهات والروابط؟ المجتمع هنا.'),
 'diagram': ('Architecture', 'Architecture', '架构', 'البنية'),
}
BIND_VL = [('libvlcpp', 'C++', 'https://code.videolan.org/videolan/libvlcpp', 'All'), ('VLCKit', 'Swift · Objective-C', 'https://code.videolan.org/videolan/VLCKit', 'iOS · macOS · tvOS'),
           ('libvlcjni', 'Kotlin · Java', 'https://code.videolan.org/videolan/vlc-android/-/tree/master/libvlc', 'Android'), ('LibVLCSharp', 'C# · .NET', 'https://code.videolan.org/videolan/LibVLCSharp', 'All')]
BIND_COM = [('vlcj', 'Java', 'https://github.com/caprica/vlcj', 'Desktop'), ('python-vlc', 'Python', 'https://github.com/oaubert/python-vlc', 'Desktop'),
            ('vlc-rs', 'Rust', 'https://github.com/garkimasera/vlc-rs', 'Desktop'), ('libvlc-go', 'Go', 'https://github.com/adrg/libvlc-go', 'Desktop')]
SAMPLES = [('LibVLCSharp', 'https://code.videolan.org/mfkl/libvlcsharp-samples'), ('vlcj', 'https://github.com/caprica/vlcj-examples/tree/master/src/main/java/uk/co/caprica/vlcj/test'),
           ('libvlcpp', 'https://code.videolan.org/videolan/libvlcpp/-/blob/master/test/main.cpp'), ('VLCKit', 'https://code.videolan.org/videolan/VLCKit/-/tree/master/Examples'),
           ('libvlcjni', 'https://code.videolan.org/videolan/libvlc-android-samples'), ('python-vlc', 'https://github.com/oaubert/python-vlc/tree/master/examples')]
GAL = [('mosaic-android.png', ('Mosaic views on Android', 'Vues en mosaïque sur Android', 'Android 上的马赛克视图', 'عرض فسيفسائي على Android')), ('360-video.png', ('360° video navigation', 'Navigation en vidéo 360°', '360° 视频视角导航', 'التنقّل في فيديو 360°')),
       ('thumbnailer.jpg', ('libVLC thumbnailer', 'Générateur de vignettes libVLC', 'libVLC 缩略图生成', 'مولّد الصور المصغّرة في libVLC')), ('mediaplayerelement.png', ('MediaPlayerElement in LibVLCSharp', 'MediaPlayerElement dans LibVLCSharp', 'LibVLCSharp 中的 MediaPlayerElement', 'MediaPlayerElement في LibVLCSharp'))]
CODE = '''#include <vlc/vlc.h>

int main(void)
{
    libvlc_instance_t *vlc = libvlc_new(0, NULL);
    libvlc_media_t *m = libvlc_media_new_location(vlc,
        "https://example.org/movie.mkv");
    libvlc_media_player_t *mp = libvlc_media_player_new_from_media(m);
    libvlc_media_release(m);

    libvlc_media_player_play(mp);   /* that's it */
    /* ... */
    libvlc_media_player_release(mp);
    libvlc_release(vlc);
}'''
def libvlc(c, p):
    V_ = lambda k: P(c, LV[k])
    code = e(CODE)
    code = re.sub(r'(#include)', r'<span class="k">\1</span>', code)
    code = re.sub(r'\b(int|void|return)\b', r'<span class="k">\1</span>', code)
    code = re.sub(r'(libvlc_\w+)', r'<span class="f">\1</span>', code)
    code = re.sub(r'(&quot;[^&]*&quot;)', r'<span class="s">\1</span>', code)
    code = re.sub(r'(/\*.*?\*/)', r'<span class="cm">\1</span>', code)
    h = [f'<p class="x-lede">{e(V_("lede"))}</p><div class="lv-hero rv"><div class="codewin" dir="ltr"><div class="tt"><i></i><i></i><i></i><span>play.c</span></div><pre><code>{code}</code></pre></div>'
         f'<dl class="facts big"><div><dt>{e(P(c, U["language"]))}</dt><dd dir="ltr">C</dd></div><div><dt>{e(P(c, U["license"]))}</dt><dd dir="ltr">LGPL 2.1</dd></div><div><dt>{e(V_("facts_v"))}</dt><dd>{e(V_("facts_vv"))}</dd></div><div><dt>{e(P(c, U["platforms"]))}</dt><dd dir="ltr">Windows · macOS · Linux · Android · iOS · tvOS</dd></div></dl></div>']
    h.append(f'<h2>{e(V_("why"))}</h2><ul class="checks">' + ''.join(f'<li class="rv d{i % 3}">{c.ico("check")}<span>{e(P(c, x))}</span></li>' for i, x in enumerate(LV['w'])) + '</ul>')
    def bgrid(items, official):
        return '<div class="binds">' + ''.join(f'<a class="bind glow rv d{i % 3}{" off" if official else ""}" href="{u}" dir="ltr"><span class="lang">{e(lang.split(" · ")[0])}</span><b>{e(n)}</b><small>{e(lang)} · {e(FW(c, pl))}</small>{c.ico("ext")}</a>' for i, (n, lang, u, pl) in enumerate(items)) + '</div>'
    h.append(f'<h2>{e(V_("by_vl"))}</h2>{bgrid(BIND_VL, True)}<h2>{e(V_("by_com"))}</h2>{bgrid(BIND_COM, False)}')
    h.append(f'<h2>{e(V_("samples"))}</h2><p>{e(V_("samples_p"))}</p><div class="samples" dir="ltr">' + ''.join(f'<a href="{u}">{c.ico("git")}{e(n)}</a>' for n, u in SAMPLES) + '</div>')
    h.append(f'<h2>{e(V_("gallery"))}</h2><div class="gal">' + ''.join(f'<figure class="rv d{i % 3}"><img src="https://images.videolan.org/images/{f}" alt="{e(P(c, cap))}" loading="lazy"><figcaption>{e(P(c, cap))}</figcaption></figure>' for i, (f, cap) in enumerate(GAL)) + '</div>')
    h.append(f'<div class="split"><a class="panel rv" href="https://mfkl.gumroad.com/l/libvlc-good-parts"><span class="fic">{c.ico("book")}</span><h2 dir="ltr">{e(V_("book"))}</h2><p>{e(V_("book_p"))}</p></a>'
             f'<a class="panel dark rv d1" href="https://discord.gg/3h3K3JF"><span class="fic">{c.ico("chat")}</span><h2>{e(V_("discord"))}</h2><p>{e(V_("discord_p"))}</p></a></div>')
    h.append(f'<h2>{e(V_("diagram"))}</h2><figure class="diag"><img src="https://images.videolan.org/images/libvlc_stack.png" alt="libVLC stack" loading="lazy"></figure>')
    h.append(ref_block(c, p))
    return '\n'.join(h)

# ================================================================= NEWS (blog)
def news_card(c, n, big=False, base=''):
    href = f'{base}{S.NEWS_ANCHOR.get(n["id"], "news")}.html#{n["id"]}' if n['id'] else 'news.html'
    txt = ' '.join(re.sub(r'<[^>]+>', ' ', H.unescape(n['html'])).split())
    ex = (txt[:260 if big else 150].rsplit(' ', 1)[0] + '…') if len(txt) > (260 if big else 150) else txt
    cat = news_cat(n); cl = dict(NEWS_CATS)[cat]
    d = I.date(c.lang, n['date']) if n['date'][:4] not in ('', '1970') else c.t('undated')
    return (f'<a class="ncard glow{" big" if big else ""}" href="{href}" data-cat="{cat}" data-q="{e((n["title"] + " " + txt[:400]).lower())}">'
            f'<span class="nmeta"><span class="ncat c-{cat}">{e(P(c, cl))}</span><time datetime="{e(n["date"])}">{e(d)}</time></span>'
            f'<h{2 if big else 3} class="nt" lang="en" dir="ltr">{e(n["title"])}</h{2 if big else 3}><p lang="en" dir="ltr">{e(ex)}</p><span class="more">{e(P(c, U["read_story"]))}{c.ico("arrow", "ic flip")}</span></a>')

def news_tools(c, count):
    chips = f'<button type="button" data-cat="" aria-pressed="true">{e(P(c, U["all"]))}</button>' + ''.join(f'<button type="button" data-cat="{k}" aria-pressed="false">{e(P(c, l))}</button>' for k, l in NEWS_CATS)
    return (f'<div class="ntools" data-ntools><label class="sr" for="nq">{e(P(c, U["filter_news"]).replace("{n}", str(count)))}</label>'
            f'<span class="sbox">{c.ico("search")}<input class="srch" id="nq" type="search" autocomplete="off" placeholder="{e(P(c, U["filter_news"]).replace("{n}", str(count)))}"></span>'
            f'<div class="chipsel" role="group">{chips}</div></div>')

def years_nav(c, cur=None):
    ys = S.YEARS + (['undated'] if 'undated' in S.NEWS_BY_YEAR else [])
    return f'<nav class="x-years" aria-label="{e(c.t("news_by_year"))}"><a href="news.html"{" aria-current=page" if cur is None else ""}>{e(P(c, U["latest"]))}</a>' + ''.join(f'<a href="news--{y}.html"' + (' aria-current="page"' if y == cur else '') + f'>{y if y != "undated" else e(c.t("undated"))} <small>{len(S.NEWS_BY_YEAR[y])}</small></a>' for y in ys) + '</nav>'

def news_hub(c):
    N = S.NEWS
    h = [f'<p class="x-lede">{e(c.t("news_lede", n=len(N)))}</p>', news_tools(c, len(N)), '<div class="nfeat">', news_card(c, N[0], True), '<div class="nside">' + ''.join(news_card(c, n) for n in N[1:3]) + '</div></div>']
    h.append('<div class="ngrid" data-nlist>' + ''.join(news_card(c, n).replace('class="ncard', 'class="ncard dup', 1) for n in N[:3]) + ''.join(news_card(c, n) if i < 21 else news_card(c, n).replace('class="ncard', 'class="ncard later', 1) for i, n in enumerate(N[3:])) + f'</div><p class="wall-empty" hidden>{e(P(c, U["no_match"]))}</p><p class="center"><button type="button" class="btn btn-gh" data-nmore>{c.ico("plist")}{e(P(c, U["show_more"]))}</button></p>')
    h.append(f'<h2>{e(P(c, U["archive"]))}</h2>' + years_nav(c))
    return '\n'.join(h)

def news_year(c, y):
    items = S.NEWS_BY_YEAR[y]
    h = [years_nav(c, y), '<div class="posts">']
    for n in items:
        cat = news_cat(n); d = I.date(c.lang, n['date']) if n['date'][:4] not in ('', '1970') else c.t('undated')
        h.append(f'<article class="post rv" id="{e(n["id"])}"><header><span class="nmeta"><span class="ncat c-{cat}">{e(P(c, dict(NEWS_CATS)[cat]))}</span><time datetime="{e(n["date"])}">{e(d)}</time></span>'
                 f'<h2 lang="en" dir="ltr"><a href="#{e(n["id"])}">{e(n["title"])}</a></h2></header><div class="prose" lang="en" dir="ltr">{S.rewrite(n["html"])}</div></article>')
    h.append('</div>')
    return '\n'.join(h)

# ================================================================= SECTION HUB
def excerpt(p, n=120):
    if p.get('desc'): t = p['desc']
    else: t = ' '.join(re.sub(r'<[^>]+>', ' ', H.unescape(p.get('html', ''))).split())
    return (t[:n].rsplit(' ', 1)[0] + '…') if len(t) > n else t
SEC_ICON = dict(download='download', vlc='cone', releases='zap', news='news', security='shield', projects='box', developers='code', support='chat', contribute='users', events='calendar', press='mail', videolan='home')
FEATURED = {
 'vlc': ['vlc--features', 'vlc--screenshots', 'vlc--skins', 'vlc--libvlc'], 'download': ['download', 'vlc--download-windows', 'vlc--download-macosx', 'vlc--download-android'],
 'releases': ['vlc--releases--3.0.24', 'vlc--releases--3.0.23', 'vlc--releases--3.0.0'], 'security': ['security', 'security--sb-vlc3024', 'security--sb-vlc3022'],
 'projects': ['projects', 'developers', 'vlc--libvlc', 'projects--dav1d', 'developers--x264', 'projects--dvblast', 'developers--i18n', 'developers--lists'],
 'support': ['support', 'support--faq', 'support--lists'], 'contribute': ['contribute', 'developers--i18n'], 'events': ['videolan--events', 'videolan--events--vdd25', 'videolan--events--vdd24'],
 'press': ['press', 'press--videolan-20'], 'videolan': ['videolan', 'videolan--team', 'videolan--partners', 'legal'],
}
def section_hub(c, k):
    items = S.ordered(k)
    seen = set(); feat = [s for s in FEATURED.get(k, []) if s in S.ALL]
    h = [f'<p class="x-lede">{e(I.sec(c.lang, k, 1))}</p>']
    if feat:
        h.append(f'<h2>{e(P(c, U["featured"]))}</h2><div class="hubfeat">')
        for i, s in enumerate(feat):
            q = S.ALL[s]; seen.add(s)
            h.append(f'<a class="hf glow rv d{i % 3}" href="{s}.html"><span class="fic">{c.ico(SEC_ICON.get(k, "book"))}</span><b lang="en" dir="ltr">{e(H.unescape(q["display"]))}</b><span lang="en" dir="ltr">{e(excerpt(q, 110))}</span>{c.ico("arrow", "ic flip go")}</a>')
        h.append('</div>')
    rest = [q for q in items if q['slug'] not in seen]
    if k == 'news':
        rest = []
    h.append(f'<h2>{e(P(c, U["everything"]).replace("{s}", I.sec(c.lang, k, 0)))} <small class="cnt">{len(rest) + len(seen)}</small></h2>')
    if len(rest) > 8:
        h.append(f'<div class="ntools" data-hubf><span class="sbox">{c.ico("search")}<input class="srch" type="search" autocomplete="off" placeholder="{e(P(c, U["filter"]).replace("{n}", str(len(rest))))}" aria-label="{e(P(c, U["filter"]).replace("{n}", str(len(rest))))}"></span></div>')
    h.append('<div class="x-list" data-hublist>' + ''.join(f'<a class="x-li" href="{q["slug"]}.html" data-q="{e((q["display"] + " " + q["path"]).lower())}" lang="en"><b>{e(H.unescape(q["display"]))}</b><span>{e(excerpt(q, 90))}</span></a>' for q in rest) + '</div>')
    if k == 'news':
        h.append(years_nav(c))
    h.append(f'<p class="wall-empty" hidden>{e(P(c, U["no_match"]))}</p>')
    return '\n'.join(h)

CURATED = {'vlc--features': features, 'projects': projects, 'videolan--team': team, 'videolan': about, 'contribute': contribute, 'support': support, 'vlc--libvlc': libvlc}
CUR_TITLE = {
 'vlc--features': FEAT_H[0], 'projects': ('Projects & developers', 'Projets et développeurs', '项目与开发者', 'المشاريع والمطوّرون'), 'videolan--team': ('The VideoLAN team', 'L’équipe VideoLAN', 'VideoLAN 团队', 'فريق VideoLAN'),
 'videolan': ('About VideoLAN', 'À propos de VideoLAN', '关于 VideoLAN', 'عن VideoLAN'), 'contribute': ('Get involved', 'Participer', '参与贡献', 'شارك معنا'),
 'support': ('Help & support', 'Aide et assistance', '帮助与支持', 'المساعدة والدعم'), 'vlc--libvlc': ('libVLC', 'libVLC', 'libVLC', 'libVLC'),
}
CUR_ICON = {'vlc--features': 'sparkle', 'projects': 'box', 'videolan--team': 'users', 'videolan': 'home', 'contribute': 'heart', 'support': 'chat', 'vlc--libvlc': 'code'}

# ================================================================= PROJECTS & DEVELOPERS: one directory
DU = {
 'dir': ('Projects & developers', 'Projets et développeurs', '项目与开发者', 'المشاريع والمطوّرون'),
 'find': ('Find a project or a guide…', 'Trouver un projet ou un guide…', '查找项目或指南…', 'ابحث عن مشروع أو دليل…'),
 'overview': ('Overview', 'Présentation', '概览', 'نظرة عامة'),
 'res': ('Developer resources', 'Ressources développeurs', '开发者资源', 'موارد المطوّرين'),
 'res_p': ('Documentation, mailing lists, translation and how to build from source.', 'Documentation, listes de diffusion, traduction et compilation depuis les sources.', '文档、邮件列表、翻译以及如何从源码编译。', 'التوثيق والقوائم البريدية والترجمة وكيفية البناء من المصدر.'),
 'arch': ('More libraries and archives', 'Autres bibliothèques et archives', '更多库与归档项目', 'مكتبات ومشاريع مؤرشفة أخرى'),
 'arch_p': ('Related encoders, and older projects kept for reference.', 'Encodeurs apparentés et anciens projets conservés pour référence.', '相关编码器，以及保留备查的旧项目。', 'مرمّزات ذات صلة، ومشاريع قديمة محفوظة للرجوع إليها.'),
 'pages': ('{n} pages', '{n} pages', '{n} 个页面', '{n} صفحات'),
 'all_proj': ('All projects', 'Tous les projets', '全部项目', 'كل المشاريع'),
 'archived': ('Archived', 'Archivé', '已归档', 'مؤرشف'),
}
RES = [('developers', 'code', ('Developer zone', 'Espace développeurs', '开发者专区', 'منطقة المطوّرين')),
       ('vlc--download-sources', 'terminal', ('Build VLC from source', 'Compiler VLC depuis les sources', '从源码编译 VLC', 'ابنِ VLC من المصدر')),
       ('developers--i18n', 'globe', ('Translate VideoLAN', 'Traduire VideoLAN', '翻译 VideoLAN', 'ترجم VideoLAN')),
       ('developers--lists', 'mail', ('Mailing lists', 'Listes de diffusion', '邮件列表', 'القوائم البريدية')),
       ('developers--vlc', 'cone', ('VLC for developers', 'VLC pour les développeurs', '面向开发者的 VLC', 'VLC للمطوّرين')),
       ('developers--unity', 'box', ('VLC for Unity', 'VLC pour Unity', 'VLC for Unity', 'VLC لـ Unity'))]
ARCH = [('developers--x262', 'x262', ('MPEG-2 encoder based on x264', 'Encodeur MPEG-2 basé sur x264', '基于 x264 的 MPEG-2 编码器', 'مرمّز MPEG-2 مبني على x264')),
        ('developers--x265', 'x265', ('HEVC encoder (MulticoreWare)', 'Encodeur HEVC (MulticoreWare)', 'HEVC 编码器（MulticoreWare）', 'مرمّز HEVC من MulticoreWare')),
        ('developers--libdvdplay', 'libdvdplay', ('Early DVD navigation library', 'Ancienne bibliothèque de navigation DVD', '早期 DVD 导航库', 'مكتبة قديمة للتنقّل في DVD')),
        ('developers--vls', 'VideoLAN Server', ('Superseded by VLC streaming', 'Remplacé par la diffusion de VLC', '已由 VLC 串流功能取代', 'حلّ محلّه البث في VLC'))]
PJMAP = {x[0]: x for x in PJ}
EXTRA_KIDS = {'developers--libaacs': ['developers--libbdplus'], 'developers--i18n': ['developers--i18n--transifex-howto', 'developers--i18n--vlc-howto', 'developers--i18n--vlcstat']}
ALL_DIR = [x[0] for x in PJ] + [x[0] for x in RES] + [x[0] for x in ARCH]

def kids(slug):
    if slug == 'vlc': return []
    k = [s for s in S.ALL if s.startswith(slug + '--')]
    return sorted(k, key=lambda s: (s.count('--'), s)) + [s for s in EXTRA_KIDS.get(slug, []) if s in S.ALL]
def owner(slug):
    """the directory entry a page belongs to (itself, or its parent project)"""
    if slug in ALL_DIR: return slug
    for o, ks in EXTRA_KIDS.items():
        if slug in ks: return o
    best = ''
    for o in ALL_DIR:
        if o != 'vlc' and slug.startswith(o + '--') and len(o) > len(best): best = o
    return best or None
def in_dir(slug, p):
    return owner(slug) is not None or (S.sec_key(p) == 'projects' and not p.get('virtual'))
def kid_label(parent_name, d):
    d = H.unescape(d)
    for pre in (parent_name + ' ', 'VLMa ', 'VideoLAN '):
        if d.startswith(pre) and len(d) > len(pre) + 2: return d[len(pre):]
    return d

def directory(c, slug):
    own = owner(slug)
    def li(s, name, sub=''):
        cur = ' aria-current="page"' if s == slug else (' class="own"' if s == own else '')
        ch = ''
        if s == own and kids(s):
            ch = '<ul class="kids">' + ''.join(f'<li><a href="{k}.html"' + (' aria-current="page"' if k == slug else '') + f' lang="en">{e(kid_label(name, S.ALL[k]["display"]))}</a></li>' for k in kids(s)) + '</ul>'
        return f'<li data-q="{e((name + " " + sub).lower())}"><a href="{s}.html"{cur}><span dir="ltr">{e(name)}</span>{f"<small>{e(sub)}</small>" if sub else ""}</a>{ch}</li>'
    groups = []
    for g, gt, _ in PJ_GROUPS:
        groups.append((P(c, gt), ''.join(li(x[0], x[1]) for x in PJ if x[3] == g)))
    groups.append((P(c, DU['res']), ''.join(li(s, P(c, t)) for s, _, t in RES if s in S.ALL)))
    groups.append((P(c, DU['arch']), ''.join(li(s, n) for s, n, _ in ARCH if s in S.ALL)))
    body = ''.join(f'<section class="pg"><h2 class="pdh">{e(t)}</h2><ul>{u}</ul></section>' for t, u in groups)
    return (f'<aside class="side pdir" data-pdir><details open><summary>{c.ico("box")}<span>{e(P(c, DU["dir"]))}</span><small>{len(ALL_DIR)}</small></summary>'
            f'<div class="pdir-s">{c.ico("search")}<input type="search" autocomplete="off" placeholder="{e(P(c, DU["find"]))}" aria-label="{e(P(c, DU["find"]))}"></div>'
            f'<nav aria-label="{e(P(c, DU["dir"]))}">{body}</nav><p class="pdir-none" hidden>{e(P(c, U["no_match"]))}</p>'
            f'<a class="all" href="projects.html">{e(P(c, DU["all_proj"]))}{c.ico("arrow", "ic flip")}</a></details></aside>')

def band(c, slug):
    """project identity band shown on a project page and all of its sub-pages"""
    own = owner(slug)
    if not own or own not in PJMAP: return ''
    _, name, il, _, tag, facts, code = PJMAP[own]
    ks = kids(own)
    tabs = ''
    if ks:
        tabs = '<nav class="ptabs" aria-label="' + e(name) + '">' + f'<a href="{own}.html"' + (' aria-current="page"' if slug == own else '') + f'>{e(P(c, DU["overview"]))}</a>' + ''.join(f'<a href="{k}.html"' + (' aria-current="page"' if k == slug else '') + f' lang="en">{e(kid_label(name, S.ALL[k]["display"]))}</a>' for k in ks) + '</nav>'
    fl = [(P(c, U['language']), facts[0]), (P(c, U['license']), facts[1]), (P(c, U['platforms']), FW(c, facts[2])), (P(c, U['since']), facts[3])]
    links = (f'<a class="btn btn-gh btn-sm" href="{code}">{c.ico("git")}{e(P(c, U["code"]))}</a>' if code else '')
    grp = P(c, dict((g, t) for g, t, _ in PJ_GROUPS)[PJMAP[own][3]])
    return (f'<section class="pband"><div class="pb-il">{illo(il)}</div><div class="pb-t"><p class="kick">{e(grp)}</p><h2 dir="ltr">{e(name)}</h2><p>{e(P(c, tag))}</p>'
            f'<dl class="facts">{"".join(f"<div><dt>{e(a)}</dt><dd dir=ltr>{e(b)}</dd></div>" for a, b in fl)}</dl><div class="plinks">{links}</div></div></section>{tabs}')

def projects_extra(c):
    """resources + archives on the merged landing page"""
    h = [f'<section class="pgrp" id="g-res"><h2>{e(P(c, DU["res"]))}</h2><p class="gd">{e(P(c, DU["res_p"]))}</p><div class="tiles">']
    h += [f'<a class="tl2 glow pcf" data-q="{e(P(c, t).lower())}" href="{s}.html">{c.ico(ic)}<b>{e(P(c, t))}</b>{c.ico("arrow", "ic flip go")}</a>' for s, ic, t in RES if s in S.ALL]
    h.append(f'</div></section><section class="pgrp" id="g-arch"><h2>{e(P(c, DU["arch"]))}</h2><p class="gd">{e(P(c, DU["arch_p"]))}</p><div class="tiles">')
    h += [f'<a class="tl2 glow pcf" data-q="{e((n + " " + P(c, d)).lower())}" href="{s}.html">{c.ico("disc")}<span><b dir="ltr">{e(n)}</b><small class="tsub">{e(P(c, d))}</small></span>{c.ico("arrow", "ic flip go")}</a>' for s, n, d in ARCH if s in S.ALL]
    h.append('</div></section>')
    return ''.join(h)
