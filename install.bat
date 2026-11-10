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
:: Install it if missing, then confirm it is visible on PATH.
where tesseract >nul 2>&1
if errorlevel 1 (
    call :install_tesseract
    if %errorlevel% neq 0 (
        echo.
        echo Error: could not install Tesseract OCR automatically.
        echo Try one of these instead:
        echo   winget install UB-Mannheim.TesseractOCR
        echo   choco install tesseract-ocr -y
        echo   https://github.com/UB-Mannheim/tesseract/wiki
        pause
        exit /b 1
    )
    echo Tesseract install command finished. If it was just installed, open a new
    echo terminal (or run refreshenv) before continuing; then re-run this installer
    echo to confirm Tesseract is visible on PATH.
) else (
    echo Tesseract OCR is already installed.
)

echo.
echo ============================================================
echo   Installation complete!
echo ============================================================
echo.
echo Run the extractor with:  invoice-extract
echo Run the tests with:      python -m unittest discover -s tests -v
echo.
:: ---------------------------------------------------------------------------
:install_tesseract
:: Install the tesseract binary. Prefers winget, then Chocolatey, then the
:: UB-Mannheim silent NSIS installer. Returns 0 on success, 1 on failure.
where winget >nul 2>&1
if errorlevel 1 (
    where choco >nul 2>&1
    if errorlevel 1 (
        rem No package manager found: download the official silent installer.
        echo.
        echo No package manager found (winget or Chocolatey). Downloading the
        echo UB-Mannheim silent NSIS installer (first time only)...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://github.com/UB-Mannheim/tesseract/wiki/files/installer/tesseract-ocr-w64-setup-5.4.0.20240606.exe' -OutFile '%TEMP%\tesseract-install.exe'"
        if %errorlevel% neq 0 (
            echo.
            echo Download failed. Install manually from:
            echo   https://github.com/UB-Mannheim/tesseract/wiki
            exit /b 1
        )
        "%TEMP%\tesseract-install.exe" /S
        if %errorlevel% neq 0 (
            echo.
            echo Silent installer failed (error %errorlevel%). Try running manually:
            echo   "%TEMP%\tesseract-install.exe" /S
            exit /b 1
        )
        exit /b 0
    ) else (
        echo Installing Tesseract OCR via Chocolatey...
        choco install tesseract-ocr -y
        if %errorlevel% neq 0 (
            echo.
            echo Chocolatey install failed (error %errorlevel%). Try running manually:
            echo   choco install tesseract-ocr -y
            exit /b 1
        )
        exit /b 0
    )
) else (
    echo Installing Tesseract OCR via winget...
    winget install --id UB-Mannheim.TesseractOCR
    if %errorlevel% neq 0 (
        echo.
        echo winget install failed (error %errorlevel%). Try running manually:
        echo   winget install UB-Mannheim.TesseractOCR
        exit /b 1
    )
    exit /b 0
)

echo Open the CLI in a terminal window by double-clicking:
echo   open-cli.bat
echo.
pause
