@echo off
rem Create a virtual environment and install the invoice extractor (editable) for development.
rem Usage:  install.bat

echo Creating a virtual environment and installing the invoice extractor...

python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"

echo.
echo Installed.
echo Run the extractor with:  invoice-extract
echo Run the tests with:      python -m unittest discover -s tests -v
