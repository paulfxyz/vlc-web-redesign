# Architecture

The site is generated once by Python and served as plain files. There is no server code, database or client framework.

```
videolan.org ──(saved pages)──▶ tools/extract.py ──▶ content/pages.json · news.json
                                                          │
tools/i18n.py + content/l10n/ ─┐                                ▼
tools/curated.py (hubs) ─┼──▶ tools/build_site.py ──▶ dist/  (25,029 HTML pages + assets)
site/ (css · js · svg)  ─┘            │                    │
tools/lite.py (simple page) ──────────┘                    ├─▶ tools/deploy_ftp.py ──▶ vlc.paulfleury.com
                                                           └─▶ vlc-web-redesign.zip
```

## Content model — `tools/vlsite.py`

- Loads `content/pages.json` (one record per original URL: title, section, cleaned HTML, headings) and `content/news.json`.
- `rewrite()` turns every videolan.org link into a local page when one exists, otherwise keeps the external URL (which then gets the leave-site notice).
- `SECTIONS` defines the eleven content sections and the order pages appear in sidebars and the sitemap. *Projects & developers* covers Projects, VLMa, Developers and Translation.

## Generator — `tools/build_site.py`

| Function | Output |
|---|---|
| `head()` / `foot()` | shared shell: old-browser guard, theme bootstrap, header, settings button, footer, `hreflang`, canonical, Open Graph |
| `home(c, slug)` | VLC home (`p/vlc.html` everywhere, and `index.html` for languages without the landing), mockups |
| `org_home()` | English VideoLAN landing (`index.html`): stack, timeline, projects, people, Dev Days (`VDD`) |
| `org_strings.py` / `translate_org.py` | landing source strings, and the OpenRouter translate → native proofread pipeline writing `content/org_i18n.json` |
| `mega()` | the *Projects* menu panel (all 16 projects, `ROLE` one-liners, translated in every language) |
| `dl_template()` | the `<template id="dlt">` holding the download chooser, shared by both homes |
| `download_block()` | the download centre, reused by the download page and the chooser |
| `content_page()` | every other page: reading layout, or the project layout (`band()` + `directory()`) for projects |
| `l10n_js()` | per-language strings used by `site.js` |
| `write()` | post-processing: asset versioning, empty-link removal, focusable `<pre>` |
| `main()` | builds all languages, `search.js` index, `lite.html`, `.htaccess`, `version.json`, redirects, `vlc-web-redesign.zip` |

Curated landing pages live in `tools/curated.py`; every string shown to users lives in `tools/i18n.py` (or in the `X` table at the top of `build_site.py`) with the English, French, Chinese and Arabic versions side by side.

## Languages — `tools/i18n.py`, `content/l10n/`

- `ALL` lists the 81 languages (code, native name, English name); `META` adds the URL folder (lowercase code), direction (`RTL`: ar, he, fa, ur, ps) and `NOSPACE` scripts (zh, zh-Hant, ja).
- English, French, Chinese and Arabic keep their hand-written tables. Every other language reads `content/l10n/<code>.json`, a flat catalog keyed by `t:` (interface), `s:` (section names and ledes), `p:` (curated strings, keyed by a hash of the English), `o:` (landing and news cards), `l:` (simple page) and `u:` (mockup subtitles). `t()`, `sec()`, `curated.P`, `org_strings.ot` and `lite.py` fall back to it.
- `complete()` checks coverage; `LANGS` (the languages the build writes) is the four base languages plus every complete catalog.
- `date()` and `num()` use Babel for each locale.

Pipeline:

```
tools/extract_l10n.py  ──▶ content/l10n/_source.json   (878 English strings + context)
tools/translate_all.py ──▶ content/l10n/<code>.json     (draft → native-editor rewrite → checks → repair)
                           content/l10n/_hashes/<code>.json · _log.jsonl (source hashes, usage)
tools/polish_loanwords.py  native terms for leftover English words in non-Latin scripts
```


## Front end — `site/`

- **`site.css`**: design tokens (`--or` orange, surfaces, radii), light and dark themes via `html[data-theme]`, accessibility modes via `data-size`, `data-contrast`, `data-motion`, `data-links`, `data-spacing`. Effects only under `html.fx`.
- **`site.js`**: one IIFE, no dependencies. Settings hub, search (lazy `search.js`), OS and architecture detection, download rail and chooser, copy buttons, filters, leave-site and donation modals, QR codes, reveal effects, self-refresh.
- **`icons.svg`**: one sprite, referenced as `icons.svg?v=<hash>#i-name`.

## Progressive enhancement

1. Inline `<head>` script: redirects old engines to `lite.html`, applies saved theme and accessibility settings before first paint, sets `html.js` and (if capable) `html.fx`.
2. Without JavaScript every page still renders and every download is a normal link; the chooser button falls back to the download page.
3. With JavaScript the site adds detection, modals, search and effects.

## Caching

The host caches static files for a long time, so the build appends a content hash to `site.css`, `site.js`, `l10n.js`, `icons.svg` and `search.js`. Each page carries `data-v`; `site.js` compares it with `/version.json` once per page and session and refreshes a stale copy.
