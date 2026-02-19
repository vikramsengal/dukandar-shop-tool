import csv
import json
import os
import re
import shutil
import sys
import tempfile
import traceback
import webbrowser
from urllib.request import urlopen
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
try:
    import pytesseract
except Exception:
    pytesseract = None
else:
    tess_cmd = os.environ.get("TESSERACT_CMD", "").strip()
    if tess_cmd and Path(tess_cmd).exists():
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
    else:
        auto_tess = shutil.which("tesseract")
        default_win_tess = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if auto_tess:
            pytesseract.pytesseract.tesseract_cmd = auto_tess
        elif Path(default_win_tess).exists():
            pytesseract.pytesseract.tesseract_cmd = default_win_tess


APP_TITLE = "Dukandar GST Statement Tool"
PAYMENT_LINK = "https://razorpay.me/@vikrambhaiparabatabhaisengal"   # <- apna Razorpay/Paytm payment link
DOWNLOAD_LINK = "https://github.com/vikramsengal/dukandar-shop-tool/raw/main/dist/myfile.exe"  # <- direct GitHub download link
UPI_ID = "sengalvikram004-2@oksbi"  # <- apni UPI ID
PAYEE_NAME = "apna Tool"
PAY_AMOUNT = 10
UPI_NOTE = "Dukandar Tool 6 month unlock"
FREE_TRIES = 10  
QR_IMAGE_PATH = "QR_code.png"  # <- app ke same folder me QR image rakho (png/jpg supported via fallback)
ADMIN_UNLOCK_CODE = "CHANGE_ME_UNLOCK_2026"  # <- payment receive verify karne ke baad user ko yahi code do
STATE_FILE = Path.home() / ".dukandar_tool_state.json"
LOG_FILE = Path.home() / ".dukandar_tool_error.log"
APP_VERSION = "1.2.0"
VERSION_URL = "https://raw.githubusercontent.com/vikramsengal/dukandar-shop-tool/main/VERSION.txt"


CATEGORY_RULES = {
    "Rent": ["rent", "landlord", "lease"],
    "Salary": ["salary", "payroll", "wage"],
    "Utilities": ["electricity", "water", "gas", "bill", "recharge", "broadband"],
    "Food": ["swiggy", "zomato", "restaurant", "food"],
    "Transfer": ["upi", "imps", "neft", "rtgs", "transfer"],
    "Shopping": ["amazon", "flipkart", "store", "mart"],
    "Refund": ["refund", "reversal", "chargeback"],
    "Tax": ["gst", "tax", "tds", "income tax"],
}


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


BANK_HINTS = {
    "SBI": ["state bank", "sbi", "sb account", "txn ref no"],
    "HDFC": ["hdfc", "chq./ref.no.", "narration", "value dt"],
    "ICICI": ["icici", "transaction remarks", "withdrawal amt", "deposit amt"],
    "AXIS": ["axis", "tran date", "particulars", "chq no"],
}


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


def month_key(date_str):
    if not date_str or date_str == "Unknown Date":
        return "Unknown Month"
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m")
    except Exception:
        return "Unknown Month"


def categorize_transaction(text):
    low = (text or "").lower()
    for category, terms in CATEGORY_RULES.items():
        if any(t in low for t in terms):
            return category
    return "Other"


def to_date_obj(date_str):
    if not date_str or date_str == "Unknown Date":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None


def parse_date_input(txt):
    txt = (txt or "").strip()
    if not txt:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(txt, fmt).date()
        except ValueError:
            continue
    return None


def log_error(err):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().isoformat(timespec='seconds')}] {err}\n")
            f.write(traceback.format_exc())
            f.write("\n")
    except Exception:
        pass


def detect_bank_format_from_text(sample_text):
    low = (sample_text or "").lower()
    best_bank = "Unknown"
    best_score = 0
    for bank, hints in BANK_HINTS.items():
        score = sum(1 for h in hints if h in low)
        if score > best_score:
            best_bank = bank
            best_score = score
    if best_score == 0:
        return "Unknown", "Generic", "low"
    confidence = "high" if best_score >= 2 else "medium"
    return best_bank, f"{best_bank}-like", confidence


def extract_text_with_ocr(page):
    if pytesseract is None:
        return ""
    try:
        img = page.to_image(resolution=220).original
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""


def parse_sales_csv(file_path):
    total_sales = 0.0
    monthly_sales = defaultdict(float)
    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    last_err = None
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    continue
                amount_col = guess_column(reader.fieldnames, ["amount", "sale", "value", "total", "net"])
                date_col = guess_column(reader.fieldnames, ["date", "txn date", "invoice date"])
                if not amount_col:
                    raise ValueError("Sales CSV me amount column nahi mila.")
                for row in reader:
                    amt = clean_amount(row.get(amount_col, ""))
                    if amt <= 0:
                        continue
                    total_sales += amt
                    d = normalize_date(row.get(date_col, "")) if date_col else None
                    monthly_sales[month_key(d or "Unknown Date")] += amt
            return total_sales, dict(monthly_sales)
        except Exception as e:
            last_err = e
    raise ValueError(f"Sales CSV parse failed: {last_err}")


def detect_file_source(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext == ".csv":
        for enc in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    sample = f.read(5000)
                return detect_bank_format_from_text(sample)
            except Exception:
                continue
        return "Unknown", "CSV", "low"
    if ext == ".pdf" and pdfplumber is not None:
        try:
            with pdfplumber.open(path) as pdf:
                sample = "\n".join((pdf.pages[i].extract_text() or "") for i in range(min(2, len(pdf.pages))))
            bank, fmt, conf = detect_bank_format_from_text(sample)
            return bank, f"{fmt} PDF", conf
        except Exception:
            return "Unknown", "PDF", "low"
    return "Unknown", "Generic", "low"


def init_day_bucket():
    return {"debit": 0.0, "credit": 0.0, "count": 0}


def load_state():
    default_state = {
        "used_tries": 0,
        "paid_unlocked": False,
        "language": "EN",
        "interstate": False,
        "profiles": {
            "Default": {
                "gst_rate": "18",
                "add_pct": "0",
                "add_fixed": "0",
                "tax_basis": "Net Credit",
                "interstate": False,
            }
        },
        "current_profile": "Default",
    }
    if not STATE_FILE.exists():
        return default_state
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(default_state)
        merged["used_tries"] = int(data.get("used_tries", 0))
        merged["paid_unlocked"] = bool(data.get("paid_unlocked", False))
        merged["language"] = str(data.get("language", "EN")).upper()
        merged["interstate"] = bool(data.get("interstate", False))
        profiles = data.get("profiles")
        if isinstance(profiles, dict) and profiles:
            merged["profiles"] = profiles
        merged["current_profile"] = str(data.get("current_profile", "Default"))
        if merged["current_profile"] not in merged["profiles"]:
            merged["current_profile"] = "Default"
        return merged
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
    transactions = []

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
                desc_col = guess_column(reader.fieldnames, ["description", "narration", "remarks", "particular", "details", "note"])

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
                    description = str(row.get(desc_col, "")).strip() if desc_col else ""
                    tx_type = "Debit" if d > c else "Credit"
                    amount = d if d > 0 else c
                    transactions.append(
                        {
                            "date": tx_date,
                            "debit": d,
                            "credit": c,
                            "amount": amount,
                            "type": tx_type,
                            "description": description,
                            "category": categorize_transaction(description),
                        }
                    )

            return total_debit, total_credit, rows_count, dict(daily), transactions
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
    transactions = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.splitlines()
            if not lines:
                ocr_text = extract_text_with_ocr(page)
                lines = ocr_text.splitlines()

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
                    transactions.append(
                        {
                            "date": tx_date,
                            "debit": amt,
                            "credit": 0.0,
                            "amount": amt,
                            "type": "Debit",
                            "description": line.strip(),
                            "category": categorize_transaction(line),
                        }
                    )
                elif is_credit and not is_debit:
                    total_credit += amt
                    rows_count += 1
                    daily[tx_date]["credit"] += amt
                    daily[tx_date]["count"] += 1
                    transactions.append(
                        {
                            "date": tx_date,
                            "debit": 0.0,
                            "credit": amt,
                            "amount": amt,
                            "type": "Credit",
                            "description": line.strip(),
                            "category": categorize_transaction(line),
                        }
                    )
                else:
                    # Ambiguous lines skip
                    pass

    return total_debit, total_credit, rows_count, dict(daily), transactions


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


def gst_split(gst_amount, interstate=False):
    if interstate:
        return 0.0, 0.0, gst_amount
    half = gst_amount / 2.0
    return half, half, 0.0


def filter_transactions(transactions, from_date=None, to_date=None):
    out = []
    for tx in transactions:
        d = to_date_obj(tx.get("date"))
        if from_date and (d is None or d < from_date):
            continue
        if to_date and (d is None or d > to_date):
            continue
        out.append(tx)
    return out


def summarize_transactions(transactions):
    total_debit = 0.0
    total_credit = 0.0
    daily = defaultdict(init_day_bucket)
    monthly = defaultdict(lambda: {"debit": 0.0, "credit": 0.0, "count": 0})
    categories = defaultdict(float)
    for tx in transactions:
        d = float(tx.get("debit", 0.0))
        c = float(tx.get("credit", 0.0))
        day = tx.get("date") or "Unknown Date"
        mon = month_key(day)
        cat = tx.get("category") or "Other"
        total_debit += d
        total_credit += c
        daily[day]["debit"] += d
        daily[day]["credit"] += c
        daily[day]["count"] += 1
        monthly[mon]["debit"] += d
        monthly[mon]["credit"] += c
        monthly[mon]["count"] += 1
        categories[cat] += d + c
    return total_debit, total_credit, dict(daily), dict(monthly), dict(categories)


def detect_duplicates(transactions):
    seen = defaultdict(list)
    for i, tx in enumerate(transactions):
        sig = (
            tx.get("date"),
            round(float(tx.get("amount", 0.0)), 2),
            tx.get("type"),
            (tx.get("description") or "").strip().lower(),
        )
        seen[sig].append(i)
    out = []
    for idxs in seen.values():
        if len(idxs) > 1:
            for idx in idxs:
                out.append(transactions[idx])
    return out


def detect_suspicious(transactions):
    alerts = []
    high_value = 100000.0
    for tx in transactions:
        amt = float(tx.get("amount", 0.0))
        desc = (tx.get("description") or "").lower()
        if amt >= high_value:
            alerts.append(f"High-value txn: {tx.get('date')} {money(amt)} ({tx.get('type')})")
        if "cash" in desc and amt >= 20000:
            alerts.append(f"Large cash-related txn: {tx.get('date')} {money(amt)}")

    # Round-trip heuristic: same day equal debit & credit
    by_day_type_amt = defaultdict(int)
    for tx in transactions:
        key = (tx.get("date"), tx.get("type"), round(float(tx.get("amount", 0.0)), 2))
        by_day_type_amt[key] += 1
    for (day, tx_type, amt), count in list(by_day_type_amt.items()):
        other = "Credit" if tx_type == "Debit" else "Debit"
        if by_day_type_amt.get((day, other, amt), 0) > 0 and count > 0:
            alerts.append(f"Round-trip pattern on {day} for {money(amt)}")
    return sorted(set(alerts))


def money(x):
    return f"₹ {x:,.2f}"


def is_android_runtime():
    return sys.platform == "android" or "ANDROID_ARGUMENT" in os.environ


def run_cli_mode():
    print(f"\n{APP_TITLE} - CLI Mode (Android/Terminal)\n")
    print("Note: Desktop GUI tkinter Android par supported nahi hai.")
    print("Yahaan file path dekar analysis chala sakte ho.\n")

    while True:
        path = input("Statement file path (.csv/.pdf) [or 'exit']: ").strip().strip('"')
        if path.lower() in {"exit", "quit"}:
            print("Bye.")
            return
        if not path or not Path(path).exists():
            print("Invalid path. Dubara try karo.\n")
            continue

        gst_rate = clean_amount(input("GST % (default 18): ").strip() or "18")
        add_pct = clean_amount(input("Additional % (default 0): ").strip() or "0")
        add_fixed = clean_amount(input("Additional Fixed (default 0): ").strip() or "0")
        basis_in = (input("Tax basis [Credit/Debit/Net Credit] (default Net Credit): ").strip() or "Net Credit")
        basis = basis_in if basis_in in {"Credit", "Debit", "Net Credit"} else "Net Credit"

        try:
            ext = Path(path).suffix.lower()
            if ext == ".csv":
                d, c, r, daily, _txns = parse_csv_statement(path)
            elif ext == ".pdf":
                d, c, r, daily, _txns = parse_pdf_statement(path)
            else:
                print("Sirf CSV/PDF supported hai.\n")
                continue

            taxable, gst, additional, total_payable = calculate_tax(d, c, gst_rate, add_pct, add_fixed, basis)
            print("\n----- RESULT -----")
            print(f"Transactions Parsed: {r}")
            print(f"Total Debit: {money(d)}")
            print(f"Total Credit: {money(c)}")
            print(f"Tax Basis: {basis}")
            print(f"Taxable Amount: {money(taxable)}")
            print(f"GST: {money(gst)}")
            print(f"Additional: {money(additional)}")
            print(f"Total Payable: {money(total_payable)}")
            print(f"Net Balance: {money(c - d)}")
            print("\nPer-Day Summary:")
            ordered_dates = sorted(daily.keys(), key=lambda x: (x == "Unknown Date", x))
            for day in ordered_dates:
                day_d = daily[day]["debit"]
                day_c = daily[day]["credit"]
                day_taxable, day_gst, day_additional, day_total = calculate_tax(
                    day_d, day_c, gst_rate, add_pct, add_fixed, basis
                )
                print(
                    f"- {day}: count={daily[day]['count']}, debit={money(day_d)}, "
                    f"credit={money(day_c)}, taxable={money(day_taxable)}, "
                    f"gst={money(day_gst)}, add={money(day_additional)}, total={money(day_total)}"
                )
            print("------------------\n")
        except Exception as e:
            print(f"Error: {e}\n")


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
        self.monthly_summary = {}
        self.category_summary = {}
        self.transactions = []
        self.filtered_transactions = []
        self.duplicates = []
        self.alerts = []
        self.detected_bank = "Unknown"
        self.detected_format = "Generic"
        self.detected_confidence = "low"
        self.sales_total = 0.0
        self.sales_monthly = {}
        self.reco_gap = 0.0
        self.state = load_state()
        self.used_tries = max(0, int(self.state.get("used_tries", 0)))
        self.paid_unlocked = bool(self.state.get("paid_unlocked", False))
        self.qr_img = None

        self.gst_rate = tk.StringVar(value="18")
        self.add_pct = tk.StringVar(value="0")
        self.add_fixed = tk.StringVar(value="0")
        self.tax_basis = tk.StringVar(value="Net Credit")
        self.from_date = tk.StringVar(value="")
        self.to_date = tk.StringVar(value="")
        self.sales_file = tk.StringVar(value="")
        self.language = tk.StringVar(value=self.state.get("language", "EN"))
        self.interstate = tk.BooleanVar(value=bool(self.state.get("interstate", False)))
        self.profile_name = tk.StringVar(value=self.state.get("current_profile", "Default"))

        self._load_profile_values()

        self._build_ui()
        self._refresh_access_state()
        if self._is_locked():
            self.after(150, self.show_payment_popup)

    def _load_profile_values(self):
        profiles = self.state.get("profiles", {})
        current = self.profile_name.get()
        p = profiles.get(current, profiles.get("Default", {}))
        if not p:
            return
        self.gst_rate.set(str(p.get("gst_rate", "18")))
        self.add_pct.set(str(p.get("add_pct", "0")))
        self.add_fixed.set(str(p.get("add_fixed", "0")))
        self.tax_basis.set(str(p.get("tax_basis", "Net Credit")))
        self.interstate.set(bool(p.get("interstate", False)))

    def save_current_profile(self):
        name = self.profile_name.get().strip() or "Default"
        profiles = self.state.setdefault("profiles", {})
        profiles[name] = {
            "gst_rate": self.gst_rate.get().strip() or "18",
            "add_pct": self.add_pct.get().strip() or "0",
            "add_fixed": self.add_fixed.get().strip() or "0",
            "tax_basis": self.tax_basis.get(),
            "interstate": bool(self.interstate.get()),
        }
        self.state["current_profile"] = name
        self.profile_name.set(name)
        self.profile_combo.config(values=sorted(profiles.keys()))
        self._persist_state()
        messagebox.showinfo("Saved", f"Profile saved: {name}")

    def apply_profile(self, _event=None):
        self._load_profile_values()
        self.state["current_profile"] = self.profile_name.get()
        self._persist_state()

    def change_language(self, _event=None):
        self.state["language"] = self.language.get().strip().upper() or "EN"
        self._persist_state()
        self.status.set("Language updated. Labels remain mostly English/Hinglish.")

    def open_log_file(self):
        if LOG_FILE.exists():
            webbrowser.open(str(LOG_FILE))
        else:
            messagebox.showinfo("Logs", "Abhi tak error logs nahi bane.")

    def check_updates(self):
        try:
            with urlopen(VERSION_URL, timeout=5) as r:
                latest = r.read().decode("utf-8", errors="ignore").strip()
            if not latest:
                raise ValueError("Invalid version response")
            if latest != APP_VERSION:
                if messagebox.askyesno("Update Available", f"Current: {APP_VERSION}\nLatest: {latest}\nDownload now?"):
                    webbrowser.open(DOWNLOAD_LINK)
            else:
                messagebox.showinfo("Up to date", f"Current version {APP_VERSION} latest hai.")
        except Exception as e:
            log_error(e)
            messagebox.showerror("Update Check Failed", str(e))

    def export_json(self):
        if not self.filtered_transactions:
            messagebox.showwarning("Warning", "Pehle Analyze karo.")
            return
        out_path = os.path.join(tempfile.gettempdir(), f"gst_data_{int(datetime.now().timestamp())}.json")
        payload = {
            "version": APP_VERSION,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "rows_count": self.rows_count,
                "total_debit": self.total_debit,
                "total_credit": self.total_credit,
                "detected_bank": self.detected_bank,
                "detected_format": self.detected_format,
                "detect_confidence": self.detected_confidence,
                "daily": self.daily_summary,
                "monthly": self.monthly_summary,
                "categories": self.category_summary,
                "duplicates_count": len(self.duplicates),
                "alerts": self.alerts,
                "sales_total": self.sales_total,
                "reconciliation_gap": self.reco_gap,
            },
            "transactions": self.filtered_transactions,
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        webbrowser.open(out_path)
        self.status.set(f"JSON export generated: {out_path}")

    def export_csv(self):
        if not self.filtered_transactions:
            messagebox.showwarning("Warning", "Pehle Analyze karo.")
            return
        out_path = os.path.join(tempfile.gettempdir(), f"gst_transactions_{int(datetime.now().timestamp())}.csv")
        fields = ["date", "type", "amount", "debit", "credit", "category", "description"]
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for tx in self.filtered_transactions:
                w.writerow({k: tx.get(k, "") for k in fields})
        webbrowser.open(out_path)
        self.status.set(f"CSV export generated: {out_path}")

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Statement File (CSV/PDF):").grid(row=0, column=0, sticky="w")
        self.file_entry = ttk.Entry(top, width=78)
        self.file_entry.grid(row=0, column=1, padx=8, sticky="we")
        ttk.Button(top, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=4)

        ttk.Label(top, text="Profile").grid(row=1, column=0, sticky="w", pady=(8, 0))
        profiles = sorted(self.state.get("profiles", {}).keys())
        self.profile_combo = ttk.Combobox(top, textvariable=self.profile_name, values=profiles, state="readonly", width=30)
        self.profile_combo.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self.profile_combo.bind("<<ComboboxSelected>>", self.apply_profile)
        ttk.Button(top, text="Save Profile", command=self.save_current_profile).grid(row=1, column=2, padx=4, pady=(8, 0))

        ttk.Label(top, text="Sales CSV (Reconciliation)").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(top, textvariable=self.sales_file, width=78).grid(row=2, column=1, padx=8, sticky="we", pady=(8, 0))
        ttk.Button(top, text="Browse Sales", command=self.browse_sales_file).grid(row=2, column=2, padx=4, pady=(8, 0))

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

        ttk.Label(settings, text="From Date (YYYY-MM-DD)").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(settings, textvariable=self.from_date, width=18).grid(row=1, column=1, padx=8, pady=(8, 0))
        ttk.Label(settings, text="To Date (YYYY-MM-DD)").grid(row=1, column=2, sticky="w", pady=(8, 0))
        ttk.Entry(settings, textvariable=self.to_date, width=18).grid(row=1, column=3, padx=8, pady=(8, 0))
        ttk.Checkbutton(settings, text="Interstate (IGST)", variable=self.interstate).grid(row=1, column=4, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(settings, text="Language").grid(row=1, column=6, sticky="w", pady=(8, 0))
        lang_box = ttk.Combobox(settings, textvariable=self.language, values=["EN", "HI"], state="readonly", width=14)
        lang_box.grid(row=1, column=7, padx=8, pady=(8, 0))
        lang_box.bind("<<ComboboxSelected>>", self.change_language)

        btns = ttk.Frame(self, padding=(12, 2))
        btns.pack(fill="x")
        self.analyze_btn = ttk.Button(btns, text="Analyze", command=self.analyze)
        self.analyze_btn.pack(side="left", padx=4)
        self.report_btn = ttk.Button(btns, text="Generate HTML Report", command=self.generate_html_report)
        self.report_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Export CSV", command=self.export_csv).pack(side="left", padx=4)
        ttk.Button(btns, text="Export JSON", command=self.export_json).pack(side="left", padx=4)
        ttk.Button(btns, text="Check Updates", command=self.check_updates).pack(side="left", padx=4)
        ttk.Button(btns, text="Open Logs", command=self.open_log_file).pack(side="left", padx=4)
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
        self.state["language"] = self.language.get().strip().upper() or "EN"
        self.state["interstate"] = bool(self.interstate.get())
        self.state["current_profile"] = self.profile_name.get().strip() or "Default"
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

    def browse_sales_file(self):
        path = filedialog.askopenfilename(
            title="Select Sales CSV",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self.sales_file.set(path)

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
                _d, _c, _r, _daily, txns = parse_csv_statement(path)
            elif ext == ".pdf":
                _d, _c, _r, _daily, txns = parse_pdf_statement(path)
            else:
                messagebox.showerror("Error", "Sirf CSV/PDF supported hai.")
                return
            self.detected_bank, self.detected_format, self.detected_confidence = detect_file_source(path)

            from_date = parse_date_input(self.from_date.get())
            to_date = parse_date_input(self.to_date.get())
            if self.from_date.get().strip() and from_date is None:
                messagebox.showerror("Error", "From Date invalid hai. Use YYYY-MM-DD.")
                return
            if self.to_date.get().strip() and to_date is None:
                messagebox.showerror("Error", "To Date invalid hai. Use YYYY-MM-DD.")
                return
            if from_date and to_date and from_date > to_date:
                messagebox.showerror("Error", "From Date, To Date se bada nahi ho sakta.")
                return

            self.transactions = txns
            self.filtered_transactions = filter_transactions(txns, from_date, to_date)
            self.rows_count = len(self.filtered_transactions)
            self.total_debit, self.total_credit, self.daily_summary, self.monthly_summary, self.category_summary = summarize_transactions(
                self.filtered_transactions
            )
            self.duplicates = detect_duplicates(self.filtered_transactions)
            self.alerts = detect_suspicious(self.filtered_transactions)
            self.sales_total = 0.0
            self.sales_monthly = {}
            self.reco_gap = 0.0
            sales_path = self.sales_file.get().strip()
            if sales_path:
                if not Path(sales_path).exists():
                    messagebox.showerror("Error", "Sales CSV path invalid hai.")
                    return
                self.sales_total, self.sales_monthly = parse_sales_csv(sales_path)
                self.reco_gap = self.total_credit - self.sales_total

            gst_rate = clean_amount(self.gst_rate.get())
            add_pct = clean_amount(self.add_pct.get())
            add_fixed = clean_amount(self.add_fixed.get())

            taxable, gst, additional, total_payable = calculate_tax(
                self.total_debit, self.total_credit, gst_rate, add_pct, add_fixed, self.tax_basis.get()
            )
            cgst, sgst, igst = gst_split(gst, bool(self.interstate.get()))

            self.tree.delete(*self.tree.get_children())
            rows = [
                ("-", "File", path),
                ("-", "Detected Bank", self.detected_bank),
                ("-", "Detected Format", f"{self.detected_format} ({self.detected_confidence})"),
                ("-", "Transactions Parsed", str(self.rows_count)),
                ("-", "Total Debit / Transfer Out", money(self.total_debit)),
                ("-", "Total Credit / Received", money(self.total_credit)),
                ("-", "Tax Basis", self.tax_basis.get()),
                ("-", "Taxable Amount", money(taxable)),
                ("-", f"GST ({gst_rate:.2f}%)", money(gst)),
                ("-", "CGST", money(cgst)),
                ("-", "SGST", money(sgst)),
                ("-", "IGST", money(igst)),
                ("-", f"Additional Charges ({add_pct:.2f}% + fixed)", money(additional)),
                ("-", "Total Estimated Payable", money(total_payable)),
                ("-", "Net Balance (Credit - Debit)", money(self.total_credit - self.total_debit)),
                ("-", "Duplicates Found", str(len(self.duplicates))),
                ("-", "Suspicious Alerts", str(len(self.alerts))),
            ]
            if sales_path:
                rows.extend(
                    [
                        ("-", "Sales Total (CSV)", money(self.sales_total)),
                        ("-", "Reconciliation Gap (Credit - Sales)", money(self.reco_gap)),
                    ]
                )
            rows.extend(
                [
                    ("-", "", ""),
                    ("-", "Per-Day Breakdown", ""),
                ]
            )
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

            self.tree.insert("", "end", values=("-", "", ""))
            self.tree.insert("", "end", values=("-", "Monthly Summary", ""))
            for mon in sorted(self.monthly_summary.keys()):
                m = self.monthly_summary[mon]
                self.tree.insert("", "end", values=(mon, "Txn Count", str(m["count"])))
                self.tree.insert("", "end", values=(mon, "Debit", money(m["debit"])))
                self.tree.insert("", "end", values=(mon, "Credit", money(m["credit"])))

            self.tree.insert("", "end", values=("-", "", ""))
            self.tree.insert("", "end", values=("-", "Category Summary", ""))
            for cat, amt in sorted(self.category_summary.items(), key=lambda x: x[1], reverse=True):
                self.tree.insert("", "end", values=("-", cat, money(amt)))

            if sales_path:
                self.tree.insert("", "end", values=("-", "", ""))
                self.tree.insert("", "end", values=("-", "Sales Reconciliation (Monthly)", ""))
                for mon in sorted(set(self.monthly_summary.keys()) | set(self.sales_monthly.keys())):
                    credit_amt = self.monthly_summary.get(mon, {}).get("credit", 0.0)
                    sales_amt = self.sales_monthly.get(mon, 0.0)
                    gap = credit_amt - sales_amt
                    self.tree.insert("", "end", values=(mon, "Credit vs Sales", f"{money(credit_amt)} vs {money(sales_amt)} (Gap {money(gap)})"))

            if self.alerts:
                self.tree.insert("", "end", values=("-", "", ""))
                self.tree.insert("", "end", values=("-", "Suspicious Alerts", ""))
                for a in self.alerts[:12]:
                    self.tree.insert("", "end", values=("-", "Alert", a))

            self._consume_try()
            self.status.set("Analysis complete.")
        except Exception as e:
            log_error(e)
            messagebox.showerror("Error", str(e))
            self.status.set("Failed.")

    def generate_html_report(self):
        if self._is_locked():
            self.show_payment_popup()
            return

        if self.rows_count == 0:
            messagebox.showwarning("Warning", "Pehle Analyze karo.")
            return

        gst_rate = clean_amount(self.gst_rate.get())
        add_pct = clean_amount(self.add_pct.get())
        add_fixed = clean_amount(self.add_fixed.get())

        taxable, gst, additional, total_payable = calculate_tax(
            self.total_debit, self.total_credit, gst_rate, add_pct, add_fixed, self.tax_basis.get()
        )
        cgst, sgst, igst = gst_split(gst, bool(self.interstate.get()))

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
    <tr><td>Detected Bank</td><td>{self.detected_bank}</td></tr>
    <tr><td>Detected Format</td><td>{self.detected_format} ({self.detected_confidence})</td></tr>
    <tr><td>Transactions Parsed</td><td>{self.rows_count}</td></tr>
    <tr><td>Total Debit / Transfer Out</td><td>{money(self.total_debit)}</td></tr>
    <tr><td>Total Credit / Received</td><td>{money(self.total_credit)}</td></tr>
    <tr><td>Taxable Amount</td><td>{money(taxable)}</td></tr>
    <tr><td>GST ({gst_rate:.2f}%)</td><td>{money(gst)}</td></tr>
    <tr><td>CGST</td><td>{money(cgst)}</td></tr>
    <tr><td>SGST</td><td>{money(sgst)}</td></tr>
    <tr><td>IGST</td><td>{money(igst)}</td></tr>
    <tr><td>Additional Charges ({add_pct:.2f}% + fixed)</td><td>{money(additional)}</td></tr>
    <tr><td><b>Total Estimated Payable</b></td><td><b>{money(total_payable)}</b></td></tr>
    <tr><td>Net Balance (Credit - Debit)</td><td>{money(self.total_credit - self.total_debit)}</td></tr>
    <tr><td>Sales Total (CSV)</td><td>{money(self.sales_total)}</td></tr>
    <tr><td>Reconciliation Gap (Credit - Sales)</td><td>{money(self.reco_gap)}</td></tr>
    <tr><td>Duplicates Found</td><td>{len(self.duplicates)}</td></tr>
    <tr><td>Suspicious Alerts</td><td>{len(self.alerts)}</td></tr>
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
    if is_android_runtime():
        run_cli_mode()
    else:
        app = App()
        app.mainloop()
