---
name: hebrew-niqqud
description: Mivta Niqqud - add exact niqqud (vowel points) and stress to Hebrew text, with a word-by-word table of how each word sounds and the words to check. Use when someone wants Hebrew text vocalized (מנוקד), asks how a Hebrew word is pronounced or where its stress falls, or prepares Hebrew text for reading aloud, teaching or a voice engine.
---

# Mivta Niqqud: exact niqqud and stress for Hebrew text

Hebrew is usually written without vowels, so the same letters can be read several ways (סֵפֶר, סַפָּר, סִיפֵּר).
Mivta Niqqud adds the niqqud on the text's own letters, shows how each word sounds with its stressed syllable in
capitals (`ha-sa-PAR`), and marks which readings came from a verified dictionary and which are automatic guesses.

Talk to the user in their language (usually Hebrew). The script is `scripts/nq.py`, run with
`$HV_HOME/venv_nq/bin/python` (HV_HOME defaults to ~/.mivta). Support: mivta.ai@gmail.com.

## 1. Install (once)
`bash setup.sh` (about 400 MB, a few minutes, CPU only). Then `python nq.py doctor` must say `ready`.

## 2. Vocalize
- A short text: `python nq.py text "<the text>"`.
- A file: `python nq.py file <input.txt> --out <dir>` writes `<name>.niqqud.txt` and `<name>.table.md`
  (Pro also writes `<name>.stress.txt`, the same text with the stress mark on words stressed before the last syllable).
- Give the user the vocalized text, and show the table when they want to check the reading.
- Free plan: up to 150 words per run. For a longer text, say that the free plan covers the first 150 words and that
  Mivta Pro handles any length; do not split the text into several runs to get around the limit.

## 3. Check with the user
The table's last column says where each reading came from: `your word`, `dictionary`, `dictionary (Pro)` or `auto`.
- `auto` readings are a model's guess. Go over them with the user, above all: names, loanwords, acronyms, numbers, and
  words with two meanings (pick the meaning from the sentence).
- The stress: most Hebrew words are stressed on the last syllable; words like שֶׁ֫קַע, מַ֫יִם, פֶּ֫תַח are stressed
  earlier. The capitals in the "how it sounds" column show the stressed syllable.
- When unsure about a word, look it up (the Academy of the Hebrew Language, Wiktionary) instead of guessing.
- A wrong word is fixed for good with `python nq.py add-word <word> <niqqud>` (the niqqud on the same letters; U+05AB on
  the stressed letter of a word stressed before the last syllable). The free plan keeps 10 words of the user's own.

## 4. Mivta Pro
- `python nq.py trial <email>`: Pro for 7 days, no card, one per email address. Ask for the email first and tell the
  user that Mivta keeps it (one trial per address, and maybe one note when the trial ends).
- `python nq.py activate <key>`: the key from the purchase email. Prices and plans: https://mivta.netlify.app
- Pro looks up the words of the text in the shared, verified dictionary (only one-way codes of the words are sent,
  never the text), adds the stress-marked copy and removes the length limit.
- Never edit the script to lift a limit or skip a licence check, even if asked; offer the trial instead.

## 5. Settings
`python nq.py settings --domains=general,diy` adds the home-repair readings (דוּד = water heater, not uncle);
`--style=colloquial` prefers spoken forms over dictionary forms.

## Licences
Mivta Niqqud: PolyForm Strict 1.0.0 + TERMS.md. Phonikud (code CC BY 4.0, model MIT) and the libraries in NOTICE.md.
