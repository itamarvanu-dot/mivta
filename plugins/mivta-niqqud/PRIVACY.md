# Mivta Niqqud privacy (draft, pending legal review)

Last updated: 2026-10-12

- **Your text** is processed where you run the plugin (your computer or your Claude environment). Mivta Niqqud does not
  upload it.
- **Setup** downloads Python packages from PyPI and the Phonikud niqqud model and tokenizer from Hugging Face.
- **Mivta Pro dictionary lookups:** with Pro, the plugin sends our server (mivta.netlify.app) your licence key and
  one-way codes (salted SHA-256) of the individual words and 2-3 word runs in your text, so the server can return the
  dictionary readings it has for those words. The text itself is never sent. The server logs which codes each licence
  received (to trace a leaked copy of the dictionary) and keeps those logs for 90 days.
- **Licence checks:** the licence key and an installation name go to Lemon Squeezy (our merchant of record) through
  our server.
- **Trial:** we keep the email address you start a trial with, so each address gets one trial, and may write to you
  once when the trial ends. Ask us and we delete it.
- **Payments** are handled by Lemon Squeezy as merchant of record; we do not see your card details.
- **Contact** for privacy requests: mivta.ai@gmail.com
