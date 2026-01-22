from pathlib import Path

# Common junk we’ve seen from bad encoding/BOM conversions
JUNK = [
    "\ufeff",            # BOM (U+FEFF)
    "Ã¯Â»Â¿",            # mojibake for BOM
]

def clean_text(s: str) -> str:
    for j in JUNK:
        s = s.replace(j, "")
    # Also remove any stray BOMs not at start
    s = s.replace("\ufeff", "")
    return s

def main(root="app"):
    root = Path(root)
    changed = 0
    for p in root.rglob("*.py"):
        raw = p.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_text(raw)
        if cleaned != raw:
            p.write_text(cleaned, encoding="utf-8", errors="ignore")
            changed += 1
    print(f"cleaned encoding in {changed} file(s)")

if __name__ == "__main__":
    main()
