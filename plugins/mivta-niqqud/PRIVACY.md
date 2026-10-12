# Mivta Niqqud privacy (draft, pending legal review)

Last updated: 2026-10-12

- **Your text** is processed where you run the plugin (your computer or your Claude environment). Mivta Niqqud does not
  upload it.
- **Setup** downloads Python packages from PyPI and the Phonikud niqqud model from Hugging Face; after that
  the free plan works offline.
- **Mivta Pro dictionary lookups:** with Pro, the plugin sends our server (mivta.netlify.app) your licence key and
  one-way codes (salted SHA-256) of the individual words and 2-3 word runs in your text, so the server can return the
  dictionary readings it has for those words. The text itself is never sent. The server logs which codes each licence
  received (to trace a leaked copy of the dictionary) and keeps those logs for 90 days.
- **Licence checks:** the licence key and a random installation id (not your computer's name) go to Lemon Squeezy (our merchant of record) through
  our server. The server logs each activation (a one-way code of the licence key, the plan and the time) and keeps
  that log for 90 days.
- **Server:** our server runs on Netlify. It uses your IP address only in memory, to limit how often requests can be
  made, and does not store it.
- **Trial:** we keep the email address you start a trial with, so each address gets one trial, and may write to you
  once when the trial ends. Ask us and we delete it.
- **Payments** are handled by Lemon Squeezy as merchant of record; we do not see your card details.
- **Age:** Mivta Niqqud is for people 18 and over, as Claude itself is, and we do not knowingly collect data from anyone
  younger. If you think a child gave us an email address, write to us and we will delete it.
- **Contact** for privacy requests: mivta.ai@gmail.com
