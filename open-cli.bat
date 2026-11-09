@echo off
:: Double-click this file to open the Invoice Extractor in the terminal (CLI).
::
:: It reuses the virtual environment (.venv) created by install.bat.
:: Arguments are passed through to the CLI (e.g. open-cli.bat --image inv.png).
cd /d "%~dp0"

set "VENV=.venv"

if exist "%VENV%\Scripts\python.exe" (
    set "PYTHON=%VENV%\Scripts\python.exe"
) else if exist "%VENV%\Scripts\python3.exe" (
    set "PYTHON=%VENV%\Scripts\python3.exe"
) else if exist "%VENV%\bin\python" (
    set "PYTHON=%VENV%\bin\python"
) else (
    echo Python 3 was not found in this project's .venv.
    echo Run install.bat first to create the environment.
    pause
    exit /b 1
)

:: Run the CLI (pass through any arguments), then pause so the window stays open
:: after the extraction finishes.
"%PYTHON%" app.py
pause
