# Changelog

All notable changes to this project. Dates are in Europe/Lisbon time.

## [1.4.0] — 2026-11-22

All 81 languages. Every language in the picker is now a complete site.

### Added
- 77 new languages, each with all 309 pages: interface, VideoLAN landing, VLC home, download centre, section names, curated pages, the simple page and the mockup subtitles. 81 languages, 25,029 pages in total.
- Right-to-left layouts for Hebrew, Persian, Urdu and Pashto, alongside Arabic.
- `tools/extract_l10n.py`: renders every page in memory and collects all 878 English strings (about 28,000 characters) with translator context into `content/l10n/_source.json`.
- `tools/translate_all.py`: two OpenRouter passes per language, Gemini 3.8 Flash drafts and Claude Sonnet 4.6 rewrites as a native-speaking editor. Core terms are approved first and reused as a glossary; replies are checked for keys, placeholders, tags, numbers and leftover English; failing chunks are repaired, split and retried. Resumable and incremental, with per-call usage in `content/l10n/_log.jsonl`.
- `tools/polish_loanwords.py`: a final pass on non-Latin scripts that replaces leftover English tech words with native terms.
- Language notes for regional variants and scripts (pt-BR / pt-PT, zh-Hant for Taiwan, Serbian Cyrillic, Uzbek Latin, Persian punctuation…).
- Locale dates and number grouping for every language (Babel), no spaces between words for Chinese and Japanese.

### Changed
- `tools/i18n.py` now describes all 81 languages (native name, English name, URL folder, direction, script) and loads a catalog per language; the build enables a language only when its catalog is complete.
- Language folders use lowercase codes (`pt-br/`, `zh-hant/`); `hreflang` alternates, the settings language list and the footer cover every language.
- Design notes describe the 81-language site.

### Fixed
- Long headlines shrink to fit instead of breaking inside a word (Malayalam, Tamil, German…); taller line height and no letter-spacing for complex scripts.
- Breadcrumb *Home* links keep a 24 px target even when the word is one character wide.
- Organisation tiles wrap very long words ("Конфиденциальность") instead of pushing the arrow out.
- Project descriptions are no longer cut to two lines on tablets.
- Header navigation switches to the compact menu whenever the labels do not fit, instead of overflowing on wide screens in languages with long words (Armenian, Georgian, Malayalam, Kazakh…).

### Checked
- Layout audit: landing, VLC home, projects hub and download centre in all 81 languages at 360, 768, 1200 and 1440 px (1,296 renders): no overflow, no clipped text, no text under 11.5 px, no tap target under 24 px.
- axe-core: 0 violations on 29 pages in 22 languages (all right-to-left languages, Indic, Thai, Khmer, Burmese, Georgian, Armenian, CJK), light and dark, phone and desktop.
- Translation cost for the 77 new languages: about $77 on OpenRouter.

## [1.3.0] — 2026-11-22

The VideoLAN landing in all four languages.

### Added
- French, Chinese and Arabic VideoLAN landings: every string of the landing, the Projects menu, the brand line and the five latest news cards (172 landing strings + 10 news strings per language).
- `tools/org_strings.py`: one English source table with translator context; `content/org_i18n.json` holds the translations.
- `tools/translate_org.py`: two OpenRouter passes per language. A fast multilingual model drafts (Gemini 3.8 Flash), then a stronger model rereads as a native-speaking editor and rewrites for natural wording, rhythm and logic (Claude Sonnet 4.6). Validates keys, placeholders and numbers, applies French typography, only re-sends changed strings, and logs usage.
- The build refuses to switch a language to the landing until every string is translated.

### Fixed
- Right-to-left alignment of Latin project names in Arabic cards, tiles and menu.
- Licence and year line under each project no longer breaks.
- Numbers strip keeps big figures on one line ("7 milliards+").
- Locale number grouping (French "1 062").

### Checked
- Layout audit on 7 page types × 4 languages × 13 widths (320–2560 px): no overflow, no text under 11.5 px, no target under 24 px, no clipped text.
- axe-core: 0 violations on every landing, light and dark, phone and desktop, with the Projects menu open.

## [1.2.0] — 2026-11-22

Every VideoLAN project gets the spotlight, with VLC still first.

### Added
- Projects menu: a full panel under *Projects* listing all 16 projects by audience, each with its illustration and a one-line role, in all four languages; closes on Escape, outside click or focus leaving.
- Hero project grid on the English landing: VLC as the large tile, plus dav1d, x264, libVLC, libbluray, DVBlast and "+10 more projects".

### Changed
- Hero text presents VideoLAN as a non-profit and a community, then VLC and the codecs, disc libraries and broadcast tools.
- "You already use VideoLAN" now comes before the VLC band.
- Navigation order: VLC, Projects, Download, News, Support, Contribute, About.

## [1.1.0] — 2026-11-22

VideoLAN, not just VLC. The English homepage now presents the whole organisation.

### Added
- New VideoLAN landing (`index.html`, English): hero with VLC as the star, numbers strip, VLC flagship band, "You already use VideoLAN" stack diagram, values and a scrollable 30-year timeline, 16 projects by audience, board, all 15 Video Dev Days editions, partners, news, get involved, organisation links.
- Facts drawn from videolan.org itself: the about page, press releases (open-sourcing 2001, LGPL 2011, Kickstarter 2012, iOS 2013, Apple TV 2016, AOMedia 2017, 20 years 2021), the events archive and the download statistics (7,092,269,654 downloads counted on 1 October 2026).
- Dedicated VLC home at `/p/vlc.html` in every language; "VLC" is now the first navigation item.
- README screenshots for the landing sections; `tools/shots.py` can scroll to a section.

### Changed
- Brand subtitle reads "Open source multimedia" in English.
- The download chooser template is shared between the VLC home and the landing.
- French, Chinese and Arabic homepages stay on the VLC home until the landing is translated.

## [1.0.0] — 2026-10-02

First public release, live at [vlc.paulfleury.com](https://vlc.paulfleury.com).

### Site
- Every videolan.org page (308 + home) rebuilt as static HTML in English, French, Chinese and Arabic (RTL): 1,236 pages.
- Homepage with OS-detected download, real VLC desktop and mobile mockups (Blender open movies), format wall, features, projects and news.
- Curated landing pages: features, projects & developers, team, libVLC, news, support, contribute, about.
- Reading layout for every other page: sidebar, table of contents, reading progress, breadcrumbs.
- Settings hub (search, language, appearance, accessibility, shortcuts) behind one button, `Ctrl K` or `/`.
- Dismissible proposal ribbon, remembered once closed.
- Full-screen donation modal; notice before leaving for external sites.

### Downloads
- Download centre for 7 systems with every VLC 3.0.24 file from `get.videolan.org`, sizes and SHA-256 fingerprints.
- Linux commands for 8 distributions; Microsoft Store, Google Play, F-Droid, App Store, Flathub and Snap.
- QR codes for mobile stores on desktop.
- *Other versions* opens a full-screen **Choose your download** modal with a system rail and "What do you need?" shortcuts; deep link `/#choose`.

### Projects & developers
- Projects and the developer zone merged into one hub.
- Searchable project directory on every project and developer page, grouped by audience, with nested sub-pages.
- Project identity band (illustration, tagline, language, licence, platforms, year, source link) and sub-page tabs.
- Old `section--developers` URL redirects to the hub.

### Accessibility and quality
- axe-core: 0 WCAG 2.2 A/AA and best-practice violations on 20 pages, light and dark, phone and desktop.
- Lighthouse: accessibility, best practices and SEO 100 (one desktop run at 96); performance 100 desktop, 90–98 mobile.
- Layout audit at 12 widths from 320 to 2560 px: no overflow, text ≥ 12 px, tap targets ≥ 24 px.
- Effects gated behind capability checks and *reduced motion*.

### Old devices
- `lite.html` per language: no JavaScript, every download with size and SHA-256.
- In-page feature test and browser list, IE conditional comment, and `.htaccess` rules; `?full=1` opts out.

### Infrastructure
- Python generator, content-hash asset versioning, self-refresh via `version.json` when a host serves a stale page.
- Absolute `hreflang` with `x-default`, canonical URLs, Open Graph images.
- Incremental FTP deploy, `vlc-web-redesign.zip` of the whole site, screenshot generator for the README.
