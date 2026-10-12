# Mivta (מבטא)

**Your own voice, reading Hebrew right.** Mivta is a Claude plugin that clones your voice and narrates Hebrew with
correct niqqud and stress: a verified dictionary, a word-by-word review before every recording, and an automatic
check of every take. It runs on a free, commercially licensed engine (Chatterbox Multilingual, MIT) on your own machine.

**הקול שלך, בעברית מדויקת.** פלאגין ל-Claude שמשבט את הקול שלכם ומקריא עברית עם ניקוד והטעמה נכונים: מילון מאומת,
סקירת מילה-מילה לפני כל הקלטה, ובדיקה אוטומטית של כל משפט.

Website: https://mivta.netlify.app · Support: mivta.ai@gmail.com · Security reports: [SECURITY.md](https://github.com/itamarvanu-dot/mivta/blob/main/SECURITY.md)

## Why
Hebrew is written without vowels, so voice engines guess. Chatterbox's own Hebrew step fails silently and the text
goes in with no niqqud; an [independent test](https://bintechai.com/learn/ai-voice) measured 65% of words wrong.
Automatic niqqud alone is not enough either: in "הספר סיפר לי שהספר נמכר בשמונה עשר שקלים" it reads the barber
(הַסַּפָּר) as the book (הַסֵּפֶר). Mivta shows you every word before recording and fixes it from a verified dictionary.

| Same voice, same sentence | What was said |
|---|---|
| Chatterbox alone | "פה הוסיפו לי שסטר נוחר בשמונה אר השקלים" (as transcribed) |
| + automatic niqqud | הַסֵּפֶר סִיפֵּר לִי... (the book told me) |
| + Mivta | הַסַּפָּר סִיפֵּר לִי שֶׁהַסֵּפֶר נִמְכַּר בִּשְׁמוֹנָה עָשָׂר שְׁקָלִים |

## Plans
| | Free | Pro | Studio |
|---|---|---|---|
| Voice | one voice, cloned from one 10 s clip | a profile built from minutes of your speech | up to 5 voices |
| Takes per line | 1 | 3-5, best one picked automatically | 3-5 |
| Automatic check of every word | - | transcription, sounds, stress | yes |
| Dictionary | 20 starter words | the shared verified dictionary + prefix engine | yes |
| Your own words | 10 | unlimited, and you can share them | unlimited |
| Script length | 10 lines | unlimited | unlimited, plus long-form split |
| Export | - | - | narration.wav (-16 LUFS) + subtitles (.srt) |
| Use | personal, non-commercial | commercial | commercial, client work |
| Price | free | ₪39/month or ₪349/year | ₪149/month or ₪1,490/year |

Pro free for 7 days, no card: ask Claude to "start my Mivta trial" (`python hv.py trial <email>`).

## Install
In Claude Code:
```
/plugin marketplace add itamarvanu-dot/mivta
/plugin install mivta@mivta
```
In Cowork (the Claude app): **Customize > Plugins > Add > Add marketplace**, enter `itamarvanu-dot/mivta`, then install Mivta.

Then ask Claude to "set up Mivta": it runs `skills/hebrew-voice/setup.sh` (about 4 GB, CPU only, 8 GB of memory).

## Use
Ask Claude in plain words, for example: "clone my voice from this recording and read this script in Hebrew".
Claude follows `skills/hebrew-voice/SKILL.md`: consent, your voice, the word-by-word review, recording, checks.

## What is in this repository, and what is not
This repository is the free plugin: Claude's instructions, the installer, the Hebrew reading layer, the starter
dictionary and the recording command. **Pro and Studio features (the automatic check of every take, the voice
profile, the prefix engine over the shared dictionary, the Studio tools) are the Mivta Pro module**, which the Mivta
server sends to an active licence or trial. It is Python source, runs only on your machine, and is personalised for
your licence.

## What the plugin sends, and where
- Free: nothing leaves your machine except model downloads from Hugging Face during setup.
- Pro and Studio:
  - your licence key and one-way codes of the words in your script go to the Mivta server (mivta.netlify.app, hosted on Netlify),
    which returns pronunciations for those words;
  - once a day the plugin checks with the server that its Pro module is current, and downloads a new one when there is;
  - licence checks go through the server to Lemon Squeezy.
  
  Never sentences, audio or your voice. Details: [PRIVACY.md](PRIVACY.md).

## Responsible use
Clone only your own voice or a voice whose owner gave written permission. Every output carries an inaudible Perth
watermark that identifies it as AI-generated. See [TERMS.md](TERMS.md).

## Licence
Source-available under the [PolyForm Strict License 1.0.0](LICENSE): free for personal, non-commercial use; no
changes, redistribution or reselling. Commercial use comes with a Pro or Studio subscription. Third-party components
keep their own licences: see [NOTICE.md](NOTICE.md).
