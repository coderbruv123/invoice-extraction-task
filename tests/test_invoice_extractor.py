"""Regression tests for the invoice parsing logic.

Run:  python -m unittest discover -s tests -v
(Module-level imports of invoice_extractor pull in tkinter+pytesseract/Pillow
without creating a display, so these run headless; only app.py's main() needs
a screen.)
"""

import json
import os
import unittest
from pathlib import Path

import invoice_extractor as ie

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "outputs" / "invoice.json"


class ParseInvoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(SAMPLE, encoding="utf-8") as fh:
            cls.data = json.load(fh)
        cls.text = cls.data["raw_text"]

    def test_core_fields_extracted(self):
        invoice = ie.parse_invoice(self.text)
        self.assertEqual(invoice["invoice_number"], "RT-2024-1052")
        self.assertEqual(invoice["invoice_date"], "2024-10-14")
        self.assertEqual(invoice["due_date"], "2024-11-13")
        self.assertEqual(invoice["supplier_name"], "RIVERTECH SUPPLIES LTD.")
        self.assertEqual(
            invoice["supplier_address"],
            "45 Industrial Estate Road, Kathmandu 44600, Nepal",
        )
        self.assertEqual(invoice["bill_to_name"], "Deutschelink GmbH")
        self.assertEqual(invoice["bill_to_address"], "Sanobharyang, Kathmandu 44700 Nepal")

    def test_items_extracted(self):
        self.assertEqual(len(self.data["items"]), 5)
        # (description, quantity, unit_price, amount)
        expected = [
            ("HDPE Pipe 110mm (6m length)", 50, 1250.0, 62500.0),
            ("HDPE Elbow 90° 110mm", 20, 450.0, 9000.0),
            ("HDPE Coupling 110mm", 30, 300.0, 9000.0),
            ("Welding Service", 10, 1500.0, 15000.0),
            ("Delivery Charge", 1, 5000.0, 5000.0),
        ]
        for got, want in zip(self.data["items"], expected):
            with self.subTest(item=got):
                self.assertEqual((got["description"], got["quantity"],
                                  got["unit_price"], got["amount"]), want)

    def test_validation_all_true(self):
        invoice = ie.parse_invoice(self.text)
        self.assertTrue(invoice["validation"]["subtotal_matches_item_sum"])
        self.assertTrue(invoice["validation"]["vat_calculation_ok"])
        self.assertTrue(invoice["validation"]["total_matches_expected"])

    def test_totals_consistent(self):
        invoice = ie.parse_invoice(self.text)
        item_sum = sum(it["amount"] for it in invoice["items"])
        self.assertAlmostEqual(item_sum, invoice["subtotal"], places=2)
        self.assertAlmostEqual(invoice["subtotal"] * 0.13, invoice["vat"], places=2)
        self.assertAlmostEqual(
            invoice["subtotal"] + invoice["vat"], invoice["total_amount"], places=2
        )

    def test_currency_cleaning(self):
        self.assertEqual(ie._clean_currency("1,250.00"), 1250.0)
        self.assertEqual(ie._clean_currency("5.00"), 5.0)

    def test_date_parsing(self):
        self.assertEqual(ie._parse_date("14 October 2024"), "2024-10-14")
        self.assertEqual(ie._parse_date("13 November 2024"), "2024-11-13")
        self.assertEqual(ie._parse_date("not a date"), "not a date")


if __name__ == "__main__":
    unittest.main()
