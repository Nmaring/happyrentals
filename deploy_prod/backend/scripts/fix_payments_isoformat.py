from pathlib import Path
import re

def patch_file(p: Path) -> bool:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    orig = txt

    # 1) payment_date.isoformat()
    txt = re.sub(
        r'\bpayment_date\.isoformat\(\)',
        '(payment_date.isoformat() if hasattr(payment_date, "isoformat") else str(payment_date))',
        txt
    )

    # 2) something.payment_date.isoformat()
    txt = re.sub(
        r'(\b\w+\b)\.payment_date\.isoformat\(\)',
        r'(\1.payment_date.isoformat() if hasattr(\1.payment_date, "isoformat") else str(\1.payment_date))',
        txt
    )

    if txt != orig:
        p.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    changed = 0
    for p in Path("app/payments").rglob("*.py"):
        if patch_file(p):
            changed += 1
    print(f"patched {changed} file(s) in app/payments")

if __name__ == "__main__":
    main()
