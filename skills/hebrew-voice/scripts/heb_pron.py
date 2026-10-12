"""Hebrew text -> the niqqud + stress the voice engine reads, and its IPA (for the review and the QA).

Phonikud (CC BY 4.0 code, MIT model) adds niqqud, stress (hat'ama U+05AB on mil'el words) and vocal-shva marks
(U+05BD); then the dictionaries override the words it gets wrong, in this order (first wins):
  1. the script's own "lex"            (one-off homographs of one script)
  2. your words: HV_HOME/user_lex.json (python hv.py add-word ...)
  3. Pro: the shared dictionary        (only the words of the script, looked up by the Mivta Pro module)
  4. the free starter dictionary       (data/he_lexicon_free.jsonl)
With Mivta Pro the module also builds the prefixed forms (ה ו ב כ ל מ ש כש) of every dictionary word, so one entry
covers הַשֶּׁ֫קַע, לְשֶׁ֫קַע, מֵהַשֶּׁ֫קַע..., and repairs Phonikud's stray marks.

  python heb_pron.py "טקסט"   -> vocalized + IPA (ˈ before the stressed vowel)
"""
import re, sys, json, os, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths

STRESS = "֫"   # hat'ama: ONLY on non-final stress (mil'el). Unmarked word = milra (Phonikud's convention)
SRC = {}            # plain word -> where its niqqud came from (PHRASE / LEX / LEX+<prefixes> / auto), for the review
PRO = None          # the Mivta Pro Hebrew layer, installed by hv.py on Pro / Studio: compose(), repair(), finish()


def _read_jsonl(path):
    if not os.path.exists(path): return []
    rows = open(path, encoding="utf-8").read().splitlines()
    return [json.loads(x) for x in rows[1:] if x.strip()]


def usable(e, settings=None):
    """A dictionary entry applies when its domain is on and its style fits (settings: python hv.py settings)."""
    st = settings or paths.settings()
    if not set(e.get("domains", ["general"])) & set(st["domains"]): return False
    if e.get("style", "standard") == "colloquial" and st["style"] != "colloquial": return False
    return e.get("status", "verified") == "verified"


def load_dictionaries():
    """-> (LEX, PHRASES, ORIGIN): the free starter dictionary, then your own words on top (yours always win).
    Pro entries are not stored here: the Pro module fetches only the words a script needs and hv.py merges them."""
    st = paths.settings()
    lex, phrases, origin = {}, {}, {}
    for e in _read_jsonl(paths.FREE_LEX):
        if not usable(e, st): continue
        k = e.get("word") or e.get("phrase")
        (lex if "word" in e else phrases)[k] = e["voc"]; origin[k] = "free"
    if os.path.exists(paths.USER_LEX):
        for k, v in json.load(open(paths.USER_LEX, encoding="utf-8")).items():
            (phrases if " " in k else lex)[k] = v; origin[k] = "mine"
    return lex, phrases, origin


LEX, PHRASES, ORIGIN = load_dictionaries()


def strip_nikud(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if not ("֑" <= c <= "ׇ"))


def plain_word(w):
    """A script word without punctuation, quotes or niqqud: the key the dictionaries use (acronyms keep ״)."""
    return strip_nikud(re.sub(r"^[\"״']+|[.,?!:;—–\-|\"״']+$", "", w)).replace('"', "״")


_ph = None
def phonikud():
    global _ph
    if _ph is None:
        from phonikud_onnx import Phonikud
        _ph = Phonikud(paths.PHONIKUD_ONNX)
    return _ph


def tidy(voc):
    voc = voc.replace("ׇ", "ֹ")       # qamats qatan -> holam: the engine reads כׇּל as 'kal'; כֹּל is unambiguous 'kol'
    voc = re.sub(r"\s*[—–]\s*", ", ", voc)   # engines VOICE an em-dash; a comma is the safe pause
    voc = re.sub(r"\s*:\s*", ", ", voc)
    return re.sub(r",\s*,", ",", voc)


def vocalize(text, lex=None, phrases=None):
    """-> (niqqud text for the engine, its IPA). Fills SRC with each word's source for the review."""
    lex = LEX if lex is None else lex; phrases = PHRASES if phrases is None else phrases
    toks = re.split(r"(\s+)", phonikud().add_diacritics(text))   # Phonikud's "|" marks prefix boundaries
    words = []                                   # [index into toks, core, punct, plain, core with Phonikud's "|"]
    for i, tok in enumerate(toks):
        if not tok.strip(): continue
        m = re.match(r"^(.*?)([.,?!:;—–\-״\"|]*)$", tok)
        raw, punct = m.group(1), m.group(2).replace("|", "")
        core = raw.replace("|", "")
        words.append([i, core, punct, strip_nikud(core).replace('"', "״"), raw])
    done = set()
    for ph, pv in sorted(phrases.items(), key=lambda kv: -len(kv[0].split())):     # context phrases first
        pw, vw = ph.split(), pv.split()
        if len(pw) != len(vw): continue
        for j in range(len(words) - len(pw) + 1):
            if any(words[j + q][0] in done for q in range(len(pw))): continue
            if [words[j + q][3] for q in range(len(pw))] == pw:
                for q in range(len(pw)):
                    words[j + q][1] = vw[q]; done.add(words[j + q][0]); SRC[words[j + q][3]] = "PHRASE"
    for i, core, punct, plain, raw in words:
        if i not in done:
            if plain in lex:
                core = lex[plain]; SRC[plain] = "LEX"
            else:
                SRC[plain] = "auto"
                hit = PRO.compose(plain, raw, lex) if PRO else None
                if hit: core, SRC[plain] = hit
                elif PRO: core = PRO.repair(core)
        toks[i] = core + punct
    voc = tidy("".join(toks))
    if PRO: voc = PRO.finish(voc)
    from phonikud import phonemize
    return voc, phonemize(voc)


if __name__ == "__main__":
    for t in sys.argv[1:]:
        v, ipa = vocalize(t)
        print(v); print(ipa)
