#!/usr/bin/env python3
"""Mirror dist/ to vlc.paulfleury.com/public_html over FTP (parallel, skips unchanged by size+manifest)."""
import ftplib, os, sys, pathlib, hashlib, json, threading, queue
HOST, USER = 'ftp.paulfleury.com', 'vlc2@paulfleury.com'
PASS = os.environ.get('VLC_FTP_PASS')
REMOTE = '/vlc.paulfleury.com/public_html'
DIST = pathlib.Path(__file__).resolve().parent.parent / 'dist'
MAN = DIST.parent / '.ftp-manifest.json'
def conn():
    f = ftplib.FTP(); f.connect(HOST, 21, timeout=60); f.login(USER, PASS); return f
def main():
    old = json.loads(MAN.read_text()) if MAN.exists() and '--full' not in sys.argv else {}
    files = [p for p in DIST.rglob('*') if p.is_file()]
    new = {str(p.relative_to(DIST)): hashlib.md5(p.read_bytes()).hexdigest() for p in files}
    todo = [k for k, v in new.items() if old.get(k) != v]
    print(f'{len(files)} files, {len(todo)} to upload')
    f = conn()
    dirs = sorted({str(pathlib.PurePosixPath(k).parent) for k in todo if '/' in k}, key=len)
    for d in dirs:
        path = REMOTE
        for part in d.split('/'):
            path += '/' + part
            try: f.mkd(path)
            except ftplib.error_perm: pass
    try: f.delete(REMOTE + '/Default.html')
    except ftplib.error_perm: pass
    f.quit()
    q = queue.Queue(); [q.put(k) for k in todo]; done = []; errs = []
    def worker():
        c = conn()
        while True:
            try: k = q.get_nowait()
            except queue.Empty: break
            for attempt in range(3):
                try:
                    with open(DIST / k, 'rb') as fh: c.storbinary(f'STOR {REMOTE}/{k}', fh)
                    done.append(k); break
                except Exception as ex:
                    try: c.quit()
                    except Exception: pass
                    c = conn()
                    if attempt == 2: errs.append((k, str(ex)))
        try: c.quit()
        except Exception: pass
    ts = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    # remove remote files that no longer exist locally
    stale = [k for k in old if k not in new]
    if stale:
        c = conn()
        for k in stale:
            try: c.delete(f'{REMOTE}/{k}')
            except Exception: pass
        c.quit()
    kept = {k: new[k] for k in new if k not in [e[0] for e in errs]}
    MAN.write_text(json.dumps(kept))
    print('uploaded', len(done), 'errors', len(errs), errs[:5], 'removed', len(stale))
if __name__ == '__main__': main()
