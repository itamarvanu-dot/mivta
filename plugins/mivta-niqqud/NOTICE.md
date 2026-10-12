# Third-party notices

Mivta Niqqud installs and runs these components. Each keeps its own licence.

| Component | Use here | Licence |
|---|---|---|
| [Phonikud](https://github.com/thewh1teagle/phonikud) (G2P code) | how each word sounds, stress | CC BY 4.0 |
| [Phonikud ONNX model](https://huggingface.co/Phonikud/phonikud-onnx) | automatic niqqud | MIT |
| [phonikud-onnx](https://pypi.org/project/phonikud-onnx/) | runs the model | MIT |
| [ONNX Runtime](https://github.com/microsoft/onnxruntime) | runs the model | MIT |
| [tokenizers](https://github.com/huggingface/tokenizers) | the model's tokenizer | Apache-2.0 |

Attribution for Phonikud (CC BY 4.0): Phonikud G2P by thewh1teagle and contributors, https://github.com/thewh1teagle/phonikud
(paper: arXiv:2506.12311). Mivta Niqqud adds its own dictionaries and display rules on top of it.

The starter dictionary (`skills/hebrew-niqqud/data/he_lexicon_free.jsonl`) and the Mivta Pro shared dictionary were
verified by hand and in recordings; they are part of Mivta.
