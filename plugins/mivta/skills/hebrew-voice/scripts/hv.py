"""Mivta: your own voice, reading Hebrew with exact pronunciation.

  python hv.py doctor                          check the install, memory, disk, your voice and your plan
  python hv.py voice <recording> --consent     build your voice from 1-3 minutes of your own clean speech
  python hv.py review   script.json            word-by-word table: niqqud + stress the engine will read (CHECK IT)
  python hv.py generate script.json            record every line (CPU: ~40-60 s per take)
  python hv.py qa       script.json            Pro: transcription + phoneme + stress check of every take, best take -> picks/
  python hv.py add-word <word> <niqqud>        your correction, used from now on (mil'el: U+05AB on the stressed letter)
  python hv.py settings [--domains=general,diy] [--style=standard|colloquial]
  python hv.py trial <email>                   Pro free for 7 days, no card
  python hv.py activate <licence key>          Pro / Studio (the key is in the purchase email)
  python hv.py contribute <word>               Pro: share one of your words (only the word and its niqqud are sent)
  python hv.py profile                         Pro: rebuild the voice profile from all your clips
  python hv.py voices [use <name>]             Studio: list voices / switch the active one (up to 5)
  python hv.py split <text.txt> <out_dir>      Studio: a long text -> script.json, one sentence per line
  python hv.py export script.json              Studio: picks -> narration.wav (48 kHz, -16 LUFS) + narration.srt

Pro and Studio features live in the Mivta Pro module, which the Mivta server delivers to an active licence (trial
included) into HV_HOME/pro/module; this file loads it, checks it once a day, and removes it when the licence ends.

script.json = {"out_dir": "/abs/dir", "seeds": 3,
               "lines": {"L01": {"text": "<one sentence, up to ~8 s>"}, ...},
               "lex": {"word": "niqqud"} (optional, this script only), "asr_norm": {"ארבע עשרה": "14"} (optional)}
Run this file with the tools venv:  <HV_HOME>/venv/bin/python hv.py ...
"""
import os, sys, re, json, time, glob, subprocess, hashlib, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import numpy as np, soundfile as sf

ASR = os.environ.get("HV_ASR", "ivrit-ai/whisper-large-v3-turbo-ct2")
GRACE_DAYS = 14                     # Pro keeps working this long while the server cannot be reached


def need(feature):
    if not paths.limit(feature):
        sys.exit(("This is part of Mivta Studio." if feature in ("long_form", "export") else paths.UPGRADE))


def load(path):
    S = json.load(open(path)); os.makedirs(S["out_dir"], exist_ok=True); S["_path"] = os.path.abspath(path); return S


# ---------------------------------------------------------------------------------------------------- server + Pro
def _server(route, body, tries=5):
    """POST to the Mivta server; the licence key rides along when there is one. A sleeping server is woken up."""
    import urllib.request, urllib.error
    L = paths.license()
    if L: body = dict(body, key=L["key"], instance_id=L.get("instance_id"))
    data = json.dumps(body).encode()
    for attempt in range(tries):
        req = urllib.request.Request(paths.DICT_SERVER.rstrip("/") + route, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and attempt < tries - 1:
                if attempt == 0: print("waking up the Mivta server (up to a minute)...", flush=True)
                time.sleep(15); continue
            try: return json.loads(e.read().decode())
            except Exception: return {"ok": False, "error": f"server error {e.code}"}
        except Exception as e:                                   # no network, DNS, timeout
            if attempt < tries - 1:
                if attempt == 0: print("the Mivta server is not answering yet, retrying...", flush=True)
                time.sleep(15); continue
            return {"ok": False, "error": f"cannot reach the Mivta server ({e})", "offline": True}


def _end_licence(reason):
    """The server says the licence is no longer valid: back to the free plan, Pro module removed."""
    for p in (paths.LICENSE,):
        if os.path.exists(p): os.remove(p)
    shutil.rmtree(paths.PRO_MODULE, ignore_errors=True)
    sys.exit(f"Your Mivta licence is not active any more ({reason}), so this machine is back on the free plan. "
             f"To keep Pro: python hv.py activate <key>. Questions: {paths.SUPPORT}")


def fetch_module(force=False):
    """Download (or confirm) the Mivta Pro module for this licence into HV_HOME/pro/module. -> True when usable."""
    meta_p = os.path.join(paths.PRO_MODULE, "module.json")
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    have = os.path.exists(os.path.join(paths.PRO_MODULE, "mivta_pro", "__init__.py"))
    r = _server("/module", {"have": "" if force or not have else meta.get("version", "")})
    if not r.get("ok"):
        if r.get("licence") == "invalid": _end_licence(r.get("error", "not valid"))
        if have and time.time() - meta.get("fetched", 0) < GRACE_DAYS * 86400: return True
        print("Mivta Pro module not available: " + r.get("error", "unknown")); return False
    if r.get("files"):
        tmp = paths.PRO_MODULE + ".new"; shutil.rmtree(tmp, ignore_errors=True)
        for rel, text in r["files"].items():
            if rel.startswith("/") or ".." in rel.split("/") or not rel.startswith("mivta_pro/") or not rel.endswith(".py"):
                sys.exit("the Mivta Pro module looks wrong - not installed")
            p = os.path.join(tmp, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f: f.write(text)
        old = paths.PRO_MODULE + ".old"; shutil.rmtree(old, ignore_errors=True)
        if os.path.exists(paths.PRO_MODULE): os.replace(paths.PRO_MODULE, old)
        os.replace(tmp, paths.PRO_MODULE); shutil.rmtree(old, ignore_errors=True)
    json.dump({"version": r.get("version"), "fetched": time.time()}, open(meta_p, "w"))
    return True


_PRO = None
def pro(required=True):
    """The Mivta Pro module (Pro / Studio / trial), checked with the server once a day."""
    global _PRO
    if _PRO: return _PRO
    if paths.tier() == "free":
        if required: sys.exit(paths.UPGRADE)
        return None
    meta_p = os.path.join(paths.PRO_MODULE, "module.json")
    fresh = os.path.exists(meta_p) and time.time() - json.load(open(meta_p)).get("fetched", 0) < 86400
    if not fresh and not fetch_module():
        if required: sys.exit(f"The Mivta Pro module is not available right now. Try again soon, or write to {paths.SUPPORT}.")
        return None
    sys.path.insert(0, paths.PRO_MODULE)
    import mivta_pro
    _PRO = mivta_pro; return mivta_pro


def vocal(S):
    """Free dictionary < shared dictionary (Pro: this script's words only) < your words < this script's lex."""
    import heb_pron as H
    lex, phrases = dict(H.LEX), dict(H.PHRASES)
    P = pro(required=False)
    if P:
        P.hebrew.install(H)
        texts = [v["text"] for v in S["lines"].values()]
        cache = os.path.join(S["out_dir"], "pro_cache.json")
        c = json.load(open(cache, encoding="utf-8")) if os.path.exists(cache) else {}
        if c.get("texts") == texts and time.time() - os.path.getmtime(cache) < 7 * 86400:
            plex, pphr = c["lex"], c["phrases"]
        else:
            try:
                plex, pphr = P.hebrew.lookup(texts, _server, H.usable, H.strip_nikud)
                json.dump({"texts": texts, "lex": plex, "phrases": pphr}, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
            except LookupError as e:
                r = e.args[0] if e.args and isinstance(e.args[0], dict) else {}
                if r.get("licence") == "invalid": _end_licence(r.get("error", "not valid"))
                print(f"(the shared dictionary is not reachable right now: {r.get('error', e)}; using your own words and "
                      "the starter dictionary for this run)", flush=True)
                plex, pphr = {}, {}
        mine = {k for k, o in H.ORIGIN.items() if o == "mine"}
        lex.update({k: v for k, v in plex.items() if k not in mine}); phrases.update({k: v for k, v in pphr.items() if k not in mine})
        for k in plex:
            if k not in mine: H.ORIGIN[k] = "pro"
    lex.update(S.get("lex", {}))
    return {k: H.vocalize(v["text"], lex, phrases) for k, v in S["lines"].items()}


# ---------------------------------------------------------------------------------------------------------- review
def review(S):
    import heb_pron as H
    V = vocal(S); rows = []
    for k, (voc, ipa) in V.items():
        tw = [w for w in S["lines"][k]["text"].split() if w not in ("—", "–")]
        vw = [w for w in voc.split() if w not in ("—", "–")]
        iw = ipa.split()
        for i, w in enumerate(tw):
            plain = H.plain_word(w)
            src = H.SRC.get(plain, "auto")
            if src == "LEX": src = {"free": "dictionary", "pro": "dictionary(Pro)", "mine": "your word"}.get(H.ORIGIN.get(plain), "dictionary")
            if plain in S.get("lex", {}): src = "script lex"
            rows.append([k, w, vw[i] if i < len(vw) else "?", iw[i] if i < len(iw) else "?", src])
    with open(f"{S['out_dir']}/review.tsv", "w") as f:
        for r in rows: f.write("\t".join(r) + "\n")
    for r in rows: print(f"{r[0]:5s} {r[1]:14s} {r[2]:20s} {r[3]:16s} {r[4]}")
    n_auto = sum(r[4] == "auto" for r in rows)
    print(f"\n{len(rows)} words, {n_auto} from automatic niqqud -> {S['out_dir']}/review.tsv\n"
          "Check EVERY word: the stress (ˈ comes before the stressed vowel) and the vowels. Fix a wrong word with\n"
          "  python hv.py add-word <word> <niqqud>     (all scripts)   or the script's \"lex\" (this script only)")
    if paths.tier() == "free":
        print(f"Free plan: {n_auto} words came from automatic niqqud only. Pro checks them against the shared, verified "
              "dictionary and builds every prefixed form of a dictionary word. " + paths.UPGRADE)


# -------------------------------------------------------------------------------------------------------- generate
def cb_text(S):
    """Our niqqud for the engine. By default the stress mark (U+05AB) and the vocal-shva mark (U+05BD) are dropped:
    they are outside the engine's training text. Pro: a line with "stress_marks": true keeps them (stress repair).
    Test, Oct 2026 (one sentence, 4 mil'el words, 3 seeds): marks kept -> stress right 9/12 vs 3/12 without, but the
    takes sounded less like the speaker; so off by default, on for a line whose takes all fail the stress check."""
    V = vocal(S); T = {}
    for k, (v, ipa) in V.items():
        keep = paths.tier() != "free" and S["lines"][k].get("stress_marks", S.get("cb", {}).get("stress_marks", False))
        T[k] = v.replace("|", "") if keep else re.sub("[ֽ֫|]", "", v)
    json.dump(T, open(f"{S['out_dir']}/cb_text.json", "w"), ensure_ascii=False, indent=1); return T


def generate(S):
    """Takes per line within the plan: free = 1 take and 10 lines per script; Pro/Studio = up to 5 takes."""
    import signal
    n_lines = paths.limit("lines")
    if n_lines and len(S["lines"]) > n_lines:
        sys.exit(f"The free plan records up to {n_lines} lines per script (this one has {len(S['lines'])}). " + paths.UPGRADE)
    cap = paths.limit("seeds")
    run = {k: v for k, v in S.items() if k != "_path"}
    run["seeds"] = min(S.get("seeds", 3), cap)
    run["lines"] = {k: dict(v, seeds=min(v.get("seeds", run["seeds"]), cap)) for k, v in S["lines"].items()}
    path = os.path.join(S["out_dir"], "_run.json"); json.dump(run, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cb_text(S)
    p = subprocess.Popen([paths.py(paths.VENV_CB), os.path.join(paths.SCRIPTS, "cb_gen.py"), path])
    signal.signal(signal.SIGTERM, lambda *a: (p.terminate(), sys.exit(1)))
    sys.exit(p.wait())


# -------------------------------------------------------------------------------------------------------------- qa
def _to_pick(src, dst):
    from scipy.signal import resample_poly
    y, sr = sf.read(src, dtype="float32")
    sf.write(dst, resample_poly(y, 2, 1).astype(np.float32) if sr == 24000 else y, 48000 if sr == 24000 else sr)


def qa(S):
    os.makedirs(f"{S['out_dir']}/picks", exist_ok=True)
    if not paths.limit("qa"):                       # free: the one take per line becomes the pick, unchecked
        for p in sorted(glob.glob(f"{S['out_dir']}/takes/*_s1.wav")):
            _to_pick(p, f"{S['out_dir']}/picks/{os.path.basename(p)[:-7]}.wav")
        sys.exit(f"picks -> {S['out_dir']}/picks/ (unchecked: listen to every line). Automatic checking of every word, "
                 "with several takes per line to choose from, " + paths.UPGRADE[len("This "):])
    P = pro()
    # the engine holds ~5 GB: Whisper + the phoneme model beside it can get the generator killed on an 8 GB machine
    while subprocess.run(["pgrep", "-f", "cb_gen.py"], capture_output=True).returncode == 0:
        print("the generator is still running - QA waits (memory)", flush=True); time.sleep(60)
    P.qa.run(S, vocal(S), ASR, _to_pick)


# ----------------------------------------------------------------------------------------------------------- voice
CONSENT = ("I confirm that this recording is my own voice, or that I have the speaker's written permission to clone it, "
           "and that I will not use the cloned voice to deceive anyone.")


def voice(rec, consent, name=None):
    """1-3 minutes of one speaker, no music -> voices/<name>/ref.wav (the best 10 s, what the engine copies),
    clips/ (the next best 10 s windows), consent.json, and on Pro the voice profile built from all of them."""
    import librosa
    if not consent:
        sys.exit("Cloning needs consent. Read this, and if it is true, run the same command with --consent:\n  " + CONSENT)
    name = name or paths.settings()["voice"]
    existing = [d for d in os.listdir(paths.VOICES) if os.path.isdir(os.path.join(paths.VOICES, d))] if os.path.exists(paths.VOICES) else []
    if name not in existing and len(existing) >= paths.limit("voices"):
        sys.exit(f"Your plan holds {paths.limit('voices')} voice(s) ({', '.join(existing)}). Studio holds up to 5.")
    vdir = os.path.join(paths.VOICES, name)
    y, sr = librosa.load(rec, sr=24000, mono=True)
    if len(y) < 20 * sr: sys.exit("need at least 20 s of speech (1-3 minutes is best)")
    hop = int(0.01 * sr); n = len(y) // hop
    db = 20 * np.log10(np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, 1)) + 1e-9)
    floor = np.percentile(db, 10); speech = db > floor + 15; clip = np.abs(y[:n * hop]).reshape(n, hop).max(1) > 0.99
    W = 1000                                                        # 10 s in 10 ms frames
    cand = []
    for s in range(0, n - W, 50):
        sp = speech[s:s + W].mean(); cl = clip[s:s + W].mean()
        runs = np.diff(np.flatnonzero(np.diff(np.r_[0, ~speech[s:s + W], 0]))) if (~speech[s:s + W]).any() else np.array([0])
        longest_pause = runs[::2].max() if len(runs) else 0
        score = sp - 5 * cl - 0.004 * max(0, longest_pause - 60)       # talk most of the window, no clipping, no long gap
        cand.append((score, s))
    cand.sort(reverse=True); chosen = []
    for score, s in cand:                                           # non-overlapping windows, best first
        if all(abs(s - c) >= W for _, c in chosen): chosen.append((score, s))
        if len(chosen) == 31: break
    os.makedirs(os.path.join(vdir, "clips"), exist_ok=True)
    for f in glob.glob(os.path.join(vdir, "clips", "*.wav")) + glob.glob(os.path.join(vdir, "profile.pt")): os.remove(f)
    peak = lambda x: x / (np.abs(x).max() + 1e-9) * 0.89
    s0 = chosen[0][1] * hop; sf.write(os.path.join(vdir, "ref.wav"), peak(y[s0:s0 + 10 * sr]), sr)
    for i, (_, s) in enumerate(chosen[1:]):
        sf.write(os.path.join(vdir, "clips", f"c{i:02d}.wav"), peak(y[s * hop:s * hop + 10 * sr]), sr)
    json.dump({"statement": CONSENT, "confirmed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "recording": os.path.basename(rec),
               "sha256": hashlib.sha256(open(rec, "rb").read()).hexdigest(), "seconds": round(len(y) / sr, 1)},
              open(os.path.join(vdir, "consent.json"), "w"), indent=1)
    st = paths.settings(); st["voice"] = name; json.dump(st, open(paths.SETTINGS, "w"), indent=1)
    print(f"voice '{name}' ready: the engine copies {chosen[0][1] / 100:.1f}-{chosen[0][1] / 100 + 10:.1f} s of the "
          f"recording, {len(chosen) - 1} more clips -> {vdir}")
    if paths.limit("profile"):
        profile()
    else:
        print("Free plan: cloned from one 10 s clip. A profile built from all your minutes sounds more like you. " + paths.UPGRADE)


def profile():
    need("profile"); P = pro()
    env = dict(os.environ, HV_SCRIPTS=paths.SCRIPTS, HV_HOME=paths.HOME)
    r = subprocess.run([paths.py(paths.VENV_CB), os.path.join(P.DIR, "cb_profile.py")], env=env)
    if r.returncode: sys.exit("profile not built (see above)")


def voices(args):
    have = sorted(d for d in os.listdir(paths.VOICES) if os.path.isdir(os.path.join(paths.VOICES, d))) if os.path.exists(paths.VOICES) else []
    if args[:1] == ["use"]:
        if args[1] not in have: sys.exit(f"no voice '{args[1]}' (have: {', '.join(have) or 'none'})")
        st = paths.settings(); st["voice"] = args[1]; json.dump(st, open(paths.SETTINGS, "w"), indent=1)
        print(f"active voice: {args[1]}"); return
    cur = paths.settings()["voice"]
    for d in have:
        prof = os.path.exists(os.path.join(paths.VOICES, d, "profile.pt"))
        print(f"{'*' if d == cur else ' '} {d:12s} {'profile' if prof else 'one clip'}")
    print(f"{len(have)} of {paths.limit('voices')} voices. New one: python hv.py voice <recording> --consent --name=<name>")


# ------------------------------------------------------------------------------------------------- your dictionary
def add_word(word, voc):
    from phonikud import phonemize
    d = json.load(open(paths.USER_LEX, encoding="utf-8")) if os.path.exists(paths.USER_LEX) else {}
    cap = paths.limit("own_words")
    if cap and word not in d and len(d) >= cap:
        sys.exit(f"The free plan keeps {cap} words of your own. " + paths.UPGRADE)
    d[word] = voc; os.makedirs(paths.HOME, exist_ok=True)
    json.dump(d, open(paths.USER_LEX, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{word} -> {voc}  [{phonemize(voc)}]  saved to your dictionary ({len(d)} words)." +
          (" Prefixed forms follow automatically." if paths.tier() != "free" else ""))


def set_settings(args):
    st = paths.settings()
    for a in args:
        if a.startswith("--domains="): st["domains"] = a.split("=", 1)[1].split(",")
        if a.startswith("--style="): st["style"] = a.split("=", 1)[1]
    os.makedirs(paths.HOME, exist_ok=True); json.dump(st, open(paths.SETTINGS, "w"), indent=1); print(st)


# --------------------------------------------------------------------------------------------------------- Studio
def split(textfile, out_dir):
    need("long_form"); pro().studio.split(textfile, out_dir)


def export(S):
    need("export"); pro().studio.export(S)


# ------------------------------------------------------------------------------------------------------- licences
def install_id():
    """A random name for this installation (shared with Mivta Niqqud): the licence's activation label, never the
    computer's name."""
    p = os.path.join(paths.HOME, "install_id")
    if not os.path.exists(p):
        import secrets
        os.makedirs(paths.HOME, exist_ok=True); open(p, "w").write("mivta-" + secrets.token_hex(4))
    return open(p).read().strip()[:40]


def activate(key):
    os.makedirs(paths.PRO, exist_ok=True)
    if os.path.exists(paths.LICENSE): os.remove(paths.LICENSE)        # the new key, not the old one, rides along
    r = _server("/activate", {"key": key, "instance": install_id()})
    if not r.get("ok"): sys.exit("licence not accepted: " + r.get("error", "unknown"))
    json.dump({"key": key, "instance_id": r.get("instance_id"), "tier": r.get("tier", "pro"), "expires": r.get("expires")},
              open(paths.LICENSE, "w"))
    if not fetch_module(force=True):
        sys.exit(f"The licence is active, but the Mivta Pro module did not download. Run the command again in a minute, "
                 f"or write to {paths.SUPPORT}.")
    print(f"Mivta {r.get('tier', 'pro').capitalize()} is on." + (" Run  python hv.py profile  to build your voice profile."
                                                                 if os.path.exists(os.path.join(paths.VOICE, "ref.wav")) else ""))


def trial(email):
    r = _server("/trial", {"email": email})
    if not r.get("ok"): sys.exit("trial refused: " + r.get("error", "unknown"))
    activate(r["key"]); print(f"Pro trial: {r.get('days', 7)} days.")


def contribute(word):
    from phonikud import phonemize
    d = json.load(open(paths.USER_LEX, encoding="utf-8")) if os.path.exists(paths.USER_LEX) else {}
    if word not in d: sys.exit(f"{word} is not in your dictionary (add-word it first)")
    need("dictionary")
    r = _server("/contribute", {"word": word, "voc": d[word], "ipa": phonemize(d[word])})
    print("thanks - it goes through the checks and joins the shared dictionary once verified" if r.get("ok") else r)


# --------------------------------------------------------------------------------------------------------- doctor
def doctor():
    ok = True
    def line(good, msg):
        nonlocal ok; ok &= good; print(("OK   " if good else "FIX  ") + msg)
    line(os.path.exists(paths.py(paths.VENV)), f"tools venv {paths.VENV}")
    line(os.path.exists(paths.py(paths.VENV_CB)), f"engine venv {paths.VENV_CB}")
    line(os.path.exists(paths.PHONIKUD_ONNX), f"niqqud model {paths.PHONIKUD_ONNX}")
    line(os.path.exists(os.path.join(paths.VOICE, "ref.wav")), f"voice '{paths.settings()['voice']}' (python hv.py voice <recording> --consent)")
    mem = int(open("/proc/meminfo").read().split("MemTotal:")[1].split()[0]) / 1e6 if os.path.exists("/proc/meminfo") else 0
    line(mem == 0 or mem >= 7, f"memory {mem:.1f} GB (the engine needs ~5 GB; run QA only after generate finishes)")
    st = os.statvfs(paths.HOME if os.path.exists(paths.HOME) else os.path.expanduser("~"))
    line(st.f_bavail * st.f_frsize / 1e9 > 2, f"free disk {st.f_bavail * st.f_frsize / 1e9:.1f} GB")
    t = paths.tier()
    if t != "free":
        line(pro(required=False) is not None, f"Mivta Pro module {getattr(_PRO, 'VERSION', '(not downloaded)')}")
    L = paths.license() or {}
    print(f"plan: {t}" + (f" (trial until {time.strftime('%Y-%m-%d', time.localtime(L['expires']))})" if L.get("expires") else ""))
    print("ready" if ok else "fix the lines above (setup.sh installs everything)")


if __name__ == "__main__":
    cmd, args = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("help", [])
    if cmd in ("review", "generate", "qa", "cbtext", "export"):
        {"review": review, "generate": generate, "qa": qa, "cbtext": cb_text, "export": export}[cmd](load(args[0]))
    elif cmd == "voice":
        nm = next((a.split("=", 1)[1] for a in args if a.startswith("--name=")), None)
        voice(args[0], "--consent" in args, nm)
    elif cmd == "profile": profile()
    elif cmd == "voices": voices(args)
    elif cmd == "split": split(args[0], args[1])
    elif cmd == "add-word": add_word(args[0], args[1])
    elif cmd == "settings": set_settings(args)
    elif cmd == "activate": activate(args[0])
    elif cmd == "trial": trial(args[0])
    elif cmd == "contribute": contribute(args[0])
    elif cmd == "doctor": doctor()
    else: print(__doc__)
