# Third-party notices

Mivta Niqqud installs and runs these components. Each keeps its own licence.

| Component | Use here | Licence |
|---|---|---|
| [Phonikud](https://github.com/thewh1teagle/phonikud) (G2P code) | how each word sounds, stress | CC BY 4.0 |
| [Phonikud ONNX model](https://huggingface.co/Phonikud/phonikud-onnx) | automatic niqqud | MIT |
| [phonikud-onnx](https://pypi.org/project/phonikud-onnx/) | runs the model | MIT |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | runs the model | MIT |
| [tokenizers](https://github.com/huggingface/tokenizers) | the model's tokenizer | Apache-2.0 |
| [DictaBERT char tokenizer](https://huggingface.co/dicta-il/dictabert-large-char-menaked) (`tokenizer.json`, included) | the model's tokenizer | CC BY 4.0 |

Attribution for Phonikud (CC BY 4.0): Phonikud G2P by thewh1teagle and contributors, https://github.com/thewh1teagle/phonikud
(paper: arXiv:2506.12311). Mivta Niqqud adds its own dictionaries and display rules on top of it.

Attribution for the DictaBERT char tokenizer (CC BY 4.0): `skills/hebrew-niqqud/data/dictabert-large-char-menaked.tokenizer.json`
is the unmodified `tokenizer.json` of dicta-il/dictabert-large-char-menaked by Dicta (revision 4dfc20b9),
https://huggingface.co/dicta-il/dictabert-large-char-menaked, licensed under https://creativecommons.org/licenses/by/4.0/.

The starter dictionary (`skills/hebrew-niqqud/data/he_lexicon_free.jsonl`) and the Mivta Pro shared dictionary were
verified by hand and in recordings; they are part of Mivta.
