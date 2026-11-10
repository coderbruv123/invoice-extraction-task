"""Helpers for locating the Tesseract OCR executable."""

import os
import shutil
from pathlib import Path

import pytesseract


def configure_tesseract():
    """Configure pytesseract to use an installed executable, including Windows defaults."""
    executable = shutil.which("tesseract")
    if executable is None and os.name == "nt":
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "Tesseract-OCR"
            / "tesseract.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
            / "Tesseract-OCR"
            / "tesseract.exe",
            Path(os.environ.get("ChocolateyInstall", r"C:\ProgramData\chocolatey"))
            / "bin"
            / "tesseract.exe",
        ]
        executable = next((str(path) for path in candidates if path.is_file()), None)

    if executable is not None:
        pytesseract.pytesseract.tesseract_cmd = executable
    return executable
