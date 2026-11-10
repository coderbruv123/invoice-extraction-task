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

%PY% -m venv "%~dp0.venv"
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
echo Installing Tesseract OCR (the binary that pytesseract needs)...

:: Tesseract is a system binary; the Python package (pytesseract) only wraps it.
:: Find it on PATH or in its common installation locations.
call :find_tesseract
if not defined TESSERACT_EXE (
    echo Tesseract was not found. Installing the UB-Mannheim OCR engine...
    call :install_tesseract
    if errorlevel 1 goto :tesseract_install_failed
    call :find_tesseract
)
if not defined TESSERACT_EXE goto :tesseract_not_found

:: Add its actual directory to this session and verify the executable itself.
for %%I in ("%TESSERACT_EXE%") do set "TESS_BIN_DIR=%%~dpI"
set "PATH=%TESS_BIN_DIR%;%PATH%"
"%TESSERACT_EXE%" --version >nul 2>&1
if errorlevel 1 goto :tesseract_not_usable
echo Tesseract OCR is ready: "%TESSERACT_EXE%"

echo.
echo ============================================================
echo   Installation complete!
echo ============================================================
echo.
echo Run the extractor with:  invoice-extract
echo Run the tests with:      python -m unittest discover -s tests -v
echo.
pause
exit /b 0

:tesseract_install_failed
echo.
echo Error: could not install Tesseract OCR automatically.
echo Try one of these instead:
echo   winget install UB-Mannheim.TesseractOCR
echo   choco install tesseract-ocr -y
echo   https://github.com/UB-Mannheim/tesseract/wiki
pause
exit /b 1

:tesseract_not_found
echo.
echo Error: Tesseract installation completed, but tesseract.exe was not found.
echo Install it from https://github.com/UB-Mannheim/tesseract/wiki
pause
exit /b 1

:tesseract_not_usable
echo.
echo Error: Tesseract was found at "%TESSERACT_EXE%" but could not run.
pause
exit /b 1

:: ---------------------------------------------------------------------------
:find_tesseract
set "TESSERACT_EXE="
for /f "delims=" %%T in ('where tesseract 2^>nul') do if not defined TESSERACT_EXE set "TESSERACT_EXE=%%~fT"
if not defined TESSERACT_EXE if exist "%ProgramFiles%\Tesseract-OCR\tesseract.exe" set "TESSERACT_EXE=%ProgramFiles%\Tesseract-OCR\tesseract.exe"
if not defined TESSERACT_EXE if exist "%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe" set "TESSERACT_EXE=%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe"
if not defined TESSERACT_EXE if exist "%ChocolateyInstall%\bin\tesseract.exe" set "TESSERACT_EXE=%ChocolateyInstall%\bin\tesseract.exe"
if not defined TESSERACT_EXE if exist "%ProgramData%\chocolatey\bin\tesseract.exe" set "TESSERACT_EXE=%ProgramData%\chocolatey\bin\tesseract.exe"
exit /b 0

::
:install_tesseract
:: Install the tesseract binary. Prefers winget, then Chocolatey, then the
:: UB-Mannheim silent NSIS installer. Returns 0 on success, 1 on failure.
where winget >nul 2>&1
if not errorlevel 1 goto :install_with_winget
where choco >nul 2>&1
if not errorlevel 1 goto :install_with_choco

rem No package manager found: download the official silent NSIS installer.
echo.
echo No package manager found (winget or Chocolatey). Downloading the
echo UB-Mannheim silent NSIS installer (first time only)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://github.com/UB-Mannheim/tesseract/wiki/files/installer/tesseract-ocr-w64-setup-5.4.0.20240606.exe' -OutFile '%TEMP%\tesseract-install.exe'"
if errorlevel 1 exit /b 1
"%TEMP%\tesseract-install.exe" /S
if errorlevel 1 exit /b 1
exit /b 0

:install_with_choco
echo Installing Tesseract OCR via Chocolatey...
choco install tesseract-ocr -y
if errorlevel 1 exit /b 1
exit /b 0

:install_with_winget
echo Installing Tesseract OCR via winget...
winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
if errorlevel 1 exit /b 1
exit /b 0
