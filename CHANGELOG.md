# Changelog

All notable changes to this project. Dates are in Europe/Lisbon time.

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
