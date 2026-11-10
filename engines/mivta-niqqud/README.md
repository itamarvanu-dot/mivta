# Mivta Niqqud engine

The Python engine behind the [Mivta Niqqud](../../plugins/mivta-niqqud) Claude plugin: exact niqqud and stress for
Hebrew text. The plugin itself contains only its instructions (`SKILL.md`); this package is what it installs and runs.

```
python3 -m venv ~/.mivta/venv_nq
~/.mivta/venv_nq/bin/pip install --prefer-binary "mivta-niqqud @ git+https://github.com/itamarvanu-dot/mivta@<commit>#subdirectory=engines/mivta-niqqud"
~/.mivta/venv_nq/bin/mivta-niqqud setup     # fetches the Phonikud model (pinned revision, SHA-256 checked)
~/.mivta/venv_nq/bin/mivta-niqqud text "שלום עולם"
```

Licence: PolyForm Strict 1.0.0 (LICENSE) + the plugin's TERMS.md. Third-party notices: NOTICE.md.
