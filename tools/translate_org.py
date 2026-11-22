#!/usr/bin/env python3
"""Translate the VideoLAN landing strings (tools/org_strings.py) with OpenRouter, in two passes per language:

1. TRANSLATE  — a fast multilingual model drafts every string.
2. PROOFREAD — a stronger model rereads the draft as a native-speaking editor and rewrites it so it reads
   like copy written in that language: natural wording, flow, logic, consistent terms. Not a literal check.

Output: content/org_i18n.json  {key: {fr, zh, ar}}. Only missing or changed keys are sent (source hashes in
content/org_i18n.src.json). Run through the credential proxy, e.g.:

    pplx credentials run custom-cred:<openrouter-handle> -- python3 tools/translate_org.py [--force] [fr zh ar]
"""
import json, re, sys, hashlib, pathlib, time
import httpx
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import org_strings as OS

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT, SRC = ROOT / 'content' / 'org_i18n.json', ROOT / 'content' / 'org_i18n.src.json'
LOG = ROOT / 'content' / 'org_i18n.log.json'
TRANSLATOR = 'google/gemini-3.8-flash'
EDITOR = 'anthropic/claude-sonnet-4.6'
API = 'https://openrouter.ai/api/v1/chat/completions'

LANGS = {
 'fr': ('French (France)', """- Address the reader as "vous". Typographic apostrophe ’ and French quotes « ».
- French spacing: a narrow no-break space (U+202F) before ; ? ! and a no-break space (U+00A0) before : and inside « ».
- Say "logiciel libre", "open source" is acceptable as an adjective ("multimédia open source"). "Association à but non lucratif" for non-profit.
- Existing site voice (keep consistent): "Gardons VLC libre, pour tous, pour toujours." · "En savoir plus" · "Contribuer" · "Projets" · "À propos"."""),
 'zh': ('Simplified Chinese (Mainland China)', """- Use full-width Chinese punctuation (，。：；“”). Put a normal space between Chinese characters and Latin words or digits (e.g. "全部 16 个项目", "领导 VideoLAN").
- Address the reader as 你. Concise, confident, modern product copy; avoid translationese and long 的-chains.
- Existing site voice (keep consistent): "让 VLC 永远免费，人人可用。" · "了解更多" · "参与贡献" · "项目" · "关于"."""),
 'ar': ('Modern Standard Arabic', """- Right-to-left text. Keep Western digits (0-9) and Latin product names unchanged. Use Arabic punctuation (، ؛ ؟).
- Address the reader in the second person singular, imperative masculine for buttons (e.g. "ساهم", "اكتشف").
- Elegant, natural MSA as used by tech publications; avoid word-for-word calques.
- Existing site voice (keep consistent): "لنُبقِ VLC حرًّا ومجانيًا للجميع وإلى الأبد." · "اعرف المزيد" · "ساهم" · "المشاريع" · "من نحن"."""),
}

COMMON = """You are localizing the homepage of videolan.org (VideoLAN, the French non-profit behind VLC media player and 16 open source multimedia projects). The audience is the general public and developers worldwide. Tone: warm, confident, precise, never salesy.

Hard rules:
- Return ONLY a JSON object mapping every input key to its {lang} string. Same keys, nothing added or removed.
- Keep every {{placeholder}} exactly as written (e.g. {{n}}, {{v}}, {{y}}).
- Keep these unchanged: VideoLAN, VLC, VLC media player, libVLC, dav1d, x264, VLMC, VLMa, DVBlast, multicat, libdvdcss, libbluray, FFmpeg, Kodi, FOSDEM, CES, SCaLE, COSCUP, Open Source Experience, Kickstarter, App Store, Apple TV, iPhone, Windows, macOS, Linux, Android, iOS, ChromeOS, GPL, GNU GPL, LGPL, BSD, AV1, H.264, DTS, DVB, MPEG TS, AACS, BD+, Blu-ray, DVD, HDR, IRC, CES, Video Dev Days, VideoLAN Dev Days, Alliance for Open Media, École Centrale Paris.
- Keep every number, year, amount and currency exactly (1996, 2009, 3,080 / 47,056 may use local digit grouping; £ stays £; "7 billion+" becomes the idiomatic local form of seven billion-plus; 130+, 3.5 billion, 40, 100, 8K must keep their value).
- Do not invent facts or drop qualifiers. Short labels must stay short (menu roles 1-4 words, layer names 1-2 words).
- Strings that are split around a link (lede_a + link + lede_b) must read as one natural sentence when concatenated: lede_a + " " + "VLC media player" + lede_b (no space before lede_b in the template).
"""

def call(model, system, user, attempt=0):
    r = httpx.post(API, timeout=300, json={'model': model, 'temperature': 0.3, 'response_format': {'type': 'json_object'},
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]},
        headers={'HTTP-Referer': 'https://vlc.paulfleury.com', 'X-Title': 'VideoLAN web redesign'})
    if r.status_code >= 500 and attempt < 2:
        time.sleep(5); return call(model, system, user, attempt + 1)
    r.raise_for_status()
    d = r.json(); txt = d['choices'][0]['message']['content'].strip()
    txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
    return json.loads(txt), d.get('usage', {})

def typo(lang, t):
    if lang == 'fr':
        t = re.sub(r"(?<=\w)'(?=\w)", '\u2019', t)
        t = re.sub(r' ?(?<!\u00a0)(?<!\u202f)([;?!])', '\u202f\\1', t) if re.search(r'\S ?[;?!]', t) else t
        t = re.sub(r'(?<=\S) ?(?<!\u00a0):(?=\s|$)', '\u00a0:', t)
        t = re.sub(r'(\d+)(es?|e) ', '\\1\\2\u00a0', t)
    return t

PH = re.compile(r'\{[a-z]+\}')
NUM = re.compile(r'\d+')
def validate(lang, src, out):
    errs = []
    for k, v in src.items():
        t = out.get(k)
        if not isinstance(t, str) or not t.strip(): errs.append(f'{k}: missing'); continue
        if sorted(PH.findall(v)) != sorted(PH.findall(t)): errs.append(f'{k}: placeholders {PH.findall(v)} vs {PH.findall(t)}')
        sv = ''.join(NUM.findall(v)); tv = ''.join(NUM.findall(t.replace('\u202f', '').replace('\u00a0', '').replace(',', '').replace(' ', '')))
        sv2 = ''.join(NUM.findall(v.replace(',', '')))
        if k not in ('n_dl_v', 't2021_d', 'n_dl') and sorted(sv2) != sorted(tv): errs.append(f'{k}: numbers {sv2} vs {tv}')
        if lang in ('zh', 'ar'):
            latin = re.sub(r'VideoLAN|VLC|libVLC|[A-Za-z0-9+.#·\-]+', '', t)
            if re.search(r'[A-Za-z]{4,}', latin): errs.append(f'{k}: leftover Latin')
    extra = set(out) - set(src)
    if extra: errs.append(f'extra keys {sorted(extra)}')
    return errs

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    langs = args or list(LANGS)
    force = '--force' in sys.argv
    tr = json.loads(OUT.read_text()) if OUT.exists() else {}
    src_h = json.loads(SRC.read_text()) if SRC.exists() else {}
    log = json.loads(LOG.read_text()) if LOG.exists() else []
    SRCD = OS.source()
    h = {k: hashlib.sha1(v.encode()).hexdigest()[:12] for k, v in SRCD.items()}
    for lang in langs:
        name, style = LANGS[lang]
        only = [a[7:].split(',') for a in sys.argv if a.startswith('--keys=')]
        todo = {k: v for k, v in SRCD.items() if (only and k in only[0]) or (not only and (force or lang not in tr.get(k, {}) or src_h.get(k, {}).get(lang) != h[k]))}
        if not todo: print(lang, 'up to date'); continue
        payload = json.dumps({'strings': todo, 'context': {k: OS.CONTEXT.get(k, 'news card title on the homepage (VideoLAN release announcement)' if k.endswith('_t') else 'news card excerpt, cut mid-text, keep the trailing ellipsis; product and library names and version numbers unchanged') for k in todo if k in OS.CONTEXT or k.startswith('nw_')}}, ensure_ascii=False, indent=1)
        sys_t = COMMON.format(lang=name) + f'\nLanguage notes for {name}:\n{style}'
        draft, u1 = call(TRANSLATOR, sys_t, f'Translate into {name}. Input:\n{payload}')
        errs = validate(lang, todo, draft)
        print(lang, 'draft', len(draft), 'issues', errs[:6])
        sys_e = COMMON.format(lang=name) + f"""\nYou are now the senior {name} copy editor and a native speaker. A first translation is attached.
Reread every string as if this were a page written natively in {name} for a respected open source organisation:
- Rewrite anything that sounds translated: choose the expression a native writer would use, improve rhythm, word order and logic between sentences, and make headings punchy.
- Keep the meaning, facts, numbers, names and placeholders of the English source. Do not add claims.
- Keep terminology consistent across all strings (same word for "project", "non-profit", "contributor", "Dev Days", etc.).
- Respect the language notes and the length of short labels.
- Fix any validation issue listed.
Language notes for {name}:
{style}
Return the full corrected JSON object with every key."""
        final, u2 = call(EDITOR, sys_e, json.dumps({'english_source': todo, 'context': {k: OS.CONTEXT.get(k, 'news card title on the homepage (VideoLAN release announcement)' if k.endswith('_t') else 'news card excerpt, cut mid-text, keep the trailing ellipsis; product and library names and version numbers unchanged') for k in todo if k in OS.CONTEXT or k.startswith('nw_')}, 'first_translation': draft, 'validation_issues': errs}, ensure_ascii=False, indent=1))
        errs2 = validate(lang, todo, final)
        print(lang, 'final', len(final), 'issues', errs2)
        if any('missing' in x or 'placeholders' in x or 'extra' in x for x in errs2):
            raise SystemExit(f'{lang}: structural validation failed, nothing saved')
        for k in todo:
            tr.setdefault(k, {})[lang] = typo(lang, final[k].strip())
            src_h.setdefault(k, {})[lang] = h[k]
        log.append({'lang': lang, 'keys': len(todo), 'translator': TRANSLATOR, 'editor': EDITOR, 'usage': [u1, u2], 'warnings': errs2, 'at': time.strftime('%Y-%m-%dT%H:%M:%S')})
        OUT.write_text(json.dumps(tr, ensure_ascii=False, indent=1, sort_keys=True))
        SRC.write_text(json.dumps(src_h, indent=1, sort_keys=True))
        LOG.write_text(json.dumps(log, ensure_ascii=False, indent=1))
    print('saved', OUT)

if __name__ == '__main__':
    main()
