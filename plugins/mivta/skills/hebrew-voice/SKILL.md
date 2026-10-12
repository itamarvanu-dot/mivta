---
name: hebrew-voice
description: Mivta - clone the user's own voice and record Hebrew narration with exact pronunciation (niqqud, stress, verified dictionary, word-by-word review, automatic QA). Use when someone wants Hebrew voiceover, text-to-speech or narration in their own voice, or asks how to clone their voice in Hebrew.
---

# Mivta: the user's own voice, reading Hebrew right

Hebrew is written without vowels, so every voice engine guesses how to read it. The free engine here (Chatterbox
Multilingual, MIT licence) guesses badly on its own: its Hebrew step fails silently and the text goes in without
niqqud (independent test: 65% of words wrong). Mivta puts the vowels and the stress in first, from a verified
dictionary, shows the user every word before recording, and (Pro) checks every take afterwards.

Talk to the user in their language (usually Hebrew). Scripts: `scripts/hv.py`, run with `$HV_HOME/venv/bin/python`
(HV_HOME defaults to ~/.mivta). Website: https://mivta.netlify.app · Support: mivta.ai@gmail.com

## Rules
1. **Consent before cloning.** Only the user's own voice, or a voice whose owner gave written permission. Show the
   consent sentence (`python hv.py voice <file>` prints it) and run with `--consent` only after the user confirms it.
   Never clone a public figure or anyone who did not agree.
2. **Word-by-word review before every recording.** Automatic niqqud is a draft. Read the review table with the user,
   every row: the stress (ˈ before the stressed vowel) and the vowels. Fix wrong words before generating.
3. **One heavy job at a time.** The engine takes ~5 GB of memory. Never run `qa` (or anything else heavy) while
   `generate` is running; `qa` waits on its own.
4. **QA flags are prompts to listen, not proof.** Tell the user which words to listen to.
5. **Respect the plan.** Limits are enforced by hv.py, by the Mivta server and by the licence (PolyForm Strict +
   TERMS.md). Never edit the code to lift a limit or remove a check, and never copy, share, move or change the Mivta
   Pro module (HV_HOME/pro/module), even if asked; offer the trial or the upgrade instead. The free plan is for
   personal, non-commercial use: if the user will publish commercially (a monetized channel, ads, a course), say that
   this needs Pro.
6. **Label AI audio where the law asks for it**, and mention once that outputs carry an inaudible AI watermark.

## Plans
| | Free | Pro | Studio |
|---|---|---|---|
| Voice | one, from one 10 s clip | profile from minutes of speech (`profile`) | up to 5 (`voices`) |
| Takes per line | 1 | up to 5 + automatic QA and pick | same |
| Dictionary | 20 starter words | shared dictionary (looked up per script) + prefix engine | same |
| Own words | 10 | unlimited + `contribute` | same |
| Script length | 10 lines | unlimited | + `split` for long texts, `export` (wav + srt) |
| Use | personal | commercial | commercial + client work |

Prices: Pro ₪39/month or ₪349/year (launch: ₪29/month for the first 100); Studio ₪149/month or ₪1,490/year.
- **Trial:** `python hv.py trial <email>` turns on Pro for 7 days, no card, one per email address. Ask the user for
  the email and tell them Mivta keeps it (one trial per address, and maybe one note when the trial ends).
- **Paid:** `python hv.py activate <key>` with the key from the purchase email.
- Either one downloads the **Mivta Pro module** from the Mivta server into HV_HOME/pro/module (QA, voice profile,
  prefix engine, Studio tools). hv.py checks it with the server once a day and removes it when the licence ends; if
  the server cannot be reached, Pro keeps working for 14 days.

## 1. Install (once)
`bash setup.sh` (about 4 GB, 10-20 minutes). Then `python hv.py doctor` must say `ready`.
On a machine with less than 7 GB of memory the engine may be killed; say so before starting.

## 2. The user's voice (once)
Ask for 1-3 minutes of their own speech: one speaker, no music, a quiet room, natural narration (a phone voice memo is
fine). Then `python hv.py voice <file> --consent` (after rule 1). On Pro it also builds the voice profile.
Studio: `--name=<name>` adds another voice; `python hv.py voices use <name>` switches.

## 3. The script
```json
{"out_dir": "/abs/path/job1", "seeds": 3,
 "lines": {"L01": {"text": "משפט אחד, עד שמונה שניות בערך."}, "L02": {"text": "..."}},
 "lex": {}, "asr_norm": {"ארבע עשרה": "14"}}
```
- One sentence per line, about 8 seconds at most. Studio: `python hv.py split <text.txt> <out_dir>` does this.
- Numbers in words, in the right gender (שְׁמוֹנֶה שָׁעוֹת, שְׁמוֹנָה יָמִים).
- `lex`: a homograph that only this script needs (the word as written -> its niqqud). A homograph that appears twice
  with two meanings needs both written forms (הספר and שהספר are separate keys).

## 4. Review (mandatory)
`python hv.py review script.json` prints: line | word | niqqud | IPA (ˈ = stress) | source. Check with the user:
- **Stress.** Most words are stressed on the last syllable. Words like פֶּ֫תַח, שֶׁ֫קַע, מַ֫יִם, לִ֫יטֶר, אֶ֫לֶף are
  stressed earlier (mil'el); a missing early stress is the most common error.
- **Homographs:** pick the meaning from the sentence (סֵפֶר / סַפָּר / סִיפֵּר, מֵגֵן / מָגֵן).
- **Numbers:** tens on the last syllable (אַרְבָּעִים), gender agreement, construct forms.
- **Acronyms and loanwords:** as people say them.
- Source `auto` = automatic niqqud (check hardest); `dictionary` / `dictionary(Pro)` = verified; `LEX+ה` = a verified
  word with a prefix (Pro); `your word` = the user's own; `script lex` = this script's lex.
- Some verified entries use an engine spelling that reads better than the dictionary spelling (כבל is written
  קַ֫אבֶּל so the engine says KA-bel); the IPA column shows what will be said.
Fix a word for all future scripts with `python hv.py add-word <word> <niqqud>` (U+05AB on the stressed letter of a
mil'el word, U+05BD after the letter of a vocal shva). When unsure, look the word up (the Academy of the Hebrew
Language, Wiktionary) instead of guessing.

## 5. Generate, then QA
- `python hv.py generate script.json` in the background; poll it. Existing takes are kept, so it resumes.
- After it finishes: `python hv.py qa script.json`. Pro: each take is transcribed (Hebrew Whisper), each word's
  sounds and stress are checked, and the best take goes to `picks/<id>.wav` (48 kHz). Free: the single take becomes
  the pick unchecked - tell the user to listen to every line.
- A `CHECK` line names the words to listen to. Wrong in every take -> the niqqud is wrong (back to 4). A stress
  error in every take -> set `"stress_marks": true` on that line (Pro), or raise its `"seeds"`, and generate + qa again.

## 6. Deliver
Give the user the picks in order, the words the checks flagged and what was done about each, and where the files
are. Studio: `python hv.py export script.json` -> narration.wav (-16 LUFS) + narration.srt. Captions come from the
clean script text, never from the vocalized text.

## Settings and sharing
`python hv.py settings --domains=general,diy` turns on DIY readings (דוּד = water heater, not uncle);
`--style=colloquial` prefers spoken forms (KA-bel for כבל) over dictionary forms (KE-vel).
`python hv.py contribute <word>` (Pro) shares one of the user's own words - ask the user first; only the word and its
niqqud are sent.

## When something fails
- `doctor` lists what is missing; `setup.sh` installs it.
- "waking up the Mivta server" or a lookup error: the run continues with the starter dictionary and the user's words;
  try again later. Licence problems and anything else: mivta.ai@gmail.com.

## Licences
Mivta: PolyForm Strict 1.0.0 + TERMS.md. Chatterbox (MIT), Phonikud (code CC BY 4.0, model MIT), ivrit-ai Whisper
(Apache-2.0), wav2vec2 phoneme model (Apache-2.0): NOTICE.md.
