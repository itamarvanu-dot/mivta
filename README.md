# Mivta (מבטא)

Hebrew that reads right. Two Claude plugins:

| Plugin | What it does |
|---|---|
| [**mivta**](plugins/mivta) | Clones your own voice and narrates Hebrew with exact pronunciation: a word-by-word review before every recording and an automatic check of every take. |
| [**mivta-niqqud**](plugins/mivta-niqqud) | Adds exact niqqud and stress to any Hebrew text, with a table of how each word sounds and the words to check. |

Website: https://mivta.netlify.app · Support: mivta.ai@gmail.com

## Install
In Claude Code:
```
/plugin marketplace add itamarvanu-dot/mivta
/plugin install mivta@mivta
/plugin install mivta-niqqud@mivta
```
In Cowork (the Claude app): **Customize > Plugins > Add > Add marketplace**, enter `itamarvanu-dot/mivta`, then
install the plugin you want.

**Other agents** that read the open Agent Skills format (SKILL.md), such as OpenAI's Codex CLI, Gemini CLI or Cursor:
copy the plugin's `skills/<name>` folder into the agent's skills folder (for Codex CLI: `~/.agents/skills/`), then ask
the agent to set it up.

## Licence
Source-available under the PolyForm Strict License 1.0.0 (see each plugin's LICENSE and TERMS.md). Commercial use comes
with a Mivta Pro or Studio subscription.
