#!/usr/bin/env bash
# Mivta Niqqud one-time install: a small Python environment (CPU) and the Phonikud niqqud model, about 400 MB in all.
#   bash setup.sh            (HV_HOME defaults to ~/.mivta; the model is shared with Mivta voice when both are installed)
# The Python packages come from PyPI (versions pinned in requirements.txt, prebuilt wheels preferred). nq.py then fetches the
# model from Hugging Face at a pinned revision and keeps it only if its SHA-256 matches.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
HV_HOME="${HV_HOME:-$HOME/.mivta}"
PY="${PYTHON:-python3}"
mkdir -p "$HV_HOME/models"
[ -x "$HV_HOME/venv_nq/bin/python" ] || "$PY" -m venv "$HV_HOME/venv_nq"
if ! "$HV_HOME/venv_nq/bin/python" -c "import phonikud, phonikud_onnx" 2>/dev/null; then   # also finishes an interrupted install
  echo "== niqqud environment"
  "$HV_HOME/venv_nq/bin/pip" install -q --no-cache-dir --prefer-binary -r "$HERE/requirements.txt"
fi
HV_HOME="$HV_HOME" "$HV_HOME/venv_nq/bin/python" "$HERE/scripts/nq.py" setup
