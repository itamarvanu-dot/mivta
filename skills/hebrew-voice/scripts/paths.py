"""Where everything lives, and which plan is active. One data folder per user (HV_HOME, default ~/.mivta).

  HV_HOME/venv           tools: Phonikud niqqud, Whisper (Hebrew), phoneme recogniser   (override: HV_VENV)
  HV_HOME/venv_cb        the voice engine: Chatterbox Multilingual (MIT)               (override: HV_VENV_CB)
  HV_HOME/models         phonikud-1.0.int8.onnx
  HV_HOME/voices/<name>  ref.wav (the 10 s the engine copies), clips/, profile.pt (Pro), consent.json
  HV_HOME/user_lex.json  your own words (always win)
  HV_HOME/pro/           license.json (Pro / Studio / trial) and module/ (the Mivta Pro module, downloaded on activation)

Plans (what each one unlocks is enforced here, in hv.py and by the Mivta server; the licence terms forbid working
around it):
  free    one voice from one clip, one take per line, up to 10 lines per script, 20 starter words, 10 words of your
          own, no automatic QA; personal, non-commercial use
  pro     voice profile from minutes of speech, 3-5 takes per line + automatic QA and pick, the shared dictionary and
          the prefix engine, unlimited own words + sharing, stress repair, commercial use
  studio  pro + up to 5 voices, long-form split, narration export with subtitles, client work
"""
import os, json, time

HOME = os.path.abspath(os.environ.get("HV_HOME", os.path.expanduser("~/.mivta")))
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(SCRIPTS), "data")
VENV = os.environ.get("HV_VENV", os.path.join(HOME, "venv"))
VENV_CB = os.environ.get("HV_VENV_CB", os.path.join(HOME, "venv_cb"))
MODELS = os.path.join(HOME, "models")
VOICES = os.path.join(HOME, "voices")
USER_LEX = os.path.join(HOME, "user_lex.json")
PRO = os.path.join(HOME, "pro")
LICENSE = os.path.join(PRO, "license.json")
PRO_MODULE = os.path.join(PRO, "module")                  # mivta_pro/ + module.json, from the Mivta server
SETTINGS = os.path.join(HOME, "settings.json")
PHONIKUD_ONNX = os.environ.get("HV_PHONIKUD", os.path.join(MODELS, "phonikud-1.0.int8.onnx"))
FREE_LEX = os.path.join(DATA, "he_lexicon_free.jsonl")
DICT_SERVER = os.environ.get("HV_DICT_SERVER", "https://mivta.netlify.app")   # the Mivta website + server
SUPPORT = "mivta.ai@gmail.com"

LIMITS = {"free":   {"voices": 1, "seeds": 1, "lines": 10, "own_words": 10, "qa": False, "profile": False, "dictionary": False,
                     "long_form": False, "export": False},
          "pro":    {"voices": 1, "seeds": 5, "lines": None, "own_words": None, "qa": True, "profile": True, "dictionary": True,
                     "long_form": False, "export": False},
          "studio": {"voices": 5, "seeds": 5, "lines": None, "own_words": None, "qa": True, "profile": True, "dictionary": True,
                     "long_form": True, "export": True}}
UPGRADE = "This is part of Mivta Pro (python hv.py trial <email> = 7 days free, no card)."


def py(venv):
    return os.path.join(venv, "bin", "python")


def settings():
    """{"domains": [...], "style": "standard" | "colloquial", "voice": "me"} - dictionary scope and the active voice."""
    d = {"domains": ["general"], "style": "standard", "voice": "me"}
    if os.path.exists(SETTINGS):
        d.update(json.load(open(SETTINGS)))
    return d


def license():
    return json.load(open(LICENSE)) if os.path.exists(LICENSE) else None


def tier():
    L = license()
    if not L or not DICT_SERVER: return "free"
    if L.get("expires") and L["expires"] < time.time(): return "free"
    return L.get("tier", "pro")


def limit(name):
    return LIMITS[tier()][name]


VOICE = os.path.join(VOICES, settings()["voice"])          # the active voice
