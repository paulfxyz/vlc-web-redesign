# Deploy

**Single source of truth: https://vlc.paulfleury.com** · code: https://github.com/paulfxyz/vlc-web-redesign

```
python3 tools/build_site.py                          # build dist/ (81 languages, about 1.3 GB)
VLC_FTP_PASS='…' python3 tools/deploy_ftp.py         # mirror dist/ → ftp.paulfleury.com:/vlc.paulfleury.com/public_html
VLC_FTP_PASS='…' python3 tools/deploy_ftp.py --full  # force re-upload of every file
```

- FTP host `ftp.paulfleury.com`, port 21; user in `VLC_FTP_USER`, password in `VLC_FTP_PASS` (both kept out of the repo).
- A first full upload of the 81-language build is about 25,000 files; later deploys only send what changed.
- Uploads only changed files (MD5 manifest in `.ftp-manifest.json`, git-ignored) and removes files deleted locally.
- The host (SiteGround) shows a bot challenge to some automated clients; real browsers pass.
- Old-browser redirect to `lite.html` is done in-page (feature test + UA list in `<head>`, plus an IE conditional comment). `.htaccess` adds the same rules and no-cache headers for HTML/JSON where the host applies them.
- SiteGround also answers 403 for a file named `dump.zip` (backup-name protection), so the archive is `vlc-web-redesign.zip`.
- SiteGround's firewall answers Opera Mini with 403 and drops very old Chrome UAs (e.g. Chrome 49/XP) before the page loads; fix in SiteGround Site Tools > Security if those visitors matter.
- Static assets are cached for a year by the host, so the build appends `?v=<hash>` to site.css/site.js/l10n.js/icons.svg/search.js.
- vlc-web-redesign.pplx.app is a legacy preview and is no longer updated.
- SiteGround's proxy cache can keep serving an old copy of `/` after an upload (seen 2026-10-02: `/index.html` new, `/` stale). Flush it in Site Tools > Speed > Caching > Dynamic Cache, or switch Dynamic Cache off for vlc.paulfleury.com. Pages also carry `data-v` and check `/version.json`, so a stale copy in a visitor's browser refreshes itself once.
- Source of truth for code: https://github.com/paulfxyz/vlc-web-redesign (MIT).
