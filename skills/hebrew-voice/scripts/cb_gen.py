"""Takes for a script in your cloned voice: Chatterbox Multilingual (MIT) reading OUR niqqud. Runs in the engine venv;
hv.py generate calls it after writing <out_dir>/cb_text.json.

  <HV_HOME>/venv_cb/bin/python cb_gen.py <script.json>
  -> <out_dir>/takes/<id>_s<k>.wav (24 kHz) + <id>_s<k>.json {"sim": likeness to your voice, 0..1}

Why our niqqud and not Chatterbox's own: its Hebrew step calls dicta_onnx.Dicta() without a model path, which fails,
and the text then goes in with no niqqud at all - 19-40% character errors on test lines, vs 0-3% with ours.
Likeness: the engine's own voice encoder (the identity model it clones with), take vs the mean of your clips.
"""
import sys, os, json, time, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
import numpy as np, torch, torchaudio, librosa
import chatterbox.models.tokenizers.tokenizer as TOK
from chatterbox.mtl_tts import ChatterboxMultilingualTTS, Conditionals

S = json.load(open(sys.argv[1])); OUT = S["out_dir"]; CB = S.get("cb", {})
T = json.load(open(f"{OUT}/cb_text.json"))
TOK.add_hebrew_diacritics = lambda s: s            # the text is already vocalized by us
torch.set_num_threads(os.cpu_count() or 2)
os.makedirs(f"{OUT}/takes", exist_ok=True)
todo = [(k, s) for k in S["lines"] for s in range(1, S["lines"][k].get("seeds", S.get("seeds", 3)) + 1)
        if not os.path.exists(f"{OUT}/takes/{k}_s{s}.wav")]
if not todo: print("nothing to generate", flush=True); sys.exit(0)
ref = CB.get("ref") or os.path.join(paths.VOICE, "ref.wav")
prof = CB.get("profile") or (None if CB.get("ref") else os.path.join(paths.VOICE, "profile.pt"))
if prof and not os.path.exists(prof): prof = None                # no profile yet: clone from the single best clip
if not os.path.exists(ref) and not prof:
    sys.exit(f"no voice yet: run  python hv.py voice <your recording> --consent  first ({ref} missing)")
t0 = time.time(); m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
if prof:
    m.conds = Conditionals.load(prof).to("cpu")
else:
    m.prepare_conditionals(ref, exaggeration=CB.get("exaggeration", 0.5))
clips = sorted(glob.glob(os.path.join(paths.VOICE, "clips", "*.wav"))) or [ref]
me = np.asarray(m.ve.embeds_from_wavs([librosa.load(c, sr=16000)[0] for c in clips], sample_rate=16000, as_spk=True))
print(f"engine loaded in {time.time() - t0:.0f}s, {len(todo)} takes", flush=True)
for k, s in todo:
    out = f"{OUT}/takes/{k}_s{s}.wav"; t = time.time()
    torch.manual_seed(1000 * s + 7)
    w = m.generate(T[k], language_id="he", exaggeration=CB.get("exaggeration", 0.5),
                   cfg_weight=CB.get("cfg_weight", 0.5), temperature=CB.get("temperature", 0.8))
    tmp = out + ".part.wav"; torchaudio.save(tmp, w, m.sr); os.replace(tmp, out)       # never a half-written take
    y16 = librosa.resample(w.squeeze(0).numpy(), orig_sr=m.sr, target_sr=16000)
    e = np.asarray(m.ve.embeds_from_wavs([y16], sample_rate=16000, as_spk=True))
    sim = float(np.dot(me, e) / (np.linalg.norm(me) * np.linalg.norm(e) + 1e-9))
    json.dump({"sim": round(sim, 3)}, open(out[:-4] + ".json", "w"))
    print(f"{k}_s{s}: {w.shape[-1] / m.sr:.2f}s in {time.time() - t:.0f}s, likeness {sim:.3f}", flush=True)
