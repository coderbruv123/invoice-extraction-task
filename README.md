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

### Option A — GUI (recommended, no command line)
The GUI opens a window with a file picker, an **Extract** button, and a **Save JSON** button.

```bash
python -m pip install -r requirements.txt
python invoice_extractor.py
```

The app auto-detects the invoice image if it's in your `Downloads` folder.
If you have a different image, click **Select Invoice Image...** first.

### Option B — Command line
```bash
python app.py --image path/to/invoice.png --output path/to/invoice.json
```
By default the CLI reads the invoice image shipped in the email at
`/home/dante/Downloads/AI-Powered Invoice Extraction Task.png` and writes
`outputs/invoice.json` next to the script.

## Install from GitHub

Clone the repo and install it as an editable package (this also installs the CLI
entry point so you can run the app from anywhere):

```bash
git clone <your-repo-url> invoice-extractor
cd invoice-extractor
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e ".[dev]"
```

Then run the app in either mode:

```bash
# GUI (recommended)
invoice-extract

# Command line
invoice-extract --image path/to/invoice.png --output outputs/invoice.json
```

With the editable install (`-e`), the command-line entry point `invoice-extract`
is created, pointing at `app:main`. Development dependencies (test runner) are
installed via the `[dev]` extra. Run the test suite with:

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
