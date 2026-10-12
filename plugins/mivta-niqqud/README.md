# Mivta Niqqud (מבטא ניקוד)

**Exact Hebrew niqqud and stress for any text.** Mivta Niqqud is a Claude plugin that adds vowel points (niqqud) to
Hebrew text on the text's own letters, shows how each word sounds with its stressed syllable, and lists the words worth
a second look: names, loanwords and words with two meanings (סֵפֶר / סַפָּר). It is for teachers, parents, students,
narrators, and anyone preparing Hebrew text for reading aloud or for a voice engine.

**ניקוד והטעמה מדויקים לכל טקסט בעברית.** מוסיף ניקוד על האותיות של הטקסט עצמו, מראה איך כל מילה נשמעת ואיפה
ההטעמה, ומסמן את המילים שכדאי לבדוק.

Website: https://mivta.netlify.app/niqqud/ · Support: mivta.ai@gmail.com

## What you get
- The text with niqqud, as a file you can print or paste.
- A table: every word, its niqqud, how it sounds (`ha-sa-PAR`, the stressed syllable in capitals) and where the reading
  came from: your own words, the dictionary, or automatic niqqud.
- Your corrections, kept for every future text.

## Plans
| | Free | Mivta Pro |
|---|---|---|
| Length | up to 150 words per run | any length |
| Dictionary | 20 starter words + your own (up to 10) | the shared, verified dictionary + your own (unlimited) |
| Prefixed forms of dictionary words (ה, ו, ב, ל, מ, ש, כש) | - | yes |
| Stress-marked copy of the text | - | yes |

Pro is the Mivta subscription: ₪39/month or ₪349/year, 7 days free with no card
(`python nq.py trial <email>`). Details: https://mivta.netlify.app/niqqud/

## Install
In Claude Code:
```
/plugin marketplace add itamarvanu-dot/mivta
/plugin install mivta-niqqud@mivta
```
Then ask Claude to "put niqqud on this text". The first time, Claude runs `skills/hebrew-niqqud/setup.sh`: a small
Python environment and the niqqud model (about 400 MB, CPU only).

## What the plugin downloads and sends
- Setup downloads Python packages from PyPI (pinned versions) and, from Hugging Face, the Phonikud
  niqqud model (pinned revision, checked against its SHA-256) and its tokenizer. After setup the free plan runs offline.
- Free plan: nothing else leaves your machine; your text never does.
- Mivta Pro: your licence key and one-way codes (salted SHA-256) of the words and 2-3 word runs of the text go to the
  Mivta server (mivta.netlify.app), which returns the dictionary readings it has for those words. The text itself is
  never sent. A trial sends the email address you give it. Details: [PRIVACY.md](PRIVACY.md).

## Licence
Source-available under the [PolyForm Strict License 1.0.0](LICENSE): free for personal, non-commercial use; no
changes, redistribution or reselling. Commercial use comes with a Mivta Pro subscription ([TERMS.md](TERMS.md)).
Third-party components keep their own licences: [NOTICE.md](NOTICE.md).
