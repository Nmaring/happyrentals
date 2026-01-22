from pathlib import Path
import re

def fix_file(p: Path):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "from __future__ import annotations" not in txt:
        return False

    lines = txt.splitlines(True)
    # remove all occurrences
    lines = [ln for ln in lines if ln.strip() != "from __future__ import annotations"]

    # Find insertion point: after shebang/encoding + optional module docstring
    i = 0
    if lines and lines[0].startswith("#!"):
        i = 1
    if i < len(lines) and re.match(r"^#.*coding[:=]\s*[-\w.]+", lines[i]):
        i += 1

    # If next non-empty token is a module docstring, insert after it
    # Detect triple-quote start at first non-empty line
    j = i
    while j < len(lines) and lines[j].strip() == "":
        j += 1

    if j < len(lines) and re.match(r'^[uUrR]?(\"\"\"|\'\'\')', lines[j].lstrip()):
        quote = '"""' if '"""' in lines[j] else "'''"
        j += 1
        while j < len(lines) and quote not in lines[j]:
            j += 1
        if j < len(lines):
            j += 1  # include closing docstring line
        insert_at = j
    else:
        insert_at = i

    lines.insert(insert_at, "from __future__ import annotations\n")
    p.write_text("".join(lines), encoding="utf-8")
    return True

def main(root="app"):
    root = Path(root)
    changed = 0
    for p in root.rglob("*.py"):
        if fix_file(p):
            changed += 1
    print(f"fixed future imports in {changed} file(s)")

if __name__ == "__main__":
    main()
