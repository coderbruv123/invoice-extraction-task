#!/usr/bin/env bash
# Create a virtual environment and install the invoice extractor (editable) for development.
# Run ONCE, then double-click the installed app or run:  invoice-extract
#
#   bash install.sh          (Linux / macOS / Git Bash on Windows)
#   ./install.sh             (after:  chmod +x install.sh)
#   OR  just "bash install.sh"
#
# No manual "pip install", "source venv", or repeated commands needed.
set -euo pipefail

echo "============================================"
echo "  Invoice Extractor — Installer"
echo "============================================"
echo

# Prefer python3 for creating the venv (python may not exist on some systems)
PYTHON_BIN="${PYTHON_CMD:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: '$PYTHON_BIN' was not found in your PATH."
  echo "Install Python 3.9+ from https://www.python.org/downloads/ and try again."
  exit 1
fi

echo "Creating a virtual environment in .venv (first time only)..."
"$PYTHON_BIN" -m venv .venv

# Activate the venv (applies to the rest of this script)
# shellcheck source=/dev/null
source .venv/bin/activate

echo
echo "Upgrading pip inside the virtual environment..."
pip install --upgrade pip

echo
echo "Installing requirements and the invoice extractor (editable, with dev deps)..."
pip install -r requirements.txt
pip install -e ".[dev]"

echo
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo
echo "Run the extractor with:  invoice-extract"
echo "Run the tests with:      python -m unittest discover -s tests -v"
echo
echo "Open the CLI in a terminal window by double-clicking:"
echo "  macOS:  open-cli.command"
echo "  Linux:  open-cli.sh"
echo "  Windows: open-cli.bat"
echo
read -r -p "Press Enter to close this window..."
