# Invoice Data Extraction

A small Python application that reads a supplied invoice image, extracts the key
information using an AI tool (Tesseract OCR), and outputs the information in
structured JSON format. It also validates the extracted amounts (subtotal vs.
items, VAT, and grand total) and handles missing data / errors gracefully.

## Task context

This is a sample solution for the *AI-Powered Invoice Data Extraction* job-task
brief (RIVERTECH SUPPLIES LTD.). The original brief asks for:

- A small Python application that reads the attached invoice image and extracts:
  - Invoice number
  - Invoice date
  - Supplier name
  - Items (description, quantity, unit price)
  - Total amount
- Output in structured JSON
- Basic validation (e.g. check if total amount matches the item amounts)
- Graceful handling of missing information or errors

## Run it

There are two ways to run the app — a graphical user interface (GUI) and a
command line (CLI). Install it **once**, then run it either by double-clicking a
file or by typing a command.

### Option A — GUI (recommended, no command line)

After installing, double-click the app for your operating system:

| OS | Double-click this file |
|----|------------------------|
| macOS | `open-gui.command` |
| Linux / git-bash | `open-gui.sh` |
| Windows | `open-gui.bat` |

The GUI opens a window with a **Select Invoice Image...** button, an **Extract
Invoice** button and a **Save JSON...** button. It also auto-detects the
invoice image shipped in the job email (if it's inside your `Downloads`
folder), so the **Extract** button is already enabled. Pick an image, click
**Extract**, then **Save JSON...**.

### Option B — Command line (CLI)

After installing, double-click the CLI app for your operating system:

| OS | Double-click this file |
|----|------------------------|
| macOS | `open-cli.command` |
| Linux / git-bash | `open-cli.sh` |
| Windows | `open-cli.bat` |

This runs `python app.py` in a terminal window. Use arguments to pick the
input and output files, for example:

```bash
open-cli.command --image path/to/invoice.png --output path/to/invoice.json
```

## Install from GitHub (easiest — run once)

Clone the repo, then run the installer **once**:

```bash
git clone <your-repo-url> invoice-extractor
cd invoice-extractor
bash install.sh        # Linux / macOS / Git Bash on Windows
```

or on Windows double-click `install.bat` in File Explorer.

That installer does everything for you:
1. creates a clean **virtual environment** (`.venv`),
2. **installs the Python requirements** (`pytesseract` + `Pillow`),
3. **installs your app** (`pip install -e .[dev]`), which also registers the `invoice-extract` command,
4. **installs the tesseract OCR engine** on your system — the binary that `pytesseract` needs (via your OS package manager).

You only run the installer **once**. After that, run the app any time with
either the double-click files above or the commands below — you never need to
`pip install` or `source .venv` again.

### Missing the tesseract binary?

If OCR fails with "Tesseract OCR is not installed", install the binary with:

| OS | Command |
|----|---------|
| macOS | `brew install tesseract` |
| Ubuntu / Debian | `sudo apt-get install -y tesseract-ocr` |
| Fedora | `sudo dnf install -y tesseract` |
| Windows | `winget install UB-Mannheim.TesseractOCR` |

The installer runs the matching install automatically; this table covers the
case where it could not detect a package manager.

**Command line after install:**

```bash
invoice-extract            # CLI, opens the default invoice image
invoice-extract --image path/to/invoice.png --output outputs/invoice.json
```

**Run the tests:**

```bash
python -m unittest discover -s tests -v
```

## Project layout

```
invoice-extraction-task/
├── app.py                  # CLI version (OCR, parsing, validation, JSON output)
├── invoice_extractor.py    # GUI version (no command line needed)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── outputs/                # Generated JSON
```

## How the AI tool is used

The app uses **Tesseract OCR** (`pytesseract`), an open-source, ML-based optical
character recognition engine, to extract the text from the invoice image. The
extracted text is then parsed into structured fields and validated before being
written to JSON.

## Submission

- Attach the generated `outputs/invoice.json` (and `app.py` + `requirements.txt`)
  to your email submission, or share a link to this repository.
- Include a short README (like this one) with instructions on how to run the
  application.

## Notes on the extraction

- The invoice is a computer-generated document; the parser expects the standard
  layout used by the provided invoice (header block, item table, totals block).
- OCR is not 100% perfect on handwritten or low-quality scans. Minor layout
  variations may produce `None` fields that are reported as `null` rather than
  crashing.
- Missing/erroneous values are surfaced via the `validation` dict (all `true`/`false`)
  so the user can decide whether to retry or flag the extraction.
