@echo off
:: Double-click this file to open the Invoice Extractor GUI.
::
:: It reuses the virtual environment (.venv) created by install.bat.
:: No command line needed — the GUI opens a window with file picker + Extract + Save.
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

:: Run the GUI (no command line needed). After the window is closed, pause so
:: the window stays open for the next run.
"%PYTHON%" invoice_extractor.py
pause
