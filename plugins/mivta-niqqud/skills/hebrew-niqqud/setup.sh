#!/usr/bin/env bash
# Mivta Niqqud one-time install: a small Python environment (CPU) + the Phonikud niqqud model. About 400 MB.
#   bash setup.sh            (HV_HOME defaults to ~/.mivta; the model is shared with Mivta voice when both are installed)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HV_HOME="${HV_HOME:-$HOME/.mivta}"
PY="${PYTHON:-python3}"
mkdir -p "$HV_HOME/models"
if [ ! -x "$HV_HOME/venv_nq/bin/python" ]; then
  echo "== niqqud environment"
  "$PY" -m venv "$HV_HOME/venv_nq"
  "$HV_HOME/venv_nq/bin/pip" install -q --no-cache-dir -r "$HERE/requirements.txt"
fi
if [ ! -s "$HV_HOME/models/phonikud-1.0.int8.onnx" ]; then
  echo "== niqqud model (Phonikud, MIT, ~300 MB)"
  curl -sSL -o "$HV_HOME/models/phonikud-1.0.int8.onnx" \
    https://huggingface.co/Phonikud/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
fi
HV_HOME="$HV_HOME" "$HV_HOME/venv_nq/bin/python" "$HERE/scripts/nq.py" doctor
