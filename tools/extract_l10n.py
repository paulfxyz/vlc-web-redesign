#!/usr/bin/env python3
"""Collect every translatable English string the site uses into content/l10n/_source.json.

Keys: t:<ui key> · s:<section>:<0 title|1 lede> · p:<hash of English> (curated tuples) · o:<landing key>
      l:<lite key> · u:<subtitle line>. Curated tuples are found by rendering every page in memory
      (French) with recording on, so only strings that really appear are sent to translators.
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import i18n as I, curated as CU, org_strings as OS, lite as LT, vlsite as S
import build_site as B

def main():
    CU.REC = set()
    c0, c1 = B.Ctx('fr', 0), B.Ctx('fr', 1)
    B.org_home(c0); B.home(c1, 'vlc'); B.l10n_js('fr')
    for slug, p in S.ALL.items(): B.content_page(B.Ctx('fr', 1), p)
    LT.page('fr', B.F, B.V, B.STORE, B.LINUX)
    src, ctx = {}, {}
    for k, v in I.T.items():
        src['t:' + k] = v[0] or I.EN_FILL[k]
    for k, (a, b) in I.SECTIONS_T.items():
        src[f's:{k}:0'], src[f's:{k}:1'] = a[0], b[0]
        ctx[f's:{k}:0'] = 'site section name (menu, breadcrumb)'; ctx[f's:{k}:1'] = 'one-line description of a site section'
    for i, x in enumerate(B.SUBS['en']):
        src[f'u:{i}'] = x; ctx[f'u:{i}'] = 'subtitle line burned into a movie still (Big Buck Bunny / Sintel), casual spoken style'
    for k, v in LT.LS.items(): src['l:' + k] = v[0]; ctx['l:' + k] = 'simple text-only page for old browsers'
    for k, v in OS.source().items():
        src['o:' + k] = v
        if k in OS.CONTEXT: ctx['o:' + k] = OS.CONTEXT[k]
        elif k.startswith('nw_'): ctx['o:' + k] = 'homepage news card ' + ('title' if k.endswith('_t') else 'excerpt (cut, keep trailing …)')
    for x in sorted(CU.REC): src['p:' + I.hk(x)] = x
    out = pathlib.Path(__file__).resolve().parent.parent / 'content' / 'l10n' / '_source.json'
    out.write_text(json.dumps({'strings': src, 'context': ctx}, ensure_ascii=False, indent=1, sort_keys=True))
    print(len(src), 'strings', sum(len(v) for v in src.values()), 'chars ->', out)

if __name__ == '__main__':
    main()
