# Privacy (draft, pending legal review)

Last updated: 2026-10-12

- **Your voice, scripts and audio** are processed where you run the plugin (your computer or your Claude
  environment). Mivta does not upload them.
- **Pro dictionary lookups:** when Pro is on, the plugin sends our server your licence key and one-way codes
  (salted SHA-256) of the individual words and 2-4 word runs in your script, so the server can return the
  pronunciations it has for those words. Sentences, audio and your voice are never sent. The server logs which
  codes each licence received (to trace a leaked copy of the dictionary), and keeps those logs for 90 days.
- **Licence checks:** the licence key and a random installation id (not your computer's name) go to Lemon Squeezy (our merchant of record) through
  our server.
- **Pro module:** with Pro or Studio, the plugin asks our server once a day whether its copy of the Mivta Pro module is
  current (it sends the licence key and the module version) and downloads a new copy when there is one. We log which
  licence received which copy.
- **Word contributions (optional):** if you choose to share a word, we receive the word, its niqqud and its phonetic
  transcription, plus a one-way code derived from your licence key so repeated contributions can be counted. Nothing
  else.
- **Trial:** we keep the email address you start a trial with, so each address gets one trial, and may write to you once
  when the trial ends. Ask us and we delete it.
- **Waitlist:** if you join the waitlist we keep your email address (and name, if given) only to tell you when
  payments open, in private storage. Ask us and we delete it.
- **Payments** are handled by Lemon Squeezy as merchant of record; we do not see your card details.
- **Contact** for privacy requests: mivta.ai@gmail.com
