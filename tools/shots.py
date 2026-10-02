#!/usr/bin/env python3
"""Regenerate the README screenshots in .github/img/ from a local build.

    python3 tools/build_site.py
    python3 -m http.server -d dist 8765 &
    python3 tools/shots.py            # needs: pip install playwright && playwright install chromium
"""
import asyncio, base64, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / '.github' / 'img'
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/'
WIN = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
IPH = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
# name, path, width, height, scheme, ua, click-selector, scale
SHOTS = [
    ('home-light', 'index.html', 1440, 900, 'light', WIN, None, 1),
    ('home-dark', 'index.html', 1440, 900, 'dark', WIN, None, 1),
    ('chooser', 'index.html', 1440, 900, 'light', WIN, 'button.cta-alt', 1),
    ('chooser-dark', 'fr/index.html', 1440, 900, 'dark', WIN, 'button.cta-alt', 1),
    ('settings', 'index.html', 1440, 900, 'dark', WIN, 'button.setb', 1),
    ('download', 'p/download.html', 1440, 900, 'light', WIN, None, 1),
    ('projects', 'p/projects--dav1d.html', 1440, 900, 'light', WIN, None, 1),
    ('features', 'p/vlc--features.html', 1440, 900, 'light', WIN, None, 1),
    ('team', 'p/videolan--team.html', 1440, 900, 'dark', WIN, None, 1),
    ('libvlc', 'p/vlc--libvlc.html', 1440, 900, 'light', WIN, None, 1),
    ('lite', 'lite.html', 1280, 800, 'light', WIN, None, 1),
    ('m-en', 'index.html', 390, 844, 'light', IPH, None, 2),
    ('m-fr', 'fr/p/download.html', 390, 844, 'dark', IPH, None, 2),
    ('m-zh', 'zh/p/vlc--features.html', 390, 844, 'light', IPH, None, 2),
    ('m-ar', 'ar/index.html', 390, 844, 'dark', IPH, None, 2),
    ('m-chooser', 'index.html', 390, 844, 'light', IPH, 'button.cta-alt', 2),
]

def b64(p): return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()

COMPOSE = {
 'banner': (1600, 820, lambda s: f'''<body style="margin:0;width:1600px;height:820px;overflow:hidden;background:radial-gradient(1200px 600px at 80% 0%,#3a2207,#140f0a 60%);font-family:system-ui,-apple-system,'Segoe UI',sans-serif;color:#fff">
<div style="position:absolute;left:80px;top:96px;width:560px">
<svg width="84" height="84" viewBox="0 0 64 64"><path d="M26 6h12l3 12H23z" fill="#ff8800"/><path d="M22.4 21h19.2l2.6 11H19.8z" fill="#fff"/><path d="M19 35h26l3 12H16z" fill="#ff8800"/><rect x="8" y="50" width="48" height="8" rx="3" fill="#ff8800"/></svg>
<div style="font-size:20px;letter-spacing:.14em;text-transform:uppercase;color:#ffb366;font-weight:700;margin:28px 0 14px">Redesign proposal</div>
<div style="font-size:64px;line-height:1.02;font-weight:800;letter-spacing:-.03em">videolan.org,<br><span style="color:#ff8800">rebuilt.</span></div>
<div style="font-size:23px;line-height:1.45;color:#d9cfc3;margin-top:24px">1,236 pages · English, Français, 中文, العربية · download chooser · WCAG 2.2 AA · zero dependencies</div>
<div style="font-size:21px;color:#ffb366;margin-top:28px;font-weight:700">vlc.paulfleury.com</div></div>
<img src="{s['home-light']}" style="position:absolute;left:690px;top:90px;width:900px;border-radius:14px;box-shadow:0 40px 90px rgba(0,0,0,.6)">
<img src="{s['m-ar']}" style="position:absolute;left:1330px;top:300px;width:230px;border-radius:30px;border:6px solid #000;box-shadow:0 30px 70px rgba(0,0,0,.7)">
</body>'''),
 'mobile': (1600, 900, lambda s: '<body style="margin:0;width:1600px;height:900px;background:#efe9e1;display:flex;gap:26px;align-items:center;justify-content:center">' + ''.join(
     f'<img src="{s[k]}" style="width:262px;border-radius:32px;border:7px solid #111;box-shadow:0 24px 60px rgba(0,0,0,.25)">' for k in ('m-en', 'm-fr', 'm-chooser', 'm-zh', 'm-ar')) + '</body>'),
}

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=__import__('os').environ.get('CHROME') or None)
        for name, path, w, h, scheme, ua, click, scale in SHOTS:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=scale, color_scheme=scheme,
                                      user_agent=ua, is_mobile=w < 700, has_touch=w < 700, reduced_motion='reduce')
            await ctx.add_init_script("try{localStorage.setItem('vl-rib','off')}catch(e){}")
            pg = await ctx.new_page()
            await pg.goto(BASE + path, wait_until='networkidle'); await pg.wait_for_timeout(400)
            if click: await pg.click(click); await pg.wait_for_timeout(700)
            await pg.screenshot(path=str(OUT / f'{name}.png'))
            await ctx.close(); print('shot', name)
        shots = {f.stem: b64(f) for f in OUT.glob('*.png')}
        for name, (w, h, html) in COMPOSE.items():
            pg = await b.new_page(viewport={'width': w, 'height': h})
            await pg.set_content(html(shots)); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(OUT / f'{name}.png')); await pg.close(); print('compose', name)
        for f in OUT.glob('m-*.png'): f.unlink()   # phones only live inside the composites
        await b.close()

asyncio.run(main())
