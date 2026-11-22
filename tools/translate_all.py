#!/usr/bin/env python3
"""Translate the whole site catalog (content/l10n/_source.json) into every additional language.

Per language, per chunk: 1) a fast multilingual model drafts, 2) a stronger model rereads as a native-speaking
editor and rewrites for natural wording, rhythm and logic. The first chunk carries the core terms; its approved
translations become a glossary for the other chunks. Output: content/l10n/<code>.json (resumable: only missing
or changed keys are sent; source hashes in content/l10n/_hashes/<code>.json; usage in content/l10n/_log.jsonl).

    pplx credentials run custom-cred:<openrouter-handle> -- python3 tools/translate_all.py [--jobs 10] [codes…]
"""
import json, re, sys, time, pathlib, hashlib, threading, concurrent.futures as cf
import httpx
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import i18n as I

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'content' / 'l10n'
TRANSLATOR, EDITOR = 'google/gemini-3.8-flash', 'anthropic/claude-sonnet-4.6'
API = 'https://openrouter.ai/api/v1/chat/completions'
LOCK = threading.Lock()

NOTES = {
 'zh-Hant': 'Traditional Chinese as used in Taiwan (zh-TW vocabulary: 軟體, 影片, 網路, 檔案, 資訊). Full-width punctuation; a space between Han characters and Latin words or digits.',
 'ja': 'Natural Japanese UI copy, です/ます where a sentence is needed, plain noun phrases for labels. Full-width punctuation 「」、。 No spaces between Japanese words; a thin space is not needed before Latin words.',
 'ko': 'Natural Korean UI copy (합니다/해요 style consistent: use 합니다 체 for sentences, noun phrases for labels).',
 'pt-PT': 'European Portuguese (Portugal) — not Brazilian: "ecrã", "transferir", "ficheiro", "utilizador".',
 'pt-BR': 'Brazilian Portuguese: "tela", "baixar", "arquivo", "usuário".',
 'sr': 'Serbian in Cyrillic script only.', 'uz': 'Uzbek in Latin script (Oʻzbekcha, with oʻ and gʻ).', 'mn': 'Mongolian in Cyrillic script.',
 'ku': 'Kurdish Kurmanji in Latin script (Hawar alphabet).', 'pa': 'Punjabi in Gurmukhi script.', 'nb': 'Norwegian Bokmål.',
 'de': 'Use "Sie" consistently; natural German product copy, not literal.', 'nl': 'Use "je" (informal) consistently, as in modern Dutch software.',
 'he': 'Hebrew, right-to-left; keep Latin product names and digits unchanged.', 'fa': 'Persian, right-to-left; Persian punctuation (، ؛ ؟); keep Western digits 0-9.',
 'ur': 'Urdu in Nastaliq-compatible Perso-Arabic script, right-to-left; keep Western digits 0-9.', 'ps': 'Pashto, right-to-left; keep Western digits 0-9.',
 'ga': 'Irish (Gaeilge), standard An Caighdeán Oifigiúil.', 'br': 'Breton (peurunvan orthography).', 'oc': 'Occitan (Languedocien, classical norm).',
 'eo': 'Esperanto.', 'fil': 'Filipino (Tagalog-based); English loanwords only where Filipino software normally uses them.',
}

PROMPT = """You are localizing videolan.org, the website of VideoLAN (French non-profit behind VLC media player and 16 open source multimedia projects), into {name}.
Audience: the general public and developers. Tone: warm, clear, confident, never salesy. Write like professional software localization for {name}, using the register customary in modern consumer software for that locale, consistently.

Hard rules:
- Return ONLY a JSON object mapping every input key to its {name} string. Same keys, nothing added or removed.
- Keep {{placeholders}} exactly (e.g. {{n}}, {{v}}, {{y}}, {{q}}, {{os}}, {{l}}, {{a}}, {{b}}) and any HTML tags exactly.
- Keep unchanged: VideoLAN, VLC, VLC media player, libVLC, dav1d, dav2d, x264, x262, VLMC, VLMa, DVBlast, multicat, libdvdcss, libdvdnav, libdvdread, libbluray, libaacs, libbdplus, libdvbpsi, biTStream, libdvbcsa, libdca, FFmpeg, Kodi, FOSDEM, CES, SCaLE, COSCUP, Open Source Experience, Kickstarter, App Store, Google Play, Microsoft Store, F-Droid, Flathub, Snap, Apple TV, iPhone, iPad, Windows, macOS, Linux, GNU/Linux, Android, iOS, ChromeOS, GPL, GNU GPL, LGPL, BSD, MIT, AV1, AV2, H.264, DTS, DVB, MPEG, AACS, BD+, Blu-ray, DVD, HDR, IRC, SHA-256, Video Dev Days, VideoLAN Dev Days, Alliance for Open Media, École Centrale Paris, Big Buck Bunny, Sintel.
- Keep every number and year with its value; Western digits 0-9. Local digit grouping is fine.
- Do not invent facts or drop qualifiers. Labels stay short (buttons and menu items 1-4 words).
- Keys starting with "t:" are interface strings; "o:" homepage copy; "p:" curated page copy; "s:" section names/ledes; "l:" a simple page for old browsers; "u:" subtitle lines in a movie still.
- o:lede_a + " " + "VLC media player" + o:lede_b must read as one sentence (o:lede_b is appended with no space; adapt its opening punctuation).
{notes}"""

EDIT = """
You are now the senior {name} copy editor, a native speaker. A first translation is attached.
Reread every string as if this page were written natively in {name} for a respected open source organisation:
- Rewrite anything that sounds translated: the expression a native writer would choose, better rhythm, word order and logic between sentences; punchy headings; idiomatic UI labels.
- Keep the meaning, facts, numbers, names, placeholders and tags of the English source. Do not add claims.
- Keep terminology consistent and follow the glossary of already-approved terms if given.
- Fix every validation issue listed.
Return the full corrected JSON object with every key."""

CORE = re.compile(r'^(t:nav_|t:donate|t:home$|t:menu$|t:cta_download|t:search$|s:[a-z]+:0$|o:brand_sub|o:h1|o:kick|o:p_btn|o:mg_all|o:board|o:n_pj|o:n_ppl)')

def call(model, system, user, tries=3):
    for a in range(tries):
        try:
            r = httpx.post(API, timeout=420, json={'model': model, 'temperature': 0.3, 'max_tokens': 32000, 'response_format': {'type': 'json_object'},
                'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]},
                headers={'HTTP-Referer': 'https://vlc.paulfleury.com', 'X-Title': 'VideoLAN web redesign'})
            if r.status_code in (429, 500, 502, 503, 504): raise RuntimeError(f'HTTP {r.status_code}')
            r.raise_for_status()
            d = r.json(); txt = d['choices'][0]['message']['content'].strip()
            txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
            o = json.loads(txt)
            if isinstance(o, dict) and len(o) == 1 and isinstance(next(iter(o.values())), dict): o = next(iter(o.values()))
            return o, d.get('usage', {})
        except Exception as ex:
            if a == tries - 1: raise
            time.sleep(8 * (a + 1))

PH = re.compile(r'\{[a-z_]+\}'); TAG = re.compile(r'</?[a-z][^>]*>'); NUM = re.compile(r'\d+')
NONLATIN = {'ru', 'uk', 'bg', 'el', 'he', 'fa', 'ur', 'ps', 'hi', 'bn', 'pa', 'gu', 'mr', 'ta', 'te', 'kn', 'ml', 'si', 'ne', 'th', 'zh-Hant', 'ja', 'ko', 'sr', 'mk', 'am', 'kk', 'ka', 'hy', 'mn', 'km', 'lo', 'my'}
KEEP = re.compile(r'VideoLAN|VLC|libVLC|Video Dev Days|Dev Days|Open Source Experience|Alliance for Open Media|École Centrale Paris|Big Buck Bunny|Kickstarter|App Store|Google Play|Microsoft Store|Apple TV|Apple Silicon|GNU/Linux|[A-Za-z0-9+.#·/\-]*\d[A-Za-z0-9+.#·/\-]*|\b[A-Z][A-Za-z0-9+.\-]*\b|\b[a-z]+[A-Z0-9][A-Za-z0-9]*\b|\{[a-z_]+\}|<[^>]+>')

def validate(lang, src, out):
    errs = []
    for k, v in src.items():
        t = out.get(k)
        if not isinstance(t, str) or not t.strip(): errs.append(f'{k}: missing'); continue
        if sorted(PH.findall(v)) != sorted(PH.findall(t)): errs.append(f'{k}: placeholders')
        if sorted(TAG.findall(v)) != sorted(TAG.findall(t)): errs.append(f'{k}: tags')
        if lang in NONLATIN and re.search(r'\b[a-z]{5,}\b', KEEP.sub('', t)) and k[0] not in 'u': errs.append(f'{k}: leftover English')
        if lang not in NONLATIN and len(v) > 30 and t.strip() == v.strip(): errs.append(f'{k}: identical to English')
    if set(out) - set(src): errs.append('extra keys')
    return errs

def chunks(src):
    core = {k: v for k, v in src.items() if CORE.match(k)}
    rest = [k for k in src if k not in core]
    groups, cur, size = [core] if core else [], {}, 0
    for k in rest:
        cur[k] = src[k]; size += len(src[k])
        if size > 3200 or len(cur) >= 80: groups.append(cur); cur, size = {}, 0
    if cur: groups.append(cur)
    return groups

def log(rec):
    with LOCK:
        with open(D / '_log.jsonl', 'a') as f: f.write(json.dumps(rec, ensure_ascii=False) + '\n')

def do_lang(code, SRC, CTX, H):
    name = I.META[code]['en_name']
    path = D / f'{code}.json'
    have = json.loads(path.read_text()) if path.exists() else {}
    hp = D / '_hashes' / f'{code}.json'; hashes = json.loads(hp.read_text()) if hp.exists() else {}
    todo = {k: v for k, v in SRC.items() if k not in have or hashes.get(k) != H[k]}
    if not todo: return code, 'up to date', 0
    sysp = PROMPT.format(name=name, notes=('Language notes: ' + NOTES[code]) if code in NOTES else '')
    gloss = {k: have[k] for k in have if CORE.match(k)}
    cost = [0.0]
    def run(ch, gloss):
        ctx = {k: CTX[k] for k in ch if k in CTX}
        draft, u1 = call(TRANSLATOR, sysp, json.dumps({'strings': ch, 'context': ctx, 'glossary': gloss}, ensure_ascii=False))
        e1 = validate(code, ch, draft)
        final, u2 = call(EDITOR, sysp + EDIT.format(name=name), json.dumps({'english_source': ch, 'context': ctx, 'glossary': gloss, 'first_translation': draft, 'validation_issues': e1[:60]}, ensure_ascii=False))
        e2 = validate(code, ch, final)
        hard = [x for x in e2 if any(w in x for w in ('missing', 'placeholders', 'tags', 'extra'))]
        u3 = {}
        if hard:  # one targeted repair of the failing keys
            bad = {k: ch[k] for k in ch if any(x.startswith(k + ':') for x in hard)} or ch
            fix, u3 = call(EDITOR, sysp + EDIT.format(name=name), json.dumps({'english_source': bad, 'glossary': gloss, 'first_translation': {k: final.get(k) or draft.get(k, '') for k in bad}, 'validation_issues': hard}, ensure_ascii=False))
            for k in bad:
                if k in fix: final[k] = fix[k]
            e2 = validate(code, ch, final)
            hard = [x for x in e2 if any(w in x for w in ('missing', 'placeholders', 'tags', 'extra'))]
        if hard:  # last resort: small editor batches, then a validated draft
            bad = [k for k in ch if any(x.startswith(k + ':') for x in hard)]
            for i in range(0, len(bad), 15):
                sub = {k: ch[k] for k in bad[i:i + 15]}
                try:
                    fix, u4 = call(EDITOR, sysp + EDIT.format(name=name), json.dumps({'english_source': sub, 'glossary': gloss, 'first_translation': {k: draft.get(k, '') for k in sub}}, ensure_ascii=False))
                    u3 = {'cost': (u3 or {}).get('cost', 0) + (u4 or {}).get('cost', 0)}
                except Exception: fix = {}
                for k in sub:
                    for cand in (fix.get(k), draft.get(k)):
                        if isinstance(cand, str) and not validate(code, {k: ch[k]}, {k: cand}) or (isinstance(cand, str) and all('leftover' in x or 'identical' in x for x in validate(code, {k: ch[k]}, {k: cand}))):
                            final[k] = cand; break
            e2 = validate(code, ch, final)
            hard = [x for x in e2 if any(w in x for w in ('missing', 'placeholders', 'tags')) ]
        with LOCK:
            for k in ch:
                if k in final and not any(x.startswith(k + ':') for x in hard):
                    have[k] = final[k].strip(); hashes[k] = H[k]
            cost[0] += sum((u or {}).get('cost', 0) or 0 for u in (u1, u2, u3))
            path.write_text(json.dumps(have, ensure_ascii=False, indent=0, sort_keys=True))
            hp.parent.mkdir(exist_ok=True); hp.write_text(json.dumps(hashes, sort_keys=True))
        log({'lang': code, 'keys': len(ch), 'soft': [x for x in e2 if x not in hard][:20], 'hard': hard, 'usage': [u1, u2, u3], 'at': time.strftime('%H:%M:%S')})
    cs = chunks(todo)
    if cs and CORE.match(next(iter(cs[0]))):
        run(cs[0], gloss); cs = cs[1:]
        gloss = {k: have[k] for k in have if CORE.match(k)}
    with cf.ThreadPoolExecutor(4) as ex:
        def safe(ch, gloss, depth=0):
            try: run(ch, gloss)
            except Exception as e4:
                log({'lang': code, 'error': f'split {len(ch)}: ' + str(e4)[:160], 'at': time.strftime('%H:%M:%S')})
                if len(ch) <= 6 or depth > 3: raise
                ks = list(ch); h = len(ks) // 2
                safe({k: ch[k] for k in ks[:h]}, gloss, depth + 1); safe({k: ch[k] for k in ks[h:]}, gloss, depth + 1)
        for f in [ex.submit(safe, ch, gloss) for ch in cs]:
            try: f.result()
            except Exception as e3: log({'lang': code, 'error': str(e3)[:200], 'at': time.strftime('%H:%M:%S')})
    cost = cost[0]
    missing = [k for k in SRC if k not in have]
    return code, f'{len(have)}/{len(SRC)} done, {len(missing)} missing', cost

def main():
    a = sys.argv[1:]; jobs = 10
    if '--jobs' in a: i = a.index('--jobs'); jobs = int(a[i + 1]); del a[i:i + 2]
    data = json.loads((D / '_source.json').read_text()); SRC, CTX = data['strings'], data['context']
    H = {k: hashlib.sha1(v.encode()).hexdigest()[:12] for k, v in SRC.items()}
    codes = a or [c for c, _, _ in I.ALL if c not in I.BASE]
    total = 0.0
    with cf.ThreadPoolExecutor(jobs) as ex:
        futs = {ex.submit(do_lang, c, SRC, CTX, H): c for c in codes}
        for f in cf.as_completed(futs):
            try: code, msg, cost = f.result(); total += cost; print(code, msg, f'${cost:.3f}', flush=True)
            except Exception as ex2: print(futs[f], 'FAILED', str(ex2)[:200], flush=True)
    print(f'total ${total:.2f}')

if __name__ == '__main__':
    main()
