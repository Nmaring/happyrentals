import os, re, sqlite3, sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND / ".env"

def read_env_db_url():
    if not ENV_PATH.exists():
        return None
    txt = ENV_PATH.read_text(encoding="utf-8", errors="ignore")
    for key in ["DATABASE_URL","SQLALCHEMY_DATABASE_URL","DB_URL"]:
        m = re.search(rf"^{key}\s*=\s*(.+)\s*$", txt, flags=re.M)
        if m:
            v = m.group(1).strip().strip('"').strip("'")
            return v
    return None

def find_sqlite_db_fallback():
    # common names
    cands = [
        BACKEND/"app.db",
        BACKEND/"database.db",
        BACKEND/"db.sqlite3",
        BACKEND/"data.db",
        BACKEND/"happy_rentals.db",
    ]
    for p in cands:
        if p.exists():
            return p
    # last resort: first *.db in backend dir
    for p in BACKEND.rglob("*.db"):
        return p
    return None

def sqlite_cols(conn, table):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def sqlite_has_table(conn, table):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None

def sqlite_add_col(conn, table, col, decl):
    cols = sqlite_cols(conn, table)
    if col in cols:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")

def try_update_units_label(conn):
    if not sqlite_has_table(conn, "units"):
        return
    cols = sqlite_cols(conn, "units")
    # best-effort candidates
    name_col = "name" if "name" in cols else None
    num_col  = "unit_number" if "unit_number" in cols else ("number" if "number" in cols else None)
    label_col = "label" if "label" in cols else None
    if not label_col:
        return

    parts = []
    if name_col: parts.append(f"NULLIF(TRIM({name_col}), '')")
    if num_col:  parts.append(f"NULLIF(TRIM({num_col}), '')")
    parts.append("'Unit ' || id")
    coalesce_expr = "COALESCE(" + ", ".join(parts) + ")"

    conn.execute(f"""
        UPDATE units
        SET label = {coalesce_expr}
        WHERE label IS NULL OR TRIM(label) = ''
    """)

def try_patch_payments(conn):
    if not sqlite_has_table(conn, "payments"):
        return
    cols = sqlite_cols(conn, "payments")

    # ensure columns exist (schema drift mentioned in handoff)
    if "channel" not in cols:
        sqlite_add_col(conn, "payments", "channel", "TEXT NOT NULL DEFAULT 'manual'")
    if "processor" not in cols:
        sqlite_add_col(conn, "payments", "processor", "TEXT NOT NULL DEFAULT 'none'")
    if "external_reference" not in cols:
        sqlite_add_col(conn, "payments", "external_reference", "TEXT")
    if "created_at" not in cols:
        sqlite_add_col(conn, "payments", "created_at", "TEXT")

    # normalize venmo: channel manual -> p2p
    cols = sqlite_cols(conn, "payments")
    if "method" in cols and "channel" in cols:
        conn.execute("""
            UPDATE payments
            SET channel='p2p'
            WHERE LOWER(COALESCE(method,''))='venmo'
              AND LOWER(COALESCE(channel,''))='manual'
        """)

    # processor mapping from method when processor is null/empty/none
    if "method" in cols and "processor" in cols:
        conn.execute("""
            UPDATE payments
            SET processor=LOWER(method)
            WHERE LOWER(COALESCE(method,'')) IN ('venmo','zelle','paypal','stripe')
              AND (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
        """)
        conn.execute("""
            UPDATE payments
            SET processor='ach'
            WHERE LOWER(COALESCE(method,''))='ach'
              AND (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
        """)
        conn.execute("""
            UPDATE payments
            SET processor='check'
            WHERE LOWER(COALESCE(method,''))='check'
              AND (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
        """)
        conn.execute("""
            UPDATE payments
            SET processor='cash'
            WHERE LOWER(COALESCE(method,''))='cash'
              AND (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
        """)

    # sqlite triggers to keep mapping on future inserts/updates
    # (idempotent: drop then create)
    conn.execute("DROP TRIGGER IF EXISTS trg_payments_norm_insert")
    conn.execute("DROP TRIGGER IF EXISTS trg_payments_norm_update")

    conn.execute("""
    CREATE TRIGGER trg_payments_norm_insert
    AFTER INSERT ON payments
    BEGIN
      UPDATE payments
      SET channel = CASE
        WHEN LOWER(COALESCE(method,''))='venmo' AND LOWER(COALESCE(channel,''))='manual' THEN 'p2p'
        ELSE COALESCE(channel,'manual')
      END,
      processor = CASE
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,'')) IN ('venmo','zelle','paypal','stripe')
          THEN LOWER(method)
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='ach'
          THEN 'ach'
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='check'
          THEN 'check'
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='cash'
          THEN 'cash'
        ELSE COALESCE(processor,'none')
      END
      WHERE id = NEW.id;
    END;
    """)

    conn.execute("""
    CREATE TRIGGER trg_payments_norm_update
    AFTER UPDATE OF method, channel, processor ON payments
    BEGIN
      UPDATE payments
      SET channel = CASE
        WHEN LOWER(COALESCE(method,''))='venmo' AND LOWER(COALESCE(channel,''))='manual' THEN 'p2p'
        ELSE COALESCE(channel,'manual')
      END,
      processor = CASE
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,'')) IN ('venmo','zelle','paypal','stripe')
          THEN LOWER(method)
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='ach'
          THEN 'ach'
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='check'
          THEN 'check'
        WHEN (processor IS NULL OR TRIM(processor)='' OR LOWER(processor)='none')
             AND LOWER(COALESCE(method,''))='cash'
          THEN 'cash'
        ELSE COALESCE(processor,'none')
      END
      WHERE id = NEW.id;
    END;
    """)

def try_patch_leases(conn):
    if not sqlite_has_table(conn, "leases"):
        return
    cols = sqlite_cols(conn, "leases")

    # lease builder options columns
    if "lease_type" not in cols:
        sqlite_add_col(conn, "leases", "lease_type", "TEXT NOT NULL DEFAULT 'fixed_term'")
    if "state" not in cols:
        sqlite_add_col(conn, "leases", "state", "TEXT")
    if "rent_due_day" not in cols:
        sqlite_add_col(conn, "leases", "rent_due_day", "INTEGER NOT NULL DEFAULT 1")
    if "late_fee_type" not in cols:
        sqlite_add_col(conn, "leases", "late_fee_type", "TEXT NOT NULL DEFAULT 'none'")
    if "late_fee_value" not in cols:
        sqlite_add_col(conn, "leases", "late_fee_value", "REAL NOT NULL DEFAULT 0")

    # optional rent_amount if not present
    cols = sqlite_cols(conn, "leases")
    if "rent_amount" not in cols and "rent" not in cols:
        sqlite_add_col(conn, "leases", "rent_amount", "REAL NOT NULL DEFAULT 0")

def main():
    db_url = read_env_db_url()
    if db_url and db_url.startswith("sqlite"):
        # sqlite:///C:/path/to/db
        m = re.match(r"sqlite:(///)?(.+)$", db_url)
        if not m:
            print("Could not parse sqlite url:", db_url)
            sys.exit(2)
        db_path = m.group(2)
        db_path = db_path.replace("\\\\", "\\")
        p = Path(db_path)
        if not p.exists():
            # relative to backend
            p2 = (BACKEND / db_path).resolve()
            if p2.exists():
                p = p2
        if not p.exists():
            print("SQLite DB not found at:", p)
            sys.exit(2)
        conn = sqlite3.connect(str(p))
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            try_update_units_label(conn)
            try_patch_payments(conn)
            try_patch_leases(conn)
            conn.commit()
            print("OK sqlite patch:", p)
        finally:
            conn.close()
        return

    # fallback: try find sqlite db by scanning
    p = find_sqlite_db_fallback()
    if p and p.exists():
        conn = sqlite3.connect(str(p))
        try:
            conn.execute("PRAGMA foreign_keys=ON")
            try_update_units_label(conn)
            try_patch_payments(conn)
            try_patch_leases(conn)
            conn.commit()
            print("OK sqlite fallback patch:", p)
        finally:
            conn.close()
        return

    print("No sqlite DB detected; set DATABASE_URL in backend/.env for non-sqlite and re-run.")
    sys.exit(3)

if __name__ == "__main__":
    main()
