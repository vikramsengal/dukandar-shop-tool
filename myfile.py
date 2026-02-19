# myfile.py
# Desktop GST Statement Analyzer (CSV/PDF) - Single file app

import csv
import json
import os
import re
import tempfile
import webbrowser
from urllib.parse import urlencode
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import pdfplumber
except Exception:
    pdfplumber = None


APP_TITLE = "Dukandar GST Statement Tool"
PAYMENT_LINK = "https://rzp.io/l/YOUR_10RS_6MONTH_LINK"   # <- apna Razorpay/Paytm payment link
DOWNLOAD_LINK = "https://yourdomain.com/downloads/dukandar-tool.exe"  # <- apka exe download link
UPI_ID = "sengalvikram004-2@oksbi"  # <- apni UPI ID
PAYEE_NAME = "apna Tool"
PAY_AMOUNT = 10
UPI_NOTE = "Dukandar Tool 6 month unlock"
FREE_TRIES = 10  
QR_IMAGE_PATH = "QR_code.png"  # <- app ke same folder me QR image rakho (png/jpg supported via fallback)
ADMIN_UNLOCK_CODE = "CHANGE_ME_UNLOCK_2026"  # <- payment receive verify karne ke baad user ko yahi code do
STATE_FILE = Path.home() / ".dukandar_tool_state.json"


DEBIT_KEYWORDS = [
    "debit", "debited", "paid", "payment", "sent", "transfer to", "withdraw", "dr"
]
CREDIT_KEYWORDS = [
    "credit", "credited", "received", "collect", "deposit", "refund", "cr", "added"
]

AMOUNT_REGEX = re.compile(
    r"(?:INR|Rs\.?|₹)?\s*([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.\d{1,2})?|[0-9]+(?:\.\d{1,2})?)",
    re.IGNORECASE
)
DATE_TOKEN_REGEX = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

DATE_FORMATS = [
    "%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y",
    "%Y-%m-%d", "%Y/%m/%d",
    "%m-%d-%Y", "%m/%d/%Y", "%m-%d-%y", "%m/%d/%y",
]


def clean_amount(value: str) -> float:
    if value is None:
        return 0.0
    s = str(value).strip()
    s = re.sub(r"[^\d,.\-]", "", s)
    s = s.replace(",", "")
    if s in ("", ".", "-", "-."):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def guess_column(columns, candidates):
    low = [c.strip().lower() for c in columns]
    for i, c in enumerate(low):
        for k in candidates:
            if k in c:
                return columns[i]
    return None


def normalize_date(value):
    if value is None:
        return None
    txt = str(value).strip()
    if not txt:
        return None

    txt = txt.split(" ")[0].strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(txt, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_date_from_line(line):
    m = DATE_TOKEN_REGEX.search(line or "")
    if not m:
        return None
    return normalize_date(m.group(1))


def init_day_bucket():
    return {"debit": 0.0, "credit": 0.0, "count": 0}


def load_state():
    default_state = {"used_tries": 0, "paid_unlocked": False}
    if not STATE_FILE.exists():
        return default_state
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "used_tries": int(data.get("used_tries", 0)),
            "paid_unlocked": bool(data.get("paid_unlocked", False)),
        }
    except Exception:
        return default_state


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=True, indent=2)
    except Exception:
        pass


def parse_csv_statement(file_path):
    total_debit = 0.0
    total_credit = 0.0
    rows_count = 0
    daily = defaultdict(init_day_bucket)

    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    last_err = None

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    continue

                debit_col = guess_column(
                    reader.fieldnames,
                    ["debit", "withdraw", "paid", "dr", "sent", "outflow", "transfer out"]
                )
                credit_col = guess_column(
                    reader.fieldnames,
                    ["credit", "deposit", "received", "cr", "inflow", "transfer in", "added"]
                )
                amount_col = guess_column(reader.fieldnames, ["amount", "amt"])
                type_col = guess_column(reader.fieldnames, ["type", "txn type", "transaction type", "cr/dr", "dr/cr"])
                date_col = guess_column(reader.fieldnames, ["date", "txn date", "transaction date", "value date", "posted date"])

                for row in reader:
                    rows_count += 1
                    d = clean_amount(row.get(debit_col, "")) if debit_col else 0.0
                    c = clean_amount(row.get(credit_col, "")) if credit_col else 0.0

                    # If separate debit/credit cols not found, use amount + type
                    if d == 0.0 and c == 0.0 and amount_col:
                        amt = clean_amount(row.get(amount_col, ""))
                        t = str(row.get(type_col, "")).lower() if type_col else ""
                        if any(k in t for k in DEBIT_KEYWORDS):
                            d += amt
                        elif any(k in t for k in CREDIT_KEYWORDS):
                            c += amt

                    total_debit += d
                    total_credit += c

                    tx_date = normalize_date(row.get(date_col, "")) if date_col else None
                    if not tx_date:
                        tx_date = "Unknown Date"
                    daily[tx_date]["debit"] += d
                    daily[tx_date]["credit"] += c
                    daily[tx_date]["count"] += 1

            return total_debit, total_credit, rows_count, dict(daily)
        except Exception as e:
            last_err = e

    raise ValueError(f"CSV parse failed: {last_err}")


def parse_pdf_statement(file_path):
    if pdfplumber is None:
        raise ValueError("PDF support ke liye `pip install pdfplumber` required hai.")

    total_debit = 0.0
    total_credit = 0.0
    rows_count = 0
    daily = defaultdict(init_day_bucket)

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.splitlines()

            for line in lines:
                low = line.lower()
                amounts = AMOUNT_REGEX.findall(line)
                if not amounts:
                    continue

                # Line me last amount ko txn amount assume kar rahe hain
                amt = clean_amount(amounts[-1])
                if amt <= 0:
                    continue

                is_debit = any(k in low for k in DEBIT_KEYWORDS)
                is_credit = any(k in low for k in CREDIT_KEYWORDS)
                tx_date = extract_date_from_line(line) or "Unknown Date"

                if is_debit and not is_credit:
                    total_debit += amt
                    rows_count += 1
                    daily[tx_date]["debit"] += amt
                    daily[tx_date]["count"] += 1
                elif is_credit and not is_debit:
                    total_credit += amt
                    rows_count += 1
                    daily[tx_date]["credit"] += amt
                    daily[tx_date]["count"] += 1
                else:
                    # Ambiguous lines skip
                    pass

    return total_debit, total_credit, rows_count, dict(daily)


def calculate_tax(total_debit, total_credit, gst_rate, add_pct, add_fixed, basis):
    if basis == "Credit":
        taxable = total_credit
    elif basis == "Debit":
        taxable = total_debit
    else:  # Net Credit
        taxable = max(total_credit - total_debit, 0.0)

    gst = taxable * (gst_rate / 100.0)
    additional = taxable * (add_pct / 100.0) + add_fixed
    total_payable = gst + additional

    return taxable, gst, additional, total_payable


def money(x):
    return f"₹ {x:,.2f}"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("950x620")
        self.minsize(900, 560)

        self.file_path = None
        self.total_debit = 0.0
        self.total_credit = 0.0
        self.rows_count = 0
        self.daily_summary = {}
        self.state = load_state()
        self.used_tries = max(0, int(self.state.get("used_tries", 0)))
        self.paid_unlocked = bool(self.state.get("paid_unlocked", False))
        self.qr_img = None

        self.gst_rate = tk.StringVar(value="18")
        self.add_pct = tk.StringVar(value="0")
        self.add_fixed = tk.StringVar(value="0")
        self.tax_basis = tk.StringVar(value="Net Credit")

        self._build_ui()
        self._refresh_access_state()
        if self._is_locked():
            self.after(150, self.show_payment_popup)

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Statement File (CSV/PDF):").grid(row=0, column=0, sticky="w")
        self.file_entry = ttk.Entry(top, width=78)
        self.file_entry.grid(row=0, column=1, padx=8, sticky="we")
        ttk.Button(top, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=4)

        settings = ttk.LabelFrame(self, text="Tax Settings", padding=12)
        settings.pack(fill="x", padx=12, pady=6)

        ttk.Label(settings, text="GST %").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.gst_rate, width=12).grid(row=0, column=1, padx=8)

        ttk.Label(settings, text="Additional %").grid(row=0, column=2, sticky="w")
        ttk.Entry(settings, textvariable=self.add_pct, width=12).grid(row=0, column=3, padx=8)

        ttk.Label(settings, text="Additional Fixed (₹)").grid(row=0, column=4, sticky="w")
        ttk.Entry(settings, textvariable=self.add_fixed, width=12).grid(row=0, column=5, padx=8)

        ttk.Label(settings, text="Tax Basis").grid(row=0, column=6, sticky="w")
        ttk.Combobox(
            settings,
            textvariable=self.tax_basis,
            values=["Credit", "Debit", "Net Credit"],
            state="readonly",
            width=14
        ).grid(row=0, column=7, padx=8)

        btns = ttk.Frame(self, padding=(12, 2))
        btns.pack(fill="x")
        self.analyze_btn = ttk.Button(btns, text="Analyze", command=self.analyze)
        self.analyze_btn.pack(side="left", padx=4)
        self.report_btn = ttk.Button(btns, text="Generate HTML Report", command=self.generate_html_report)
        self.report_btn.pack(side="left", padx=4)
        self.unlock_btn = ttk.Button(btns, text="Unlock (Pay ₹10)", command=self.show_payment_popup)
        self.unlock_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Open Payment Link (₹10 / 6 months)", command=lambda: webbrowser.open(PAYMENT_LINK)).pack(side="right", padx=4)
        ttk.Button(btns, text="Open Download Link", command=lambda: webbrowser.open(DOWNLOAD_LINK)).pack(side="right", padx=4)

        self.tree = ttk.Treeview(self, columns=("date", "metric", "value"), show="headings", height=18)
        self.tree.heading("date", text="Date")
        self.tree.heading("metric", text="Metric")
        self.tree.heading("value", text="Value")
        self.tree.column("date", width=180, anchor="w")
        self.tree.column("metric", width=280, anchor="w")
        self.tree.column("value", width=390, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=8)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", padx=12, pady=(0, 10))

    def _is_locked(self):
        return (not self.paid_unlocked) and self.used_tries >= FREE_TRIES

    def _tries_left(self):
        return max(FREE_TRIES - self.used_tries, 0)

    def _persist_state(self):
        self.state["used_tries"] = self.used_tries
        self.state["paid_unlocked"] = self.paid_unlocked
        save_state(self.state)

    def _refresh_access_state(self):
        if self._is_locked():
            self.analyze_btn.config(state="disabled")
            self.report_btn.config(state="disabled")
            self.status.set("Free tries khatam. Unlock ke liye payment karo.")
        else:
            self.analyze_btn.config(state="normal")
            self.report_btn.config(state="normal")
            if self.paid_unlocked:
                self.status.set("Paid plan active. Unlimited usage.")
            else:
                self.status.set(f"Free tries left: {self._tries_left()} / {FREE_TRIES}")

    def _consume_try(self):
        if self.paid_unlocked:
            return
        self.used_tries += 1
        self._persist_state()
        self._refresh_access_state()
        if self._is_locked():
            messagebox.showinfo("Free Limit", "Aapke 10 free tries complete ho gaye. Ab payment required hai.")
            self.show_payment_popup()

    def _open_upi_intent(self):
        params = {
            "pa": UPI_ID,
            "pn": PAYEE_NAME,
            "am": f"{PAY_AMOUNT:.2f}",
            "cu": "INR",
            "tn": UPI_NOTE,
        }
        upi_link = "upi://pay?" + urlencode(params)
        webbrowser.open(upi_link)

    def show_payment_popup(self):
        if self.paid_unlocked:
            messagebox.showinfo("Info", "App already unlocked.")
            return

        popup = tk.Toplevel(self)
        popup.title("Unlock Required")
        popup.geometry("420x560")
        popup.resizable(False, False)
        popup.grab_set()
        popup.transient(self)

        ttk.Label(
            popup,
            text=f"Free tries used: {self.used_tries}/{FREE_TRIES}\nUnlock ke liye ₹{PAY_AMOUNT} payment karein.",
            justify="center",
        ).pack(pady=10)

        qr_base = Path(__file__).with_name(QR_IMAGE_PATH)
        qr_candidates = [qr_base]
        # Common fallback names/extensions, so a minor filename mismatch doesn't break unlock UI.
        for name in ("QR_code.jpg", "QR_code.jpeg", "QR_code.png"):
            p = Path(__file__).with_name(name)
            if p not in qr_candidates:
                qr_candidates.append(p)
        qr_path = next((p for p in qr_candidates if p.exists()), None)

        if qr_path:
            try:
                self.qr_img = tk.PhotoImage(file=str(qr_path))
                ttk.Label(popup, image=self.qr_img).pack(pady=6)
            except Exception:
                ttk.Label(popup, text="QR image load nahi hua. Neeche payment link use karein.").pack(pady=6)
        else:
            ttk.Label(popup, text=f"QR file nahi mili: {qr_base.name}").pack(pady=6)

        ttk.Label(popup, text=f"UPI: {UPI_ID}").pack(pady=4)
        ttk.Button(popup, text="Open UPI Payment", command=self._open_upi_intent).pack(pady=4)
        ttk.Button(popup, text="Open Payment Link", command=lambda: webbrowser.open(PAYMENT_LINK)).pack(pady=4)

        ttk.Separator(popup).pack(fill="x", padx=16, pady=10)
        ttk.Label(popup, text="Payment ke baad unlock code daalein:").pack(pady=4)
        code_var = tk.StringVar()
        ttk.Entry(popup, textvariable=code_var, width=36).pack(pady=4)

        def do_unlock():
            if code_var.get().strip() == ADMIN_UNLOCK_CODE:
                self.paid_unlocked = True
                self._persist_state()
                self._refresh_access_state()
                popup.destroy()
                messagebox.showinfo("Success", "App unlocked successfully.")
            else:
                messagebox.showerror("Invalid", "Unlock code galat hai.")

        ttk.Button(popup, text="Unlock App", command=do_unlock).pack(pady=8)
        ttk.Label(
            popup,
            text="Note: app offline hai, isliye payment auto-verify nahi hota.\nAap payment check karke code share karein.",
            justify="center",
        ).pack(pady=8)

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Statement",
            filetypes=[("Statements", "*.csv *.pdf"), ("CSV", "*.csv"), ("PDF", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.file_path = path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)

    def analyze(self):
        if self._is_locked():
            self.show_payment_popup()
            return

        path = self.file_entry.get().strip()
        if not path or not Path(path).exists():
            messagebox.showerror("Error", "Valid file select karo.")
            return

        try:
            ext = Path(path).suffix.lower()
            if ext == ".csv":
                d, c, r, daily = parse_csv_statement(path)
            elif ext == ".pdf":
                d, c, r, daily = parse_pdf_statement(path)
            else:
                messagebox.showerror("Error", "Sirf CSV/PDF supported hai.")
                return

            self.total_debit = d
            self.total_credit = c
            self.rows_count = r
            self.daily_summary = daily

            gst_rate = clean_amount(self.gst_rate.get())
            add_pct = clean_amount(self.add_pct.get())
            add_fixed = clean_amount(self.add_fixed.get())

            taxable, gst, additional, total_payable = calculate_tax(
                d, c, gst_rate, add_pct, add_fixed, self.tax_basis.get()
            )

            self.tree.delete(*self.tree.get_children())
            rows = [
                ("-", "File", path),
                ("-", "Transactions Parsed", str(r)),
                ("-", "Total Debit / Transfer Out", money(d)),
                ("-", "Total Credit / Received", money(c)),
                ("-", "Tax Basis", self.tax_basis.get()),
                ("-", "Taxable Amount", money(taxable)),
                ("-", f"GST ({gst_rate:.2f}%)", money(gst)),
                ("-", f"Additional Charges ({add_pct:.2f}% + fixed)", money(additional)),
                ("-", "Total Estimated Payable", money(total_payable)),
                ("-", "Net Balance (Credit - Debit)", money(c - d)),
                ("-", "", ""),
                ("-", "Per-Day Breakdown", ""),
            ]
            for row in rows:
                self.tree.insert("", "end", values=row)

            ordered_dates = sorted(
                self.daily_summary.keys(),
                key=lambda x: (x == "Unknown Date", x)
            )
            for day in ordered_dates:
                day_d = self.daily_summary[day]["debit"]
                day_c = self.daily_summary[day]["credit"]
                day_taxable, day_gst, day_additional, day_total = calculate_tax(
                    day_d,
                    day_c,
                    gst_rate,
                    add_pct,
                    add_fixed,
                    self.tax_basis.get(),
                )
                self.tree.insert("", "end", values=(day, "Txn Count", str(self.daily_summary[day]["count"])))
                self.tree.insert("", "end", values=(day, "Debit", money(day_d)))
                self.tree.insert("", "end", values=(day, "Credit", money(day_c)))
                self.tree.insert("", "end", values=(day, "Taxable", money(day_taxable)))
                self.tree.insert("", "end", values=(day, "GST", money(day_gst)))
                self.tree.insert("", "end", values=(day, "Additional", money(day_additional)))
                self.tree.insert("", "end", values=(day, "Total Payable", money(day_total)))

            self._consume_try()
            self.status.set("Analysis complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.set("Failed.")

    def generate_html_report(self):
        if self._is_locked():
            self.show_payment_popup()
            return

        if self.total_credit == 0 and self.total_debit == 0:
            messagebox.showwarning("Warning", "Pehle Analyze karo.")
            return

        gst_rate = clean_amount(self.gst_rate.get())
        add_pct = clean_amount(self.add_pct.get())
        add_fixed = clean_amount(self.add_fixed.get())

        taxable, gst, additional, total_payable = calculate_tax(
            self.total_debit, self.total_credit, gst_rate, add_pct, add_fixed, self.tax_basis.get()
        )

        day_rows = []
        ordered_dates = sorted(
            self.daily_summary.keys(),
            key=lambda x: (x == "Unknown Date", x)
        )
        for day in ordered_dates:
            day_d = self.daily_summary[day]["debit"]
            day_c = self.daily_summary[day]["credit"]
            day_taxable, day_gst, day_additional, day_total = calculate_tax(
                day_d, day_c, gst_rate, add_pct, add_fixed, self.tax_basis.get()
            )
            day_rows.append(
                f"<tr>"
                f"<td>{day}</td>"
                f"<td>{self.daily_summary[day]['count']}</td>"
                f"<td>{money(day_d)}</td>"
                f"<td>{money(day_c)}</td>"
                f"<td>{money(day_taxable)}</td>"
                f"<td>{money(day_gst)}</td>"
                f"<td>{money(day_additional)}</td>"
                f"<td>{money(day_total)}</td>"
                f"</tr>"
            )

        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GST Statement Report</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#f7f8fb;margin:0;padding:24px;color:#1e293b}}
.card{{max-width:900px;margin:auto;background:#fff;border-radius:14px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,.08)}}
h1{{margin:0 0 10px;font-size:24px}}
small{{color:#64748b}}
table{{width:100%;border-collapse:collapse;margin-top:16px}}
th,td{{text-align:left;padding:10px;border-bottom:1px solid #e2e8f0}}
th{{background:#f1f5f9}}
.badge{{display:inline-block;padding:4px 10px;background:#ecfeff;color:#155e75;border-radius:999px;font-size:12px}}
</style>
</head>
<body>
<div class="card">
  <h1>Dukandar GST Statement Report</h1>
  <small>Generated: {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}</small>
  <div style="margin-top:8px"><span class="badge">Tax Basis: {self.tax_basis.get()}</span></div>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>Transactions Parsed</td><td>{self.rows_count}</td></tr>
    <tr><td>Total Debit / Transfer Out</td><td>{money(self.total_debit)}</td></tr>
    <tr><td>Total Credit / Received</td><td>{money(self.total_credit)}</td></tr>
    <tr><td>Taxable Amount</td><td>{money(taxable)}</td></tr>
    <tr><td>GST ({gst_rate:.2f}%)</td><td>{money(gst)}</td></tr>
    <tr><td>Additional Charges ({add_pct:.2f}% + fixed)</td><td>{money(additional)}</td></tr>
    <tr><td><b>Total Estimated Payable</b></td><td><b>{money(total_payable)}</b></td></tr>
    <tr><td>Net Balance (Credit - Debit)</td><td>{money(self.total_credit - self.total_debit)}</td></tr>
  </table>
  <h2 style="margin-top:18px;font-size:20px">Per-Day Summary</h2>
  <table>
    <tr>
      <th>Date</th><th>Txn Count</th><th>Debit</th><th>Credit</th>
      <th>Taxable</th><th>GST</th><th>Additional</th><th>Total Payable</th>
    </tr>
    {''.join(day_rows)}
  </table>
  <p style="margin-top:16px;color:#64748b;font-size:13px">
    Note: Ye estimate report hai. Final GST filing se pehle CA se verify karna recommended hai.
  </p>
</div>
</body>
</html>"""

        out_path = os.path.join(tempfile.gettempdir(), f"gst_report_{int(datetime.now().timestamp())}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        webbrowser.open(out_path)
        self.status.set(f"HTML report generated: {out_path}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
