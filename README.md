<div align="center">

<img src=".github/img/banner.png" alt="VideoLAN Web Redesign: videolan.org rebuilt, 25,029 pages in 81 languages" width="100%">

<br>

**An unofficial, free redesign of [videolan.org](https://www.videolan.org), offered to the VideoLAN team.**<br>
Every page of the current site rebuilt as one static, accessible website in 81 languages: a landing for the whole VideoLAN organisation, a dedicated VLC home, and a real download centre for VLC 3.0.24.

Everything is live at **[vlc.paulfleury.com](https://vlc.paulfleury.com)**. Prefer not to clone? Grab the whole built site in one archive: **[vlc-web-redesign.zip](https://vlc.paulfleury.com/vlc-web-redesign.zip)**.

<br>

[![license: MIT](https://img.shields.io/badge/license-MIT-0a0a0a?style=for-the-badge&labelColor=282828)](LICENSE)
[![live: vlc.paulfleury.com](https://img.shields.io/badge/live-vlc.paulfleury.com-ff8800?style=for-the-badge&labelColor=282828)](https://vlc.paulfleury.com)
[![download: vlc-web-redesign.zip](https://img.shields.io/badge/download-vlc--web--redesign.zip-0a0a0a?style=for-the-badge&labelColor=282828)](https://vlc.paulfleury.com/vlc-web-redesign.zip)

[![version: 1.4.0](https://img.shields.io/badge/version-1.4.0-ff8800?style=flat-square&labelColor=282828)](CHANGELOG.md)
[![pages: 25,029](https://img.shields.io/badge/pages-25%2C029-0a0a0a?style=flat-square&labelColor=282828)](#-whats-inside)
[![i18n: 81 languages](https://img.shields.io/badge/i18n-81%20languages-0a0a0a?style=flat-square&labelColor=282828)](#-81-languages-five-rtl)
[![RTL: Arabic · Hebrew · Persian · Urdu · Pashto](https://img.shields.io/badge/RTL-Arabic%20%C2%B7%20Hebrew%20%C2%B7%20Persian%20%C2%B7%20Urdu%20%C2%B7%20Pashto-0a0a0a?style=flat-square&labelColor=282828)](#-81-languages-five-rtl)
[![translated: OpenRouter, 2 passes](https://img.shields.io/badge/translated-OpenRouter%2C%202%20passes-6467f2?style=flat-square&labelColor=282828&logo=openrouter&logoColor=ededed)](#-how-81-languages-are-translated)
[![WCAG: 2.2 AA](https://img.shields.io/badge/WCAG-2.2%20AA-2e7d32?style=flat-square&labelColor=282828)](#-quality-what-was-checked)
[![axe-core: 0 violations](https://img.shields.io/badge/axe--core-0%20violations-2e7d32?style=flat-square&labelColor=282828)](#-quality-what-was-checked)
[![Lighthouse a11y: 100](https://img.shields.io/badge/Lighthouse%20a11y-100-2e7d32?style=flat-square&labelColor=282828&logo=lighthouse&logoColor=ededed)](#-quality-what-was-checked)
[![Lighthouse SEO: 100](https://img.shields.io/badge/Lighthouse%20SEO-100-2e7d32?style=flat-square&labelColor=282828&logo=lighthouse&logoColor=ededed)](#-quality-what-was-checked)
[![screens: 320 → 2560 px](https://img.shields.io/badge/screens-320%20%E2%86%92%202560%20px-0a0a0a?style=flat-square&labelColor=282828)](#-quality-what-was-checked)
[![old devices: lite.html](https://img.shields.io/badge/old%20devices-lite.html-ff8800?style=flat-square&labelColor=282828)](#-old-devices-get-a-simple-page)
[![theme: light · dark](https://img.shields.io/badge/theme-light%20%C2%B7%20dark-0a0a0a?style=flat-square&labelColor=282828)](#-the-site)
[![tracking: none](https://img.shields.io/badge/tracking-none-0a0a0a?style=flat-square&labelColor=282828)](#-stack)
[![cookies: none](https://img.shields.io/badge/cookies-none-0a0a0a?style=flat-square&labelColor=282828)](#-stack)
[![runtime dependencies: 0](https://img.shields.io/badge/runtime%20dependencies-0-0a0a0a?style=flat-square&labelColor=282828)](#-stack)
[![JS: 15 KB gzip](https://img.shields.io/badge/JS-15%20KB%20gzip-f7df1e?style=flat-square&labelColor=282828&logo=javascript&logoColor=282828)](site/site.js)
[![CSS: 24 KB gzip](https://img.shields.io/badge/CSS-24%20KB%20gzip-1572b6?style=flat-square&labelColor=282828&logo=css3&logoColor=ededed)](site/site.css)
[![Python: generator](https://img.shields.io/badge/Python-generator-3776ab?style=flat-square&labelColor=282828&logo=python&logoColor=ededed)](tools/build_site.py)
[![VLC: 3.0.24](https://img.shields.io/badge/VLC-3.0.24-ff8800?style=flat-square&labelColor=282828&logo=vlcmediaplayer&logoColor=ededed)](https://vlc.paulfleury.com/p/download.html)
[![vibe designed: Perplexity Computer](https://img.shields.io/badge/vibe%20designed-Perplexity%20Computer-20808d?style=flat-square&labelColor=282828&logo=perplexity&logoColor=ededed)](#-this-is-vibe-designing)

**[→ Open the site](https://vlc.paulfleury.com)** &nbsp;·&nbsp; **[→ Choose a download](https://vlc.paulfleury.com/p/vlc.html#choose)** &nbsp;·&nbsp; **[→ Design notes](https://vlc.paulfleury.com/p/design-notes.html)** &nbsp;·&nbsp; **[→ Simple version](https://vlc.paulfleury.com/lite.html)** &nbsp;·&nbsp; **[↓ Download](https://vlc.paulfleury.com/vlc-web-redesign.zip)**

</div>

---

## 📋 Summary

videolan.org carries twenty years of content: the player, libVLC, a dozen sister projects, 432 news posts, docs, the team and the non-profit. This repository is a free, unsolicited proposal to give all of it a modern, accessible home, without losing a single page.

| # | Deliverable | What it is | Where |
|---|---|---|---|
| **1** | **The full site** | VideoLAN landing + VLC home + 307 content pages, in 81 languages: 25,029 static HTML pages | [vlc.paulfleury.com](https://vlc.paulfleury.com) |
| **1b** | **VLC home** | The player's own page: download, mockups, formats, features | [`/p/vlc.html`](https://vlc.paulfleury.com/p/vlc.html) |
| **2** | **Download centre** | OS detection, every VLC 3.0.24 file from `get.videolan.org` with its SHA-256, Linux commands for 8 distributions, stores and QR codes | [`/p/download.html`](https://vlc.paulfleury.com/p/download.html) |
| **3** | **"Choose your download"** | Full-screen chooser behind *Other versions*: pick a system, or say what you need | [`/#choose`](https://vlc.paulfleury.com/p/vlc.html#choose) |
| **4** | **Settings hub** | One button for search, language, appearance and accessibility | any page, `Ctrl K` or `/` |
| **5** | **Projects & developers** | One merged hub with a searchable directory on every project page | [`/p/projects.html`](https://vlc.paulfleury.com/p/projects.html) |
| **6** | **Simple version** | A no-JavaScript page for old browsers and slow connections | [`/lite.html`](https://vlc.paulfleury.com/lite.html) |
| **7** | **The generator** | Python scripts that turn the extracted content into the site | [`tools/`](tools/) |

> [!NOTE]
> Concept work, not affiliated with or endorsed by VideoLAN. "VLC", "VideoLAN" and the cone are trademarks of VideoLAN. The MIT License covers the code and design in this repository; see [Licenses](#-license) for the content and photos.

---

## 🌐 The site

<div align="center"><a href="https://vlc.paulfleury.com"><picture><source media="(prefers-color-scheme: dark)" srcset=".github/img/home-dark.png"><img src=".github/img/home-light.png" alt="The VideoLAN landing: Open source multimedia, for everyone, with VLC in the hero" width="100%"></picture></a></div>

### 🏛️ VideoLAN, not just VLC

Since 1.1.0 the homepage presents the whole organisation (in all 81 languages since 1.4.0), built from what videolan.org already publishes (the about page, the 25 press releases, the events archive, the download statistics). VLC stays the star of the hero and links to its own home at [`/p/vlc.html`](https://vlc.paulfleury.com/p/vlc.html).

| Section | What it shows |
|---|---|
| **Projects menu** | One click on *Projects* opens all 16 projects by audience, with illustrations and roles, in every language |
| **Hero** | VideoLAN in one sentence, the detected VLC download, and a project grid: VLC as the large tile, then dav1d, x264, libVLC, libbluray, DVBlast and 10 more |
| **In numbers** | 1996 · 7 billion+ VLC downloads counted since 2005 · 16 projects · 1,062 named contributors · 15 Dev Days · 0 ads |
| **You already use VideoLAN** | The VideoLAN stack in five layers (apps, engine, codecs, discs, broadcast), with dav1d, x264 and libVLC called out |
| **VLC, our flagship** | Four promises, TV and iPhone mockups, links to downloads, features and libVLC |
| **A project, and a non-profit** | Values, then a scrollable 30-year timeline: 1996 campus TV to the 15th Dev Days in Rome |
| **Projects** | All 16 projects grouped for everyone, for broadcasters, for developers |
| **People** | Board, Dev Days 2014 photo, all 15 Video Dev Days editions (Paris to Rome), partners |
| **News, Get involved, The organisation** | Latest posts, four ways to help, donation, press, legal, privacy, security, mirrors, contact |

<div align="center"><img src=".github/img/org-menu.png" alt="The Projects menu: all 16 VideoLAN projects grouped by audience" width="100%"></div>

<table>
<tr>
<td width="50%"><img src=".github/img/org-stack.png" alt="You already use VideoLAN: the five-layer VideoLAN stack"></td>
<td width="50%"><img src=".github/img/org-story.png" alt="Thirty years timeline, 1996 to 2026, in dark mode"></td>
</tr>
<tr>
<td width="50%"><img src=".github/img/org-people.png" alt="Video Dev Days: 15 editions from Paris to Rome"></td>
<td width="50%"><img src=".github/img/vlc-page.png" alt="The VLC home: Plays everything. Tracks nothing."></td>
</tr>
</table>

### 🌍 How 81 languages are translated

Every string the site shows lives once in English. [`tools/extract_l10n.py`](tools/extract_l10n.py) renders every page in memory and collects them into one catalog, [`content/l10n/_source.json`](content/l10n/_source.json): 878 strings (about 28,000 characters) with a note on where each one appears. Interface labels, the VideoLAN landing, the VLC home, the download centre, section names, curated pages, the simple page and the movie subtitles in the mockups all come from it.

[`tools/translate_all.py`](tools/translate_all.py) then runs two passes per language through [OpenRouter](https://openrouter.ai):

1. **Translate** with a fast multilingual model (Gemini 3.8 Flash).
2. **Proofread as a native speaker** with a stronger model (Claude Sonnet 4.6), asked to rewrite anything that sounds translated: wording, rhythm, logic between sentences, consistent terms, local typography and register.

The first chunk of each language holds the core terms (navigation, *Donate*, *Download*, section names); once approved they become a glossary for every other chunk, so the same word is used everywhere. Each reply is checked for missing keys, placeholders, HTML tags, numbers and leftover English; failed chunks are repaired, split and retried. Language notes cover the details that matter (Brazilian vs European Portuguese, Traditional Chinese for Taiwan, Serbian in Cyrillic, Persian punctuation…). [`tools/polish_loanwords.py`](tools/polish_loanwords.py) then rereads non-Latin-script languages and replaces leftover English tech words with native terms.

The run is resumable and incremental: only new or changed English strings are sent again. Every call is logged with its token usage in `content/l10n/_log.jsonl`; the whole 77-language run cost about $77. The build only enables a language once its catalog is complete.

The VLC home leads with one job: get the right VLC. The main button already knows your system (Windows 64-bit, Apple Silicon or Intel, Android, iPhone), points at the real file, and shows its size. Below it: real player mockups built in HTML and CSS with Blender open movies, the format wall, features, projects, news and the non-profit. The landing and the VLC home are available in all 81 languages.

<div align="center"><img src=".github/img/mobile.png" alt="Five phone screens: English home, French download centre, the download chooser, Chinese features and Arabic home in right-to-left" width="100%"></div>

On phones every page is compact and thumb-friendly: one-column layouts, horizontally scrolling tabs, large tap targets, and QR codes swapped for direct store buttons.

---

## 🧭 What's inside

| Area | What changed | Try it |
|---|---|---|
| **Home** | Detected download, player mockups, features, projects, news, partners | [/](https://vlc.paulfleury.com) |
| **Download** | One centre for 7 systems, every format, checksums, verification, older and nightly builds | [/p/download.html](https://vlc.paulfleury.com/p/download.html) |
| **Features** | Curated landing page instead of a long list | [/p/vlc--features.html](https://vlc.paulfleury.com/p/vlc--features.html) |
| **Projects & developers** | Projects and the developer zone merged; searchable directory, project identity band, sub-page tabs | [/p/projects--dav1d.html](https://vlc.paulfleury.com/p/projects--dav1d.html) |
| **libVLC** | Bindings, code samples, licensing and who uses it, organised | [/p/vlc--libvlc.html](https://vlc.paulfleury.com/p/vlc--libvlc.html) |
| **News** | 432 posts with categories, search, yearly archives and "show more" | [/p/news.html](https://vlc.paulfleury.com/p/news.html) |
| **Team** | Jean-Baptiste Kempf, Dev Days photo, 1,062 contributors searchable by group | [/p/videolan--team.html](https://vlc.paulfleury.com/p/videolan--team.html) |
| **Support · Contribute · About** | Redesigned hubs; donation in a full-screen modal | [/p/support.html](https://vlc.paulfleury.com/p/support.html) |
| **Everything else** | Every original page kept, in a reading layout with sidebar, table of contents and progress bar | [/p/sitemap.html](https://vlc.paulfleury.com/p/sitemap.html) |

<table>
<tr>
<td width="50%"><img src=".github/img/projects.png" alt="dav1d project page with the searchable project directory"></td>
<td width="50%"><img src=".github/img/features.png" alt="Features landing page"></td>
</tr>
<tr>
<td width="50%"><img src=".github/img/libvlc.png" alt="libVLC page with bindings and code samples"></td>
<td width="50%"><img src=".github/img/team.png" alt="Team page in dark mode"></td>
</tr>
</table>

---

## ⬇️ The download chooser

<div align="center"><picture><source media="(prefers-color-scheme: dark)" srcset=".github/img/chooser-dark.png"><img src=".github/img/chooser.png" alt="The Choose your download modal with system rail, Windows options and quick intents" width="100%"></picture></div>

*Other versions* opens a full-screen chooser instead of a dropdown:

- **System rail** on the left (Windows, macOS, Linux, Android, iPhone/iPad/Apple TV, source, other systems) with a *Detected* badge; tabs you swipe on phones.
- **"What do you need?"** shortcuts: *Install on this device*, *Portable, no install*, *From an app store*, *Command line*, *Older versions*, *Source code*. Each one picks the system, scrolls to the right file and highlights it.
- **Every file is real**: installers, MSI, ZIP and 7z for x64, ARM64 and 32-bit, Universal / Apple Silicon / Intel DMGs, `tar.xz` source, all linked to `get.videolan.org` with SHA-256 fingerprints and a copy button.
- **Linux**: copy-ready commands for Ubuntu, Debian, Fedora (RPM Fusion), Arch, openSUSE, Gentoo, Flatpak and Snap.
- **Light**: the chooser lives in a `<template>` and only enters the page when opened. Shareable as [`/#choose`](https://vlc.paulfleury.com/p/vlc.html#choose). Without JavaScript, the button is a plain link to the download page.
- **Leaving the site** for a store or mirror shows a short notice first, so nobody is surprised by the jump.

---

## 🌍 81 languages, five RTL

<div align="center"><img src=".github/img/languages.png" alt="Ten phone screens of the VideoLAN landing in German, Spanish, Japanese, Korean, Hindi, Russian, Hebrew, Thai, Khmer and Swahili" width="100%"></div>

All 81 languages in the picker are live, each with 309 pages: navigation, the VideoLAN landing, the VLC home, the download centre, curated pages, settings, notices, dates and number formats. Arabic, Hebrew, Persian, Urdu and Pashto are fully mirrored right-to-left, with bidirectional-safe file names, versions and commands.

| Group | Languages |
|---|---|
| Hand-tuned since 1.3.0 | English · Français · 简体中文 · العربية |
| Europe | Deutsch · Español · Italiano · Português (Brasil, Portugal) · Nederlands · Polski · Čeština · Slovenčina · Magyar · Română · Български · Ελληνικά · Русский · Українська · Svenska · Dansk · Norsk bokmål · Suomi · Íslenska · Eesti · Latviešu · Lietuvių · Slovenščina · Hrvatski · Bosanski · Српски · Македонски · Shqip · Català · Galego · Euskara · Cymraeg · Gaeilge · Brezhoneg · Occitan · Esperanto |
| Asia & Pacific | 繁體中文 · 日本語 · 한국어 · Tiếng Việt · ไทย · Bahasa Indonesia · Bahasa Melayu · Filipino · हिन्दी · বাংলা · ਪੰਜਾਬੀ · ગુજરાતી · मराठी · தமிழ் · తెలుగు · ಕನ್ನಡ · മലയാളം · සිංහල · नेपाली · ភាសាខ្មែរ · ລາວ · မြန်မာ · Монгол · Қазақ тілі · Oʻzbekcha |
| Middle East & Caucasus | עברית · فارسی · اردو · پښتو · Türkçe · Azərbaycanca · ქართული · Հայերեն · Kurdî |
| Africa | Kiswahili · Afrikaans · አማርኛ · Hausa · Yorùbá · isiZulu |

The original articles (news, docs, project pages) are still in English inside the translated layout, with a short notice and an `EN` tag. Translations of smaller languages are machine-made and reviewed by a second model, not by people: native speakers from the VideoLAN community would be the best final check.

---

## ⚙️ Settings, in one place

<div align="center"><img src=".github/img/settings.png" alt="Settings hub with Search, Language, Appearance, Accessibility and Shortcuts tabs" width="100%"></div>

The header has one *Settings* button (`Ctrl K` or `/`) instead of four icons:

| Tab | What it does |
|---|---|
| **Search** | Instant search across all 308 pages; the index loads on first use |
| **Language** | All 81 languages, each in its own script, with the current one first |
| **Appearance** | Light, dark or system |
| **Accessibility** | Text size, high contrast, reduced motion, underlined links, wider spacing |
| **Shortcuts** | Keyboard reference |

Everything is saved on the device in `localStorage`. No cookies, no account, no tracking.

---

## ✅ Quality: what was checked

| Check | Scope | Result |
|---|---|---|
| **axe-core 4** (WCAG 2.0/2.1/2.2 A + AA, best practices) | 20 pages · light & dark · 390 and 1366 px · chooser and settings open | **0 violations** |
| **Lighthouse 12** accessibility · best practices · SEO | home, download, team, Arabic home, lite · mobile & desktop | **100 · 100 · 100** (one desktop run at 96 for a team photo) |
| **Lighthouse 12** performance | same pages | **100** desktop · **90–98** mobile |
| **Layout audit** | 21 pages × 12 widths: 320, 360, 390, 414, 600, 768, 820, 1024, 1180, 1366, 1920, 2560 px | no horizontal overflow, no text under 12 px, tap targets ≥ 24 px |
| **81-language audit** | landing, VLC home, projects hub and download centre × 81 languages × 360, 768, 1200 and 1440 px (1,296 renders) | no overflow, no clipped text, no text under 11.5 px, no tap target under 24 px |
| **axe-core in 22 languages** | 29 pages incl. all five RTL languages, Indic, Thai, Khmer, Burmese, Georgian, Armenian, CJK · light & dark · 390 and 1366 px | **0 violations** |
| **Links** | every `href` and `src` in the build | 0 broken internal links |
| **Old-browser redirect** | live site, browser identities and disabled features | see below |

Effects (reveal, glow, parallax, mockup animations) only run on capable devices: they are gated behind an `html.fx` class that requires modern CSS, `IntersectionObserver`, and no *reduced motion* preference.

---

## 🧓 Old devices get a simple page

<div align="center"><img src=".github/img/lite.png" alt="The simple no-JavaScript version: downloads, sizes and SHA-256 for every file" width="80%"></div>

Old or limited browsers are sent to [`lite.html`](https://vlc.paulfleury.com/lite.html) (one per language): plain HTML, inline CSS, no JavaScript, light and dark. It still lists every download with its size and SHA-256, the Linux commands, store links, source, older versions, donation and help. *Open the full site* (`?full=1`) opts out for that browser.

| Rule | Where | Catches |
|---|---|---|
| Feature test | inline in every `<head>` | no `querySelector`, `addEventListener`, `Promise`, `CSS.supports`, custom properties, grid or sticky |
| Browser list | same script | IE / Trident, Opera Mini / Presto, UC Browser, KaiOS, BlackBerry, Windows Phone, Symbian, consoles, Android ≤ 4, iOS ≤ 11, Firefox ≤ 51, Chrome ≤ 56 |
| Conditional comment | `<!--[if IE]>` | IE 5–9, even with JavaScript off |
| Server rules | [`dist/.htaccess`](tools/build_site.py) | the same list, for Apache hosts that honour `.htaccess` |

Tested on the live site: IE 11, iOS 9 Safari, iPad iOS 11, Android 4.4, KaiOS 2.5 and Windows Phone land on the simple page; Chrome 130 and iOS 17 Safari get the full site; an engine without CSS grid or without `Promise` is redirected too.

---

## 🧰 Stack

- **Generator**: Python 3 standard library. [`tools/build_site.py`](tools/build_site.py) renders every page from the extracted content in [`content/`](content/), the curated landing pages in [`tools/curated.py`](tools/curated.py) and the strings in [`tools/i18n.py`](tools/i18n.py).
- **Front end**: one stylesheet ([`site/site.css`](site/site.css)), one script ([`site/site.js`](site/site.js)), one SVG sprite ([`site/icons.svg`](site/icons.svg)). No framework, system fonts only (no web fonts to download), no runtime dependencies.
- **Images**: WebP with JPEG fallback, 640 and 1280 px, lazy-loaded, sized by `srcset`.
- **Caching**: assets are versioned with a content hash (`site.css?v=…`); pages check `version.json` once and refresh themselves if a host cached an old copy.
- **SEO**: absolute `hreflang` alternates with `x-default`, canonical URLs, Open Graph cards.
- **Optional**: `npx terser` minifies `site.js` when available; the build works without it.

Details: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** · deploy: **[docs/DEPLOY.md](docs/DEPLOY.md)** · history: **[CHANGELOG.md](CHANGELOG.md)**

```
site/               site.css · site.js · icons.svg · media/ (film stills, QR codes, portraits, og.png)
content/            pages.json · news.json, extracted from videolan.org · l10n/ (one catalog per language)
tools/
  build_site.py     generator: shell, home, download centre, chooser, content pages, l10n, vlc-web-redesign.zip
  curated.py        landing pages: features, projects & developers, team, libVLC, news, support…
  i18n.py           81 languages (names, RTL, scripts), EN · FR · ZH · AR tables, catalog loader, dates and numbers
  extract_l10n.py   collects every English string into content/l10n/_source.json
  translate_all.py  OpenRouter translate → native proofread for every language, resumable
  polish_loanwords.py  replaces leftover English tech words in non-Latin scripts
  org_strings.py    landing source strings; translate_org.py for the hand-tuned FR · ZH · AR landing
  vlsite.py         content model, link rewriting, navigation order
  lite.py           the simple no-JavaScript page
  extract.py        turns the saved videolan.org pages into content/*.json
  deploy_ftp.py     incremental FTP mirror of dist/
  shots.py          regenerates the screenshots in .github/img/
shared/             favicon
docs/               ARCHITECTURE.md · DEPLOY.md
```

---

## 💻 Run it locally

```bash
git clone https://github.com/paulfxyz/vlc-web-redesign.git
cd vlc-web-redesign
python3 tools/build_site.py           # writes dist/: EN at the root, one folder per language (fr/ de/ ja/ pt-br/ …)
python3 -m http.server -d dist 8765   # open http://localhost:8765
```

Screenshots for this README:

```bash
pip install playwright && playwright install chromium
python3 tools/shots.py                # with the local server running
```

---

## 🚀 Deploy

`dist/` is a plain folder of static files: any web server, object storage or CDN works.

```bash
VLC_FTP_PASS='…' python3 tools/deploy_ftp.py   # what runs vlc.paulfleury.com (SiteGround)
```

It uploads only changed files, removes deleted ones and never stores the password. Host-specific notes (proxy cache, firewall, `.htaccess`) are in [docs/DEPLOY.md](docs/DEPLOY.md).

---

## 🤖 This is vibe designing

No design tool was opened for this project. Every page, mockup and interaction was designed through conversation: Paul set the goal ("the best possible site for VLC, ever"), the taste and the priorities, then pushed for more (real mockups, a better download flow, a settings hub, the projects merge, a stricter audit). An AI agent turned each request into code, rendered it in a headless browser, looked at the screenshots, fixed what looked wrong and shipped.

- **Built from the real site.** Every videolan.org page was saved, cleaned and re-rendered, so nothing is invented and nothing is lost.
- **Look, then fix.** Each change was checked with screenshots at phone, tablet and desktop sizes, in light and dark, left-to-right and right-to-left, then with axe-core and Lighthouse.
- **Human in the loop.** Scope, taste and every publish step came from Paul; the agent handled research, drafting, building, QA and deployment.

| Role | Tool |
|---|---|
| Agent platform | [Perplexity Computer](https://www.perplexity.ai/computer) |
| Rendering, screenshots, layout audit | Chromium via [Playwright](https://playwright.dev) |
| Accessibility | [axe-core](https://github.com/dequelabs/axe-core), [Lighthouse](https://developer.chrome.com/docs/lighthouse) |
| Badges | [shields.io](https://shields.io) |

---

## 🙋 Who made this

[Paul Fleury](https://paulfleury.com), a French internet entrepreneur in Lisbon and a VLC user for twenty years. It comes with its sibling, [VLC Logotype](https://github.com/paulfxyz/vlc-logotype): 100 icon concepts for the player ([paulfleury.com/vlc](https://paulfleury.com/vlc/)).

Both are gifts. VideoLAN can take any part of them, change everything, or ignore them.

---

## 📄 License

- **Code and design** (HTML, CSS, JavaScript, Python, SVG icons and illustrations): [MIT](LICENSE).
- **Text content** in `content/` comes from [videolan.org](https://www.videolan.org) and belongs to VideoLAN and its authors.
- **VLC, VideoLAN and the cone** are trademarks of VideoLAN. This is an independent design proposal.
- **Film stills** (Big Buck Bunny, Sintel, Elephants Dream, Tears of Steel, Caminandes) © Blender Foundation, [CC BY](https://creativecommons.org/licenses/by/3.0/).
- **Portrait of Jean-Baptiste Kempf** by Axelle Manfrini, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), via Wikimedia Commons.
- **VideoLAN Dev Days 2014 photo** from images.videolan.org.
