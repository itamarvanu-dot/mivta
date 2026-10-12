"""Mivta Niqqud: exact niqqud and stress for Hebrew text, with a word-by-word table of the reading.

  python nq.py doctor                              check the install and the plan
  python nq.py text "<Hebrew text>" [--out DIR]    vocalize a short text (prints it; files too with --out)
  python nq.py file <input.txt> [--out DIR]        vocalize a file -> <name>.niqqud.txt, <name>.table.md (+ .stress.txt, Pro)

Free plan: up to 150 words per run. Mivta Pro: any length, the shared verified dictionary, the stress-marked copy.
  python nq.py add-word <word> <niqqud>            your own reading of a word, used from now on (mil'el: U+05AB)
  python nq.py settings [--domains=general,diy] [--style=standard|colloquial]
  python nq.py trial <email>                       Mivta Pro for 7 days, no card (the shared, verified dictionary)
  python nq.py activate <licence key>              Mivta Pro / Studio (the key from the purchase email)

Outputs: .niqqud.txt = standard niqqud (the input's own letters, vowel points added); .stress.txt = the same with the
stress mark (U+05AB) on words stressed before the last syllable; .table.md = every word, its niqqud, how it sounds
(Latin, the stressed syllable in capitals) and where the reading came from.

Readings, first match wins: your own words (HV_HOME/user_lex.json) > Mivta Pro's shared dictionary (Pro only: one-way
codes of the words are sent to the Mivta server, never the text) > the starter dictionary > Phonikud's automatic
niqqud (the Phonikud model, MIT; Phonikud code, CC BY 4.0).
Run with:  ~/.mivta/venv_nq/bin/python nq.py ...
"""
import os, sys, re, json, time, hashlib, unicodedata

HOME = os.path.abspath(os.environ.get("HV_HOME", os.path.expanduser("~/.mivta")))      # shared with Mivta (voice)
HERE = os.path.dirname(os.path.abspath(__file__))
FREE_LEX = os.path.join(os.path.dirname(HERE), "data", "he_lexicon_free.jsonl")
MODEL = os.environ.get("HV_PHONIKUD", os.path.join(HOME, "models", "phonikud-1.0.int8.onnx"))
LICENSE = os.path.join(HOME, "pro", "license.json")
USER_LEX = os.path.join(HOME, "user_lex.json")
SETTINGS = os.path.join(HOME, "settings.json")
SERVER = os.environ.get("HV_DICT_SERVER", "https://mivta.netlify.app")
SUPPORT = "mivta.ai@gmail.com"
FREE_OWN_WORDS = 10
FREE_WORDS = 150                                   # free plan: words per run (Pro: any length)
UPGRADE = "Mivta Pro checks them against the shared, verified dictionary (python nq.py trial <email>: 7 days free, no card)."
STRESS, METEG, SHVA, DAGESH = "\u05ab", "\u05bd", "\u05b0", "\u05bc"
NIQQUD = re.compile(r"[\u0591-\u05c7]")
# the vowel each point says (qamats: a, or o as in kol); a plain shva says e only where the IPA has one
QUALITY = {"\u05b1": "e", "\u05b2": "a", "\u05b3": "o", "\u05b4": "i", "\u05b5": "e", "\u05b6": "e", "\u05b7": "a",
           "\u05b8": "ao", "\u05b9": "o", "\u05ba": "o", "\u05bb": "u", "\u05c7": "o"}


# ------------------------------------------------------------------------------------------------- plan + server
def settings():
    d = {"domains": ["general"], "style": "standard", "voice": "me"}
    if os.path.exists(SETTINGS): d.update(json.load(open(SETTINGS)))
    return d


def licence():
    return json.load(open(LICENSE)) if os.path.exists(LICENSE) else None


def tier():
    L = licence()
    if not L: return "free"
    if L.get("expires") and L["expires"] < time.time(): return "free"
    return L.get("tier", "pro")


def server(route, body, tries=4):
    """POST to the Mivta server; the licence key rides along when there is one."""
    import urllib.request
    L = licence()
    if L: body = dict(body, key=L["key"], instance_id=L.get("instance_id"))
    data = json.dumps(body).encode()
    for attempt in range(tries):
        req = urllib.request.Request(SERVER.rstrip("/") + route, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and attempt < tries - 1: time.sleep(10); continue
            try: return json.loads(e.read().decode())
            except Exception: return {"ok": False, "error": f"server error {e.code}"}
        except Exception as e:
            if attempt < tries - 1: time.sleep(10); continue
            return {"ok": False, "error": f"cannot reach the Mivta server ({e})", "offline": True}


# ------------------------------------------------------------------------------------------------- dictionaries
def strip(s):
    return NIQQUD.sub("", unicodedata.normalize("NFD", s)).replace("|", "")


def plain(w):
    """A text word without punctuation, quotes or niqqud: the dictionaries' key (acronyms keep ״)."""
    return strip(re.sub(r"^[\"״'(\[]+|[.,?!:;—–\-|\"״')\]]+$", "", w)).replace('"', "״")


def code(s):
    """One-way code of a word or a word sequence: the only thing sent to the Mivta server."""
    return hashlib.sha256(("hv1|" + unicodedata.normalize("NFC", s)).encode()).hexdigest()[:24]


def clusters(w):
    """'שֶׁ֫קַע' -> [['ש', 'ֶׁ֫'], ['ק', 'ַ'], ['ע', '']]: each letter with the marks that follow it."""
    out = []
    for ch in unicodedata.normalize("NFD", w):
        if "א" <= ch <= "ת" or not out: out.append([ch, ""])
        else: out[-1][1] += ch
    return out


def fit(voc, word):
    """The dictionary's niqqud on the TEXT's own letters. A reading spelled with fewer vowel letters (תִּקְוָה for
    תקווה) gets the text's extra ו / י unpointed (תִּקְוָוה), the usual way to point full spelling. None when the
    letters differ otherwise: such an entry is not a spelling of this word."""
    cs, out, i = clusters(voc), [], 0
    for ch in word:
        if i < len(cs) and cs[i][0] == ch:
            out.append(cs[i][0] + cs[i][1]); i += 1
        elif ch in "וי":
            out.append(ch)
        else:
            return None
    return "".join(out) if i == len(cs) else None


def usable(e, st):
    if not set(e.get("domains", ["general"])) & set(st["domains"]): return False
    if e.get("style", "standard") == "colloquial" and st["style"] != "colloquial": return False
    return e.get("status", "verified") == "verified"


def load_dictionaries():
    """-> (words, phrases, origin): the starter dictionary, then your own words on top (yours always win)."""
    st = settings(); words, phrases, origin = {}, {}, {}
    rows = open(FREE_LEX, encoding="utf-8").read().splitlines() if os.path.exists(FREE_LEX) else []
    for r in rows[1:]:
        if not r.strip(): continue
        e = json.loads(r)
        if not usable(e, st): continue
        k = e.get("word") or e.get("phrase")
        (words if "word" in e else phrases)[k] = e["voc"]; origin[k] = "dictionary"
    if os.path.exists(USER_LEX):
        for k, v in json.load(open(USER_LEX, encoding="utf-8")).items():
            (phrases if " " in k else words)[k] = v; origin[k] = "your word"
    return words, phrases, origin


def pro_lookup(text):
    """Pro: the shared dictionary's entries for the words of this text (words, prefixed forms, 2-3 word phrases)."""
    ws = [plain(w) for w in text.split()]; ws = [w for w in ws if w]
    want = {}
    for i, w in enumerate(ws):
        want[code(w)] = w
        for L in (2, 3):
            if i + L <= len(ws): ph = " ".join(ws[i:i + L]); want[code(ph)] = ph
    found = {}
    keys = sorted(want)
    for j in range(0, len(keys), 2500):
        r = server("/lookup", {"codes": keys[j:j + 2500], "forms": True})
        if not r.get("ok"):
            if r.get("licence") == "invalid":
                os.remove(LICENSE)
                sys.exit(f"Your Mivta licence is not active any more ({r.get('error')}); back to the free plan. "
                         f"Questions: {SUPPORT}")
            print(f"(the shared dictionary is not reachable right now: {r.get('error')}; using the starter dictionary)")
            return {}
        found.update({want[c]: e for c, e in r["entries"].items() if c in want})
    return found


# ------------------------------------------------------------------------------------------------- vocalize
_ph = None
def phonikud():
    global _ph
    if _ph is None:
        from phonikud_onnx import Phonikud
        _ph = Phonikud(MODEL)
    return _ph


def _boundary(raw, n):
    """Phonikud's own reading marks a prefix boundary ("|") after exactly n letters (מִשְׁקָע is not מ + שקע)."""
    if "|" not in raw: return False
    return len([c for c in raw.split("|")[0] if "א" <= c <= "ת"]) == n


def _definite(raw, n):
    """בַּשֶּׁקַע (the socket) vs בְּשֶׁקַע (a socket): Phonikud's vowel under the last prefix letter decides."""
    cs = clusters(raw.split("|")[0])
    return n <= len(cs) and any(v in cs[n - 1][1] for v in ("ַ", "ָ"))


def _tidy_dagesh(word):
    """Drop a dagesh the grammar does not allow, which the model now and then adds to a word: on a guttural (א ה ח ע ר,
    a final mappiq ה aside), or on a letter outside בגדכפ"ת that starts the word or follows a letter without a vowel
    (שָּׁלוֹם, מַפְסֵּק): a doubled letter always follows a vowel. A shuruk (וּ) keeps its dot."""
    cs, prev_vowel = clusters(word), False
    letters = [k for k, (c, _) in enumerate(cs) if "א" <= c <= "ת"]
    for k in letters:
        c, m = cs[k]
        if DAGESH in m and c != "ו":
            mappiq = c == "ה" and k == letters[-1]
            if (c in "אהחער" and not mappiq) or (c not in "בגדכפתאהחער" and not prev_vowel):
                cs[k][1] = m.replace(DAGESH, "")
        if not (c in "וי" and not NIQQUD.search(m)):                         # a bare vowel letter keeps the vowel before it
            prev_vowel = any(x in QUALITY for x in m) or (c == "ו" and DAGESH in m)
    return "".join(a + b for a, b in cs)


def vocalize(text, pro=None):
    """-> (rows [{word, voc, source}] in text order, the vocalized text with all marks)."""
    words, phrases, origin = load_dictionaries(); st = settings()
    pro = pro or {}
    toks = re.split(r"(\s+)", phonikud().add_diacritics(text))
    items = []                                     # {i: token index, core, punct, w: plain key, raw: with "|"}
    for i, tok in enumerate(toks):
        if not tok.strip(): continue
        m = re.match(r"^(.*?)([.,?!:;—–\-״\"')\]|]*)$", tok)
        raw, punct = _tidy_dagesh(m.group(1)), m.group(2).replace("|", "")
        items.append({"i": i, "core": raw.replace("|", ""), "punct": punct, "w": plain(raw), "raw": raw, "src": "auto"})
    done = set()
    allph = {k: e["voc"] for k, e in pro.items() if e.get("k") == "p" and usable(e, st)}
    allph.update(phrases)                          # your phrases win over the shared ones
    for ph, pv in sorted(allph.items(), key=lambda kv: -len(kv[0].split())):
        pw, vw = ph.split(), pv.split()
        if len(pw) != len(vw): continue
        for j in range(len(items) - len(pw) + 1):
            span = items[j:j + len(pw)]
            if any(x["i"] in done for x in span) or [x["w"] for x in span] != pw: continue
            fitted = [fit(v, x["w"]) for v, x in zip(vw, span)]
            if None in fitted: continue
            for x, f in zip(span, fitted):
                x["core"] = f; done.add(x["i"])
                x["src"] = "your word" if origin.get(ph) == "your word" else "dictionary (Pro)" if ph not in phrases else "dictionary"
    for x in items:
        if x["i"] in done: continue
        w, reading, source = x["w"], None, "auto"
        if w in words and origin.get(w) == "your word":
            reading, source = fit(words[w], w), "your word"
        if reading is None and w in pro and usable(pro[w], st):
            e = pro[w]
            if e.get("k") == "w":
                reading = fit(e.get("ortho") or e["voc"], w)
            elif e.get("k") == "f" and _boundary(x["raw"], e["pre"]):
                if "alt" in e and _definite(x["raw"], e["pre"]): reading = fit(e.get("alt_ortho") or e["alt"], w)
                else: reading = fit(e.get("ortho") or e["voc"], w)
            source = "dictionary (Pro)"
        if reading is None and w in words:
            reading, source = fit(words[w], w), "dictionary"
        if reading:
            x["core"], x["src"] = reading, source
    for x in items:
        toks[x["i"]] = x["core"] + x["punct"]
    rows = [{"word": strip(x["core"]) + x["punct"], "voc": x["core"], "source": x["src"]} for x in items]
    return rows, "".join(toks)


def readable(voc):
    """Phonikud writes full-spelling u and o as qubuts / holam + a bare vav (מְחֻובָּרִים, בֹּוץ); readers expect the
    vav to carry them: shuruk and holam male (מְחוּבָּרִים, בּוֹץ)."""
    cs = clusters(voc.replace("|", ""))
    for a, b in zip(cs, cs[1:]):
        if b[0] == "ו" and not NIQQUD.search(b[1]):            # a bare vav (spaces or punctuation may follow it)
            if "\u05bb" in a[1]: a[1] = a[1].replace("\u05bb", ""); b[1] = "\u05bc" + b[1]
            elif "\u05b9" in a[1]: a[1] = a[1].replace("\u05b9", ""); b[1] = "\u05b9" + b[1]
    return "".join(c + m for c, m in cs)


def _no_final_shva(text):
    """Readers write no shva under a word's last letter, except ך and תּ (לָךְ, אַתְּ). The voice dictionary closes
    חַשְׁמַלַּאי with one (it keeps the glide in a voice engine); the reading copy drops it."""
    def word(m):
        cs = clusters(m.group(0)); c, mk = cs[-1]
        if SHVA in mk and c != "ך" and not (c == "ת" and DAGESH in mk): cs[-1][1] = mk.replace(SHVA, "")
        return "".join(x + y for x, y in cs)
    return re.sub(r"(?:[א-ת][֑-ׇ]*)+", word, text)


def standard(voc):
    """Standard niqqud for reading: no stress mark, no vocal-shva helper mark."""
    return _no_final_shva(readable(voc).replace(STRESS, "").replace(METEG, ""))


def with_stress(voc):
    """Niqqud + the stress mark on words stressed before the last syllable (helps readers and voice engines)."""
    return _no_final_shva(readable(voc).replace(METEG, ""))


LAT = [("tʃ", "tch"), ("dʒ", "j"), ("ts", "ts"), ("ʃ", "sh"), ("χ", "kh"), ("x", "kh"), ("ʁ", "r"), ("ɡ", "g"),
       ("ʒ", "zh"), ("j", "y"), ("ʔ", ""), ("ˌ", "")]


def _vowel_letters(voc, vowels):
    """The letters that carry the spoken vowels of a word, in order -> [letter index] or None when they cannot be matched.
    A full vowel point, a shuruk or a marked vocal shva always says a vowel; a plain shva only where the IPA has an e
    there (Phonikud says וְ as 've' but כְּשֶׁ as 'kshe')."""
    cs = [c for c in clusters(voc) if "א" <= c[0] <= "ת"]
    marks = []
    for k, (c, m) in enumerate(cs):
        q = "".join(QUALITY[x] for x in m if x in QUALITY)
        if q: marks.append((q, False))
        elif SHVA in m: marks.append(("e", METEG not in m))
        elif c == "ו" and DAGESH in m and (k == 0 or not any(x in QUALITY or x == METEG for x in cs[k - 1][1])):
            marks.append(("u", False))                                      # shuruk
        else: marks.append(("", False))
    out, n = [], 0
    for k, (q, optional) in enumerate(marks):
        if not q: continue
        if optional:
            sure = sum(1 for x, o in marks[k + 1:] if x and not o)
            if not (n < len(vowels) and vowels[n] == "e" and sure < len(vowels) - n): continue
        if n >= len(vowels) or vowels[n] not in q: return None
        out.append(k); n += 1
    return (out, cs) if n == len(vowels) else None


def sounds(ipa_word, voc=None):
    """'hasapˈaʁ' -> 'ha-sa-PAR': syllables, the stressed one in capitals. Between two vowels one consonant opens the
    next syllable and a longer run leaves its first consonant behind (yish-BRU); with the word's niqqud, a doubled
    letter with shva opens the syllable with the run (הַפְּחָת: ha-PKHAT, הַסְּפָרִים: ha-sfa-RIM)."""
    w = re.sub(r"[.,?!:;\"״'\-]", "", ipa_word)
    stress_at = w.find("ˈ"); w = w.replace("ˈ", "")
    phones, i = [], 0
    while i < len(w):
        two = w[i:i + 2]
        if two in ("ts", "tʃ", "dʒ"): phones.append(two); i += 2
        else: phones.append(w[i]); i += 1
    pos, k = [], 0
    for p in phones: pos.append(k); k += len(p)
    vow = [n for n, p in enumerate(phones) if p in "aeiou"]
    if not vow: return w
    sv = next((n for n in vow if pos[n] >= stress_at), vow[-1]) if stress_at >= 0 else vow[-1]
    match = _vowel_letters(voc, [phones[n] for n in vow]) if voc else None
    cuts = []
    for j, (a, b) in enumerate(zip(vow, vow[1:])):
        if b - a - 1 <= 1: cuts.append(a + 1); continue                     # V.V, V.CV
        onset = False
        if match:
            at, cs = match
            run = [c for c in cs[at[j] + 1:at[j + 1]] if c[1] or c[0] not in "אהוי"]
            onset = bool(run) and SHVA in run[0][1] and DAGESH in run[0][1]
        cuts.append(a + 1 if onset else a + 2)
    sylls, start = [], 0
    for c in cuts + [len(phones)]:
        sylls.append((start, c)); start = c
    out = []
    for a, b in sylls:
        s = "".join(phones[a:b])
        for x, y in LAT: s = s.replace(x, y)
        out.append(s.upper() if a <= sv < b else s)
    return "-".join(x for x in out if x)


def say(voc):
    """How a vocalized word or phrase sounds, in Latin syllables: 'ha-sa-PAR'."""
    from phonikud import phonemize
    v = voc.replace("|", "")
    ipas, vws = phonemize(v).split(), v.split()
    return " ".join(sounds(x, vws[n] if len(ipas) == len(vws) else None) for n, x in enumerate(ipas))


# ------------------------------------------------------------------------------------------------- commands
def run(text, out_dir=None, name="text"):
    cut = None
    words = list(re.finditer(r"\S+", text))
    if tier() == "free" and len(words) > FREE_WORDS:
        cut = len(words); text = text[:words[FREE_WORDS - 1].end()]          # the first 150 words, lines kept
    pro = pro_lookup(text) if tier() != "free" else {}
    rows, voc = vocalize(text, pro)
    for r in rows:
        r["sounds"] = say(r["voc"]) if r["voc"] else ""
    n_auto = sum(r["source"] == "auto" for r in rows)
    lines = ["| # | מילה | ניקוד | הגייה | מקור |", "|---|---|---|---|---|"]
    lines += [f"| {i} | {r['word']} | {standard(r['voc'])} | {r['sounds']} | {r['source']} |" for i, r in enumerate(rows, 1)]
    table = "\n".join(lines)
    print(standard(voc)); print(); print(table); print()
    print(f"{len(rows)} words: {len(rows) - n_auto} from dictionaries, {n_auto} from automatic niqqud. Check the automatic "
          "ones with the user, above all names, loanwords and words with two meanings (סֵפֶר / סַפָּר). Fix a word for good "
          "with  python nq.py add-word <word> <niqqud>.")
    if tier() == "free" and n_auto: print(f"Free plan: {n_auto} words came from automatic niqqud only. {UPGRADE}")
    if cut: print(f"Free plan: the first {FREE_WORDS} of {cut} words. Mivta Pro vocalizes texts of any length.")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        outs = [("niqqud.txt", standard(voc)), ("table.md", table)]
        if tier() != "free": outs.insert(1, ("stress.txt", with_stress(voc)))
        for ext, body in outs:
            open(os.path.join(out_dir, f"{name}.{ext}"), "w", encoding="utf-8").write(body + "\n")
        print("-> " + ", ".join(f"{out_dir}/{name}.{ext}" for ext, _ in outs) +
              ("" if tier() != "free" else "   (the stress-marked copy is part of Mivta Pro)"))


def add_word(word, voc):
    if strip(voc) != strip(word) and fit(voc, word) is None:
        sys.exit(f"{voc} is not a spelling of {word}: give the niqqud on the same letters")
    d = json.load(open(USER_LEX, encoding="utf-8")) if os.path.exists(USER_LEX) else {}
    if tier() == "free" and word not in d and len(d) >= FREE_OWN_WORDS:
        sys.exit(f"The free plan keeps {FREE_OWN_WORDS} words of your own. {UPGRADE}")
    d[word] = voc; os.makedirs(HOME, exist_ok=True)
    json.dump(d, open(USER_LEX, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{word} -> {voc}  [{say(voc)}]  saved ({len(d)} {'word' if len(d) == 1 else 'words'} of your own)")


def set_settings(args):
    st = settings()
    for a in args:
        if a.startswith("--domains="): st["domains"] = a.split("=", 1)[1].split(",")
        if a.startswith("--style="): st["style"] = a.split("=", 1)[1]
    os.makedirs(HOME, exist_ok=True); json.dump(st, open(SETTINGS, "w"), indent=1); print(st)


def activate(key):
    import socket
    os.makedirs(os.path.dirname(LICENSE), exist_ok=True)
    if os.path.exists(LICENSE): os.remove(LICENSE)
    r = server("/activate", {"key": key, "instance": socket.gethostname()[:40]})
    if not r.get("ok"): sys.exit("licence not accepted: " + r.get("error", "unknown"))
    json.dump({"key": key, "instance_id": r.get("instance_id"), "tier": r.get("tier", "pro"), "expires": r.get("expires")},
              open(LICENSE, "w"))
    print(f"Mivta {r.get('tier', 'pro').capitalize()} is on: the shared dictionary is used from now on.")


def trial(email):
    r = server("/trial", {"email": email})
    if not r.get("ok"): sys.exit("trial refused: " + r.get("error", "unknown"))
    activate(r["key"]); print(f"Pro trial: {r.get('days', 7)} days.")


def doctor():
    ok = True
    def line(good, msg):
        nonlocal ok; ok &= good; print(("OK   " if good else "FIX  ") + msg)
    try:
        import phonikud, phonikud_onnx  # noqa: F401
        line(True, "Python packages (phonikud, phonikud-onnx)")
    except ImportError:
        line(False, "Python packages missing (bash setup.sh)")
    line(os.path.exists(MODEL), f"niqqud model {MODEL}")
    L = licence() or {}
    print(f"plan: {tier()}" + (f" (trial until {time.strftime('%Y-%m-%d', time.localtime(L['expires']))})" if L.get("expires") else ""))
    print("ready" if ok else "fix the lines above (bash setup.sh installs everything)")


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("help", [])
    out = next((a.split("=", 1)[1] for a in args if a.startswith("--out=")), None)
    if "--out" in args: out = args[args.index("--out") + 1]
    if cmd == "text": run(args[0], out, "text")
    elif cmd == "file":
        src = args[0]; run(open(src, encoding="utf-8").read(), out or os.path.dirname(os.path.abspath(src)),
                           os.path.splitext(os.path.basename(src))[0])
    elif cmd == "add-word": add_word(args[0], args[1])
    elif cmd == "settings": set_settings(args)
    elif cmd == "trial": trial(args[0])
    elif cmd == "activate": activate(args[0])
    elif cmd == "doctor": doctor()
    else: print(__doc__)
