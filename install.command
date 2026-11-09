#!/usr/bin/env bash
# macOS double-click version of install.sh.
# Right-click in Finder > Open  (first time) or just double-click.
# If your Mac asks "cannot be opened because it is from an unidentified developer",
# go to System Settings > Privacy & Security > Allow Anyway, then run it again.
#
# After it finishes, the app is installed and you can run `invoice-extract`.

echo "============================================"
echo "  Invoice Extractor — Installer"
echo "============================================"
echo

# Installing Tesseract OCR: pytesseract needs the tesseract *binary* on the
# system, not just the Python package.
install_tesseract() {
    if command -v tesseract >/dev/null 2>&1; then
        echo "Tesseract OCR already installed: $(tesseract --version | head -n 1)"
        return 0
    fi
    echo "Tesseract OCR not found. Installing it..."
    if command -v brew >/dev/null 2>&1; then
        brew install tesseract
    elif command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y tesseract
    elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y tesseract
    else
        echo "Could not detect a package manager. Please install Tesseract OCR manually:"
        echo "  macOS:    brew install tesseract"
        echo "  Ubuntu:   apt-get install -y tesseract-ocr"
        echo "  Fedora:   dnf install -y tesseract"
        return 1
    fi
}
PYTHON_BIN="${PYTHON_CMD:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: '$PYTHON_BIN' was not found in your PATH."
  echo "Install Python 3.9+ from https://www.python.org/downloads/ and try again."
  read -r -p "Press Enter to close this window..."
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
echo "Installing Tesseract OCR (the binary that pytesseract needs)..."
install_tesseract

echo
echo "============================================"
echo "  Installation complete!"
echo "============================================"
echo
echo "Run the extractor with:  invoice-extract"
echo "Run the tests with:      python -m unittest discover -s tests -v"
echo
echo "Open the CLI in a terminal window by double-clicking:"
echo "  open-cli.command (macOS)"
echo
read -r -p "Press Enter to close this window..."
