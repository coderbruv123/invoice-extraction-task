#!/usr/bin/env bash
# Double-click this file on macOS to open the Invoice Extractor GUI.
#
# It reuses the virtual environment (.venv) created by install.command / install.sh.
# No command line needed — the GUI opens a window with file picker + Extract + Save.
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
    echo "Run ./install.command first to create the environment." >&2
    exit 1
fi

# Run the GUI (no command line needed). After the window is closed, pause so
# the terminal window stays open for the next run.
"${PYTHON}" invoice_extractor.py
read -r -p "Press Enter to close this window..." _ 2>/dev/null || true
