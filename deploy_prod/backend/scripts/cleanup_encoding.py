from pathlib import Path

def clean_text(raw: bytes) -> str:
    # remove UTF-8 BOM if present
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    # decode
    txt = raw.decode("utf-8", errors="ignore")
    # remove any stray FEFF anywhere
    txt = txt.replace("\ufeff", "")
    return txt

def main():
    root = Path("app")
    changed = 0
    for p in root.rglob("*.py"):
        raw = p.read_bytes()
        txt = clean_text(raw)
        # normalize newlines minimally
        p.write_text(txt, encoding="utf-8", newline="\n")
        changed += 1
    print(f"cleaned encoding in {changed} python file(s)")

if __name__ == "__main__":
    main()
