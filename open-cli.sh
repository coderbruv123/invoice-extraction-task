#!/usr/bin/env bash
# Double-click this file to open the Invoice Extractor in the terminal (CLI).
#
# It reuses the virtual environment (.venv) created by install.sh / install.command.
# Arguments are passed through to the CLI (e.g. ./open-cli.sh --image inv.png).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

VENV="${VENV:-.venv}"

PYTHON=""
if [ -x "${VENV}/bin/python" ]; then
    PYTHON="${VENV}/bin/python"
elif [ -x "${VENV}/Scripts/python.exe" ]; then
    PYTHON="${VENV}/Scripts/python.exe"
elif [ -x "${VENV}/bin/python3" ]; then
    PYTHON="${VENV}/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
fi

if [ -z "${PYTHON}" ] || [ ! -f "${PYTHON}" ]; then
    echo "Python 3 was not found in this project's .venv (${VENV})." >&2
    echo "Run ./install.sh first to create the environment." >&2
    exit 1
fi

# Run the CLI (pass through any arguments), then pause so the window stays open
# after the extraction finishes.
"${PYTHON}" app.py "$@"
read -r -p "Press Enter to close this window..." _ 2>/dev/null || true
