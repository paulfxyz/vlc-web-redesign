# VideoLAN web redesign

An independent, free redesign proposal for [videolan.org](https://www.videolan.org), offered to the VideoLAN team under the MIT license.

**Live:** https://vlc.paulfleury.com

## What it is

- A single static HTML5 site: no framework, no tracking, no build-time dependencies beyond Python 3.
- All 1,236 pages of videolan.org rebuilt from the original content, in English, French, Chinese and Arabic (right-to-left).
- A real download centre for VLC 3.0.24: OS detection, every installer and archive from `get.videolan.org` with SHA-256 fingerprints, Linux commands for eight distributions, store links and QR codes, plus a full-screen "Choose your download" chooser.
- Accessible by default (WCAG 2.2 AA, axe-core clean, Lighthouse accessibility 100): keyboard and screen-reader friendly, high contrast, text size, reduced motion, link and spacing options, light and dark themes.
- Lightweight and progressive: effects only run on capable devices, and old or limited browsers (IE, old iOS/Android, KaiOS, feature-poor engines) are sent to a simple no-JavaScript page (`lite.html`).
- A merged "Projects & developers" area with a searchable directory, project identity bands and sub-page tabs; curated landing pages for features, team, libVLC, news, support and contribute.

## Structure

```
site/          site.css, site.js, icons.svg, media/ (images, QR codes)
tools/         build_site.py (generator), curated.py (landing pages), i18n.py (strings),
               vlsite.py (content model), lite.py (simple page), extract.py, deploy_ftp.py
content/       pages.json, news.json — content extracted from videolan.org
shared/        favicon
```

## Build

```sh
python3 tools/build_site.py          # writes dist/ (EN at root, fr/ zh/ ar/)
python3 -m http.server -d dist 8765  # preview locally
```

`npx terser` is used to minify `site.js` when available; the build works without it. See `DEPLOY.md` for the FTP deploy to vlc.paulfleury.com.

## Licenses

- **Code and design** (HTML, CSS, JavaScript, Python, SVG icons and illustrations): MIT, see `LICENSE`.
- **Text content** in `content/` comes from videolan.org and belongs to VideoLAN and its authors.
- **VLC, VideoLAN and the cone logo** are trademarks of VideoLAN.
- **Film stills** (Big Buck Bunny, Sintel, Elephants Dream, Tears of Steel, Caminandes) © Blender Foundation, CC BY.
- **Portrait of Jean-Baptiste Kempf** by Axelle Manfrini, CC BY-SA 4.0, via Wikimedia Commons.
- **VideoLAN Dev Days 2014 photo** from images.videolan.org.

This is not an official VideoLAN project.
