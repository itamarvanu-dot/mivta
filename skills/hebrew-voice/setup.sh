#!/usr/bin/env bash
# Mivta one-time install: two Python environments (CPU) + the niqqud model. About 4 GB of disk and 10-20 minutes.
# The voice engine's weights (~3 GB) download from Hugging Face on the first generate.
#   bash setup.sh            (HV_HOME defaults to ~/.mivta)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HV_HOME="${HV_HOME:-$HOME/.mivta}"
PY="${PYTHON:-python3}"
TORCH="torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu"
mkdir -p "$HV_HOME/models" "$HV_HOME/voices" "$HV_HOME/pro"

if [ ! -x "$HV_HOME/venv/bin/python" ]; then
  echo "== tools environment (niqqud, Hebrew speech recognition, phoneme check)"
  "$PY" -m venv "$HV_HOME/venv"
  "$HV_HOME/venv/bin/pip" install -q --no-cache-dir $TORCH
  "$HV_HOME/venv/bin/pip" install -q --no-cache-dir -r "$HERE/requirements-tools.txt"
fi
if [ ! -x "$HV_HOME/venv_cb/bin/python" ]; then
  echo "== voice engine environment (Chatterbox Multilingual, MIT)"
  "$PY" -m venv "$HV_HOME/venv_cb"
  "$HV_HOME/venv_cb/bin/pip" install -q --no-cache-dir $TORCH
  # exact versions tested together; --no-deps because chatterbox-tts declares a web UI (gradio) it does not need here
  "$HV_HOME/venv_cb/bin/pip" install -q --no-cache-dir --no-deps -r "$HERE/requirements-engine.txt"
fi
if [ ! -s "$HV_HOME/models/phonikud-1.0.int8.onnx" ]; then
  echo "== niqqud model (Phonikud, MIT)"
  curl -sSL -o "$HV_HOME/models/phonikud-1.0.int8.onnx" \
    https://huggingface.co/Phonikud/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
fi
HV_HOME="$HV_HOME" "$HV_HOME/venv/bin/python" "$HERE/scripts/hv.py" doctor
