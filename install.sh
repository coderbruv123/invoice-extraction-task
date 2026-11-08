# Create a virtual environment and install the invoice extractor (editable) for development.
# Usage:  bash install.sh    (Linux / macOS)
#         install.bat        (Windows)

set -euo pipefail

echo "Creating a virtual environment and installing the invoice extractor..."

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

echo
echo "Installed."
echo "Run the extractor with:  invoice-extract"
echo "Run the tests with:      python -m unittest discover -s tests -v"
