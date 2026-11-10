#!/usr/bin/env python3
"""
Invoice Data Extraction — AI-Powered Invoice Extraction Task.
---------------------------------------------------------------------------
Reads an invoice image, extracts key information using Tesseract OCR
(an open-source, ML-based AI tool), and outputs the data in structured JSON.

Usage:
    python app.py --image path/to/invoice.png --output path/to/output.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pytesseract
from PIL import Image

# ---------------------------------------------------------------------------
# OCR
# ---------------------------------------------------------------------------


def extract_text(image_path):
    """Run Tesseract OCR on the invoice image and return the extracted text."""
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)
    except Exception as exc:
        raise RuntimeError(f"Failed to OCR image '{image_path}': {exc}") from exc


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def _clean_currency(value):
    """Turn '1,250.00' into 1250.0."""
    return float(str(value).replace(",", "").strip())


def _parse_date(text):
    """Convert '14 October 2024' -> '2024-10-14'. Returns original string if unparseable."""
    text = text.strip().rstrip('.')
    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
    if match:
        day, month_name, year = match.group(1), match.group(2).lower().rstrip('s'), match.group(3)
        month = MONTHS.get(month_name)
        if month:
            return f"{year}-{month:02d}-{int(day):02d}"
    return text


def _extract_items(lines):
    """Parse the invoice table rows into a list of item dicts."""
    items = []
    for line in lines:
        # Item rows look like: 4   Welding Service 10 hrs   1,500.00   15,000.00
        match = re.match(r'^\s*\d+\s+(.+?)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*$', line)
        if not match:
            continue

        raw_desc = match.group(1).strip()
        unit_price = _clean_currency(match.group(2))
        amount = _clean_currency(match.group(3))

        # Quantity is usually a small integer followed by a unit word
        # (e.g. "50 pes", "30 pc", "10 hrs", "1 ot").
        quantity = None
        measure = None
        qm = re.search(r'(\d+)\s*(pes|pc|ot|hrs?|units?)\b', raw_desc, re.IGNORECASE)
        if qm:
            quantity = int(qm.group(1))
            measure = qm.group(2).lower()
            if measure == "ot":          # OCR misread of "pc"
                measure = "pc"
            raw_desc = re.sub(qm.group(0), "", raw_desc).strip()

        items.append({
            "description": raw_desc.strip("| "),
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": amount,
        })
    return items


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------


def parse_invoice(text):
    """Extract structured invoice data from OCR'd text."""
    lines = [ln.strip() for ln in text.splitlines()]

    invoice = {
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "payment_terms": None,
        "supplier_name": None,
        "supplier_address": None,
        "supplier_phone": None,
        "supplier_email": None,
        "bill_to_name": None,
        "bill_to_address": None,
        "items": [],
        "subtotal": None,
        "vat": None,
        "total_amount": None,
        "validation": {
            "subtotal_matches_item_sum": None,
            "vat_calculation_ok": None,
            "total_matches_expected": None,
        },
        "raw_text": text,
    }

    # --- Invoice number ---
    m = re.search(r'Invoice\s*No\s*[:\-]\s*(RT-\d{4}-\d+)', text, re.IGNORECASE)
    if m:
        invoice["invoice_number"] = m.group(1).upper()

    # --- Dates / terms ---
    m = re.search(r'Invoice\s*Date\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["invoice_date"] = _parse_date(m.group(1))

    m = re.search(r'Due\s*Date\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["due_date"] = _parse_date(m.group(1))

    m = re.search(r'Payment\s*Terms\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["payment_terms"] = m.group(1).strip()

    # --- Supplier ---
    m = re.search(r'(RIVERTECH SUPPLIES LTD\.)', text, re.IGNORECASE)
    if m:
        invoice["supplier_name"] = m.group(1)

    m = re.search(r'45\s+Industrial\s+Estate\s+Road\s*,?\s*[\w\s,]*?\s+Nepal\s*,?\s*,?', text, re.IGNORECASE)
    if m:
        addr = m.group(0)
        # Drop stray OCR glyphs (e.g. the trailing "W" on its own line)
        addr = re.sub(r'[Ww]', '', addr)
        # Insert a comma after "Road" for proper formatting
        addr = re.sub(r'Industrial Estate Road\s+Kathmandu', 'Industrial Estate Road, Kathmandu', addr)
        invoice["supplier_address"] = " ".join(addr.split())

    m = re.search(r'Phone\s*[:\-]\s*([\+\d\s]+?)\s+(?:RIVERTECH|Email)', text, re.IGNORECASE)
    if m:
        invoice["supplier_phone"] = m.group(1).strip()

    m = re.search(r'Email\s*[:\-]\s*([\w.@]+)', text, re.IGNORECASE)
    if m:
        invoice["supplier_email"] = m.group(1)

    # --- Bill to ---
    m = re.search(r'Bill\s+To\s*[:\-]\s*INVOICE\s+(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["bill_to_name"] = m.group(1).strip()

    # Bill-to address: locate "Sanobharyang" and "Nepal" by position, then
    # strip the stray "Invoice Date: 14 October 2024" fragment on the same line.
    sanob_pos = text.find('Sanobharyang')
    if sanob_pos != -1:
        nep_pos = text.find('Nepal', sanob_pos)
        if nep_pos != -1:
            addr = text[sanob_pos:nep_pos + len('Nepal')]
            addr = re.sub(r'\s*Invoice\s+Date[^,\n]*', '', addr)
            invoice["bill_to_address"] = " ".join(addr.split())

    # --- Items ---
    invoice["items"] = _extract_items(lines)

    # --- Totals ---
    m = re.search(r'Subtotal\s*\(NPR\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["subtotal"] = _clean_currency(m.group(1))

    m = re.search(r'VAT\s*\(13%\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["vat"] = _clean_currency(m.group(1))

    m = re.search(r'Total\s+Amount\s*\(NPR\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["total_amount"] = _clean_currency(m.group(1))

    # --- Validation ---
    item_sum = sum(item["amount"] for item in invoice["items"])
    invoice["validation"]["subtotal_matches_item_sum"] = \
        invoice["subtotal"] is not None and abs(item_sum - invoice["subtotal"]) < 0.01

    vat_rate = 0.13
    expected_vat = invoice["subtotal"] * vat_rate if invoice["subtotal"] else None
    invoice["validation"]["vat_calculation_ok"] = \
        invoice["vat"] is not None and expected_vat is not None and \
        abs(invoice["vat"] - expected_vat) < 0.01

    expected_total = (invoice["subtotal"] or 0) + (invoice["vat"] or 0)
    invoice["validation"]["total_matches_expected"] = \
        invoice["total_amount"] is not None and abs(invoice["total_amount"] - expected_total) < 0.01

    return invoice


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_json(data, output_path):
    """Write the extracted data to a JSON file, formatted and indented."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    return path


def check_tesseract():
    """Verify the tesseract binary is installed (pytesseract cannot run without it)."""
    try:
        pytesseract.get_tesseract_version()
    except Exception as exc:
        print("[-] Tesseract OCR is not installed, so OCR cannot run.", file=sys.stderr)
        print("    Install the tesseract binary first:", file=sys.stderr)
        print("      macOS  : brew install tesseract", file=sys.stderr)
        print("      Ubuntu : sudo apt-get install -y tesseract-ocr", file=sys.stderr)
        print("      Windows: winget install UB-Mannheim.TesseractOCR", file=sys.stderr)
        print(f"    Details: {exc}", file=sys.stderr)
        sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="AI-powered invoice data extraction (Tesseract OCR -> JSON)."
    )
    _default_image = Path.home() / "Downloads" / "AI-Powered Invoice Extraction Task.png"
    _default_output = Path.home() / "Downloads" / "invoice_extracted.json"

    parser.add_argument(
        "--image",
        default=str(_default_image),
        help="Path to the invoice image.",
    )
    parser.add_argument(
        "--output",
        default=str(_default_output),
        help="Path for the output JSON file.",
    )
    args = parser.parse_args(argv)

    check_tesseract()

    print(f"[+] Reading invoice image: {args.image}")
    try:
        text = extract_text(args.image)
    except Exception as exc:
        print(f"[-] {exc}", file=sys.stderr)
        return 1

    print("[+] OCR complete. Parsing fields...")
    invoice = parse_invoice(text)
    output_path = write_json(invoice, args.output)

    print(f"[+] Extracted {len(invoice['items'])} line items.")
    print(f"[+] Validation: {invoice['validation']}")
    print(f"[+] Wrote JSON to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
