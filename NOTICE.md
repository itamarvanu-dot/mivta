# Third-party notices

Mivta installs and runs these components. Each keeps its own licence.

| Component | Use here | Licence |
|---|---|---|
| [Chatterbox Multilingual](https://huggingface.co/ResembleAI/chatterbox) by Resemble AI | the voice engine | MIT |
| [Phonikud](https://github.com/thewh1teagle/phonikud) (G2P code) | niqqud, stress and IPA | CC BY 4.0 |
| [Phonikud ONNX model](https://huggingface.co/Phonikud/phonikud-onnx) | niqqud model | MIT |
| [ivrit-ai Whisper large-v3-turbo (CTranslate2)](https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ct2) | Hebrew transcription in QA | Apache-2.0 |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | runs the transcription model | MIT |
| [wav2vec2-lv-60-espeak-cv-ft](https://huggingface.co/facebook/wav2vec2-lv-60-espeak-cv-ft) by Meta | phoneme check in QA | Apache-2.0 |
| [Perth](https://github.com/resemble-ai/Perth) watermark by Resemble AI | marks every output as AI-generated | MIT |

Attribution for Phonikud (CC BY 4.0): Phonikud G2P by thewh1teagle and contributors, https://github.com/thewh1teagle/phonikud
(paper: arXiv:2506.12311). Mivta adds its own dictionary and prefix rules on top of it.

The dictionaries (`data/he_lexicon_free.jsonl` and the Pro shared dictionary) were verified by hand and by
recording tests; they are part of Mivta.
