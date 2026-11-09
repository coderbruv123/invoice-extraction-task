@echo off
rem Create a virtual environment and install the invoice extractor (editable) for development.
rem Run ONCE, then double-click the installed app or run:  invoice-extract
rem
rem   Installer:  double-click install.bat   (or:  install.bat   from cmd)
rem   Clean run:  cmd /c install.bat
rem
rem No manual "pip install", "activate", or repeated commands needed.

echo ============================================================
echo   Invoice Extractor — Installer
echo ============================================================
echo.

rem Pick a Python interpreter (py launcher first, then python)
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PY=py -3"
) else (
    set "PY=python"
)

%PY% --version
if %errorlevel% neq 0 (
    echo.
    echo Error: Python 3.9+ was not found.
    echo Install it from https://www.python.org/downloads/ and check
    echo "Add Python to PATH" on the installer's last screen.
    pause
    exit /b 1
)

%PY% -m venv .venv
if %errorlevel% neq 0 (
    echo.
    echo Error: could not create the virtual environment (.venv).
    pause
    exit /b 1
)

call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo.
    echo Error: could not activate the virtual environment.
    pause
    exit /b 1
)

echo.
echo Upgrading pip inside the virtual environment...
python -m pip install --upgrade pip

echo.
echo Installing requirements and the invoice extractor (editable, with dev deps)...
pip install -r requirements.txt
pip install -e ".[dev]"

echo.
echo ============================================================
echo   Installation complete!
echo ============================================================
echo.
echo Run the extractor with:  invoice-extract
echo Run the tests with:      python -m unittest discover -s tests -v
echo.
echo Open the CLI in a terminal window by double-clicking:
echo   open-cli.bat
echo.
pause
