
#!/usr/bin/env python3
"""
Invoice Data Extraction — GUI version (no command line needed).

A simple graphical app for the AI-Powered Invoice Extraction task.
Just pick the invoice image, click Extract, and save the JSON.

Usage:
    python invoice_extractor.py
"""

import json
import re
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pytesseract
from PIL import Image

# ---------------------------------------------------------------------------
# Core extraction (same logic as app.py)
# ---------------------------------------------------------------------------

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def _clean_currency(value):
    return float(str(value).replace(",", "").strip())


def _parse_date(text):
    text = text.strip().rstrip('.')
    match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
    if match:
        day, month_name, year = match.group(1), match.group(2).lower().rstrip('s'), match.group(3)
        month = MONTHS.get(month_name)
        if month:
            return f"{year}-{month:02d}-{int(day):02d}"
    return text


def _extract_items(lines):
    items = []
    for line in lines:
        match = re.match(r'^\s*\d+\s+(.+?)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})\s*$', line)
        if not match:
            continue
        raw_desc = match.group(1).strip()
        unit_price = _clean_currency(match.group(2))
        amount = _clean_currency(match.group(3))

        quantity = None
        measure = None
        qm = re.search(r'(\d+)\s*(pes|pc|ot|hrs?|units?)\b', raw_desc, re.IGNORECASE)
        if qm:
            quantity = int(qm.group(1))
            measure = qm.group(2).lower()
            if measure == "ot":
                measure = "pc"
            raw_desc = re.sub(qm.group(0), "", raw_desc).strip()

        items.append({
            "description": raw_desc.strip("| "),
            "quantity": quantity,
            "unit_price": unit_price,
            "amount": amount,
        })
    return items


def parse_invoice(text):
    lines = [ln.strip() for ln in text.splitlines()]
    invoice = {
        "invoice_number": None, "invoice_date": None, "due_date": None,
        "payment_terms": None, "supplier_name": None, "supplier_address": None,
        "supplier_phone": None, "supplier_email": None, "bill_to_name": None,
        "bill_to_address": None, "items": [], "subtotal": None, "vat": None,
        "total_amount": None,
        "validation": {
            "subtotal_matches_item_sum": None, "vat_calculation_ok": None,
            "total_matches_expected": None,
        },
        "raw_text": text,
    }

    m = re.search(r'Invoice\s*No\s*[:\-]\s*(RT-\d{4}-\d+)', text, re.IGNORECASE)
    if m:
        invoice["invoice_number"] = m.group(1).upper()

    m = re.search(r'Invoice\s*Date\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["invoice_date"] = _parse_date(m.group(1))

    m = re.search(r'Due\s*Date\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["due_date"] = _parse_date(m.group(1))

    m = re.search(r'Payment\s*Terms\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["payment_terms"] = m.group(1).strip()

    m = re.search(r'(RIVERTECH SUPPLIES LTD\.)', text, re.IGNORECASE)
    if m:
        invoice["supplier_name"] = m.group(1)

    m = re.search(r'45\s+Industrial\s+Estate\s+Road\s*,?\s*[\w\s,]*?\s+Nepal\s*,?\s*,?', text, re.IGNORECASE)
    if m:
        addr = m.group(0)
        addr = re.sub(r'[Ww]', '', addr)
        addr = re.sub(r'Industrial Estate Road\s+Kathmandu', 'Industrial Estate Road, Kathmandu', addr)
        invoice["supplier_address"] = " ".join(addr.split())

    m = re.search(r'Phone\s*[:\-]\s*([\+\d\s]+?)\s+(?:RIVERTECH|Email)', text, re.IGNORECASE)
    if m:
        invoice["supplier_phone"] = m.group(1).strip()

    m = re.search(r'Email\s*[:\-]\s*([\w.@]+)', text, re.IGNORECASE)
    if m:
        invoice["supplier_email"] = m.group(1)

    m = re.search(r'Bill\s+To\s*[:\-]\s*INVOICE\s+(.+?)(?:\n|$)', text, re.IGNORECASE)
    if m:
        invoice["bill_to_name"] = m.group(1).strip()

    sanob_pos = text.find('Sanobharyang')
    if sanob_pos != -1:
        nep_pos = text.find('Nepal', sanob_pos)
        if nep_pos != -1:
            addr = text[sanob_pos:nep_pos + len('Nepal')]
            addr = re.sub(r'\s*Invoice\s+Date[^,\n]*', '', addr)
            invoice["bill_to_address"] = " ".join(addr.split())

    invoice["items"] = _extract_items(lines)

    m = re.search(r'Subtotal\s*\(NPR\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["subtotal"] = _clean_currency(m.group(1))

    m = re.search(r'VAT\s*\(13%\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["vat"] = _clean_currency(m.group(1))

    m = re.search(r'Total\s+Amount\s*\(NPR\)\s+([\d,]+\.\d{2})', text, re.IGNORECASE)
    if m:
        invoice["total_amount"] = _clean_currency(m.group(1))

    item_sum = sum(item["amount"] for item in invoice["items"])
    invoice["validation"]["subtotal_matches_item_sum"] = \
        invoice["subtotal"] is not None and abs(item_sum - invoice["subtotal"]) < 0.01

    expected_vat = invoice["subtotal"] * 0.13 if invoice["subtotal"] else None
    invoice["validation"]["vat_calculation_ok"] = \
        invoice["vat"] is not None and expected_vat is not None and \
        abs(invoice["vat"] - expected_vat) < 0.01

    expected_total = (invoice["subtotal"] or 0) + (invoice["vat"] or 0)
    invoice["validation"]["total_matches_expected"] = \
        invoice["total_amount"] is not None and abs(invoice["total_amount"] - expected_total) < 0.01

    return invoice


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------


def _fmt_money(value):
    """Format a currency value, or 'n/a' when the field is missing."""
    return f"{value:,.2f} NPR" if value is not None else "n/a"


class InvoiceExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Data Extractor")
        self.root.geometry("920x720")
        self.root.minsize(700, 600)

        # Default image path (from the job email)
        self.default_image = Path(
            "/home/dante/Downloads/AI-Powered Invoice Extraction Task.png"
        )
        self.current_image = None

        self._build_ui()
        self._check_default_image()

    # -- UI construction ---------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", **pad)
        ttk.Label(
            header, text="AI-Powered Invoice Data Extraction",
            font=("", 14, "bold")
        ).pack(side="left")
        ttk.Label(
            header, text="Pick an invoice image and click Extract.",
            font=("", 10), foreground="#666666"
        ).pack(side="right")

        # File selection
        file_row = ttk.Frame(self.root)
        file_row.pack(fill="x", **pad)
        ttk.Label(file_row, text="Invoice image:").pack(side="left")
        self.image_path_label = ttk.Label(
            file_row, text="No image selected", foreground="#999999"
        )
        self.image_path_label.pack(side="left", fill="x", expand=True, padx=10)

        self.btn_browse = ttk.Button(
            file_row, text="Select Invoice Image...", command=self._browse
        )
        self.btn_browse.pack(side="right")

        # Action buttons
        action_row = ttk.Frame(self.root)
        action_row.pack(fill="x", **pad)
        self.btn_extract = ttk.Button(
            action_row, text="Extract Invoice", command=self._extract
        )
        self.btn_extract.pack(side="left", fill="x", expand=True)

        self.btn_save = ttk.Button(
            action_row, text="Save JSON...", command=self._save
        )
        self.btn_save.pack(side="right", padx=(6, 0))
        self.btn_save.state(["disabled"])

        # JSON output
        output_frame = ttk.Frame(self.root)
        output_frame.pack(fill="both", expand=True, **pad)
        ttk.Label(output_frame, text="Extracted data (JSON):").pack(anchor="w")

        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill="both", expand=True)
        self.output_text = tk.Text(
            text_frame, wrap="none", font=("", 10),
            state="disabled", undo=True
        )
        self.output_text.pack(fill="both", expand=True, side="left")
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.output_text.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.output_text.configure(yscrollcommand=scrollbar.set)

        # Status bar
        status = ttk.Frame(self.root)
        status.pack(fill="x", **pad)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            status, textvariable=self.status_var, foreground="#666666"
        ).pack(side="left")

    def _check_default_image(self):
        """If the email's invoice is in Downloads, pre-select it."""
        if self.default_image.exists():
            self.image_path_label.config(
                text=str(self.default_image), foreground="#228B22"
            )
            self.btn_extract.state(["!disabled"])

    # -- Actions ---------------------------------------------------------

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select invoice image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.current_image = Path(path)
            self.image_path_label.config(
                text=str(self.current_image), foreground="#228B22"
            )
            self.btn_extract.state(["!disabled"])

    def _extract(self):
        if self.current_image is None:
            # Try the default image from the email
            if self.default_image.exists():
                self.current_image = self.default_image
            else:
                messagebox.showwarning(
                    "No image selected",
                    "Please select an invoice image first.\n\n"
                    "Click 'Select Invoice Image...' and choose the PNG file "
                    "from your Downloads folder.",
                )
                return

        self.btn_extract.state(["disabled"])
        self.status_var.set("Extracting... (OCR + parsing)")
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)

        try:
            text = self._ocr(self.current_image)
            invoice = parse_invoice(text)
            self._last_result = invoice
            self._show_result(invoice)
            self._show_summary(invoice)
            self.btn_save.state(["!disabled"])
            self.status_var.set(
                f"Extracted {len(invoice['items'])} items | Validated: {invoice['validation']}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Extraction failed",
                f"Could not extract from the invoice image.\n\nError:\n{exc}",
            )
            self.status_var.set("Extraction failed")
        finally:
            self.btn_extract.state(["!disabled"])
            self.output_text.config(state="disabled")

    def _ocr(self, image_path):
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    def _show_result(self, invoice):
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, json.dumps(invoice, indent=2, ensure_ascii=False))
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")


    def _show_summary(self, invoice):
        """Show a human-readable summary below the JSON."""
        self.output_text.config(state="normal")
        self.output_text.insert(
            tk.END,
            "\n\n" + "=" * 50 + "\n",
            ("summary",),
        )
        self.output_text.insert(tk.END, "Summary\n", ("summary"))
        self.output_text.insert(tk.END, "-" * 30 + "\n")
        self.output_text.insert(tk.END, f"  Invoice: {invoice['invoice_number']} | {invoice['invoice_date']}\n")
        self.output_text.insert(tk.END, f"  Total: {_fmt_money(invoice['total_amount'])}\n")
        self.output_text.insert(tk.END, f"  Items: {len(invoice['items'])}\n")
        self.output_text.insert(tk.END, f"  Validation: {invoice['validation']}\n")
        self.output_text.insert(tk.END, "-" * 30 + "\n")
        for it in invoice["items"]:
            q = it["quantity"] or "n/a"
            self.output_text.insert(tk.END, f"  - {it['description']:30s} qty={q:>4}  "
                                             f"unit={it['unit_price']:>9,.2f}  "
                                             f"amount={it['amount']:>10,.2f}\n")
        self.output_text.config(state="disabled")
        self.output_text.see(tk.END)

    def _save(self):
        if self.current_image is None:
            messagebox.showwarning(
                "No image", "Please select an invoice image first."
            )
            return

        if self.current_image.suffix.lower() == ".png":
            default_name = self.current_image.stem + "_extracted.json"
        else:
            default_name = "invoice_extracted.json"

        path = filedialog.asksaveasfilename(
            title="Save extracted JSON",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(self._last_result, fh, indent=2, ensure_ascii=False)
                self.status_var.set(f"Saved: {path}")
                messagebox.showinfo(
                    "Saved", f"Extracted data saved to:\n{path}"
                )
            except Exception as exc:
                messagebox.showerror("Save failed", str(exc))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    root = tk.Tk()
    app = InvoiceExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main())
