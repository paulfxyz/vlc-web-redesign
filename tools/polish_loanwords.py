"""Replace leftover English words in non-Latin-script catalogs with native wording.
Only strings with lowercase English words (outside product names) are re-sent to the editor model."""
import json, re, sys, concurrent.futures as cf
sys.path.insert(0, 'tools'); sys_args = sys.argv[1:]; sys.argv = sys.argv[:1]
import translate_all as T, i18n as I
S = json.load(open('content/l10n/_source.json'))['strings']
K = re.compile(T.KEEP.pattern + r'|media player|lib[a-z0-9]+|videolan|libera|multicat|bitstream|dvblast|webvtt|tarball|teletext|cookies?|demux|ipod|touch')
SYS = """You are a senior native {name} software localizer. Each string below is already translated but still contains English words in Latin script.
Replace every common English word with the natural {name} term that native software and tech journalism in {name} use (e.g. streaming, build, library, closed captions, merge request, distribution, codec, binding).
Keep in Latin script only: product and project names, brand names, file formats, acronyms (AV1, DVB, MPEG, SRT, CPU…), and code. If a native term really does not exist, keep the English word but add nothing else.
Keep meaning, placeholders, HTML tags and numbers unchanged. Return ONLY a JSON object with the same keys."""
def job(c):
    p = f'content/l10n/{c}.json'; D = json.load(open(p))
    bad = {k: v for k, v in D.items() if k[0] != 'u' and re.search(r'\b[a-z]{4,}\b', K.sub('', v))}
    if not bad: return c, 0, 0
    out, cost = {}, 0
    ks = list(bad)
    for i in range(0, len(ks), 12):  # small batches: long non-Latin replies can outlive the connection
        part = {k: bad[k] for k in ks[i:i + 12]}
        o, u = T.call(T.EDITOR, SYS.format(name=I.META[c]['en_name']), json.dumps({'english_source': {k: S[k] for k in part}, 'current': part}, ensure_ascii=False))
        out.update(o); cost += (u or {}).get('cost', 0) or 0
    n = 0
    for k in bad:
        v = out.get(k)
        if isinstance(v, str) and v.strip() and not T.validate(c, {k: S[k]}, {k: v}) or (isinstance(v, str) and all('leftover' in x for x in T.validate(c, {k: S[k]}, {k: v}))):
            if v.strip() != D[k]: D[k] = v.strip(); n += 1
    json.dump(D, open(p, 'w'), ensure_ascii=False, indent=0, sort_keys=True)
    return c, n, cost
langs = [c for c, *_ in I.ALL if c in T.NONLATIN and (len(sys_args) == 0 or c in sys_args)]
tot = 0
with cf.ThreadPoolExecutor(6) as ex:
    for f in cf.as_completed([ex.submit(job, c) for c in langs]):
        try: c, n, cost = f.result(); tot += cost or 0; print(c, n, f'${cost:.3f}', flush=True)
        except Exception as e: print('FAIL', e, flush=True)
print(f'total ${tot:.2f}')
