@echo off
:: Double-click this file to open the Invoice Extractor GUI.
::
:: It reuses the virtual environment (.venv) created by install.bat.
:: If the packages are missing (install.bat ran under a different shell, or was
:: interrupted), this launcher (re)installs them into the venv before launching
:: the app, so it never fails with "No module named pytesseract".
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

:: Make sure the venv has the Python packages (pytesseract, Pillow) before
:: launching. Returns 0 when the app is ready.
call :ensure_packages "%PYTHON%"

:: Verify the tesseract binary is available before launching the app.
:: pytesseract needs the tesseract binary on PATH (or at a known location).
set "TESS_BIN_DIR=C:\Program Files\Tesseract-OCR;C:\Program Files (x86)\Tesseract-OCR;C:\ProgramData\chocolatey\bin"
set "PATH=%PATH%;%TESS_BIN_DIR%"
where tesseract >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Tesseract OCR is not installed or not found in its usual locations.
    echo.
    echo Please run install.bat to install Tesseract OCR, then open this file again.
    echo.
    pause
    exit /b 1
)

:: Run the GUI (no command line needed). After the window is closed, pause so
:: the window stays open for the next run.
"%PYTHON%" invoice_extractor.py
pause
exit /b %errorlevel%

:: ---------------------------------------------------------------
:: ensure_packages <python_executable>
:: Installs requirements.txt and the editable app into the venv if
:: pytesseract / Pillow are missing. Returns 0 when the app is ready.
:: ---------------------------------------------------------------
:ensure_packages
setlocal
set "PY=%~1"
%PY% -c "import pytesseract, PIL" 2>nul
if %errorlevel% equ 0 (
    endlocal
    exit /b 0
)
echo.
echo Python packages missing in the venv. (Re)installing into %VENV%...
%PY% -m pip install --upgrade pip
%PY% -m pip install -r "%~dp0requirements.txt"
%PY% -m pip install -e "%~dp0.[dev]"
set "PIP_RC=%errorlevel%"
endlocal
exit /b %PIP_RC%
