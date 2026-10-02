# Architecture

The site is generated once by Python and served as plain files. There is no server code, database or client framework.

```
videolan.org ──(saved pages)──▶ tools/extract.py ──▶ content/pages.json · news.json
                                                          │
tools/i18n.py (strings) ─┐                                ▼
tools/curated.py (hubs) ─┼──▶ tools/build_site.py ──▶ dist/  (1,236 HTML pages + assets)
site/ (css · js · svg)  ─┘            │                    │
tools/lite.py (simple page) ──────────┘                    ├─▶ tools/deploy_ftp.py ──▶ vlc.paulfleury.com
                                                           └─▶ dump.zip
```

## Content model — `tools/vlsite.py`

- Loads `content/pages.json` (one record per original URL: title, section, cleaned HTML, headings) and `content/news.json`.
- `rewrite()` turns every videolan.org link into a local page when one exists, otherwise keeps the external URL (which then gets the leave-site notice).
- `SECTIONS` defines the eleven content sections and the order pages appear in sidebars and the sitemap. *Projects & developers* covers Projects, VLMa, Developers and Translation.

## Generator — `tools/build_site.py`

| Function | Output |
|---|---|
| `head()` / `foot()` | shared shell: old-browser guard, theme bootstrap, header, settings button, footer, `hreflang`, canonical, Open Graph |
| `home()` | homepage, mockups, and the `<template id="dlt">` holding the download chooser |
| `download_block()` | the download centre, reused by the download page and the chooser |
| `content_page()` | every other page: reading layout, or the project layout (`band()` + `directory()`) for projects |
| `l10n_js()` | per-language strings used by `site.js` |
| `write()` | post-processing: asset versioning, empty-link removal, focusable `<pre>` |
| `main()` | builds all languages, `search.js` index, `lite.html`, `.htaccess`, `version.json`, redirects, `dump.zip` |

Curated landing pages live in `tools/curated.py`; every string shown to users lives in `tools/i18n.py` (or in the `X` table at the top of `build_site.py`) with four translations side by side.

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
