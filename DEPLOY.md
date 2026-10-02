# Deploy

**Single source of truth: https://vlc.paulfleury.com**

```
python3 tools/build_site.py                          # build dist/ (EN + FR/ZH/AR)
VLC_FTP_PASS='…' python3 tools/deploy_ftp.py         # mirror dist/ → ftp.paulfleury.com:/vlc.paulfleury.com/public_html
VLC_FTP_PASS='…' python3 tools/deploy_ftp.py --full  # force re-upload of every file
```

- FTP host `ftp.paulfleury.com`, user `vlc2@paulfleury.com`, port 21 (password kept out of the repo).
- Uploads only changed files (MD5 manifest in `.ftp-manifest.json`, git-ignored) and removes files deleted locally.
- The host (SiteGround) shows a bot challenge to some automated clients; real browsers pass.
- vlc-web-redesign.pplx.app is a legacy preview and is no longer updated.
