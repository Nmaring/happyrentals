from sqlalchemy import text
from app.db_compat import engine

def has_col(conn, table, col):
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(r[1] == col for r in rows)

def add_col_if_missing(conn, table, col, ddl):
    if not has_col(conn, table, col):
        print(f"ADD COLUMN {table}.{col}: {ddl}")
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
    else:
        print(f"OK {table}.{col} exists")

def main():
    with engine.begin() as conn:
        # ---- units ----
        # ensure label exists too (in case)
        add_col_if_missing(conn, "units", "label",  "label VARCHAR(64)")
        add_col_if_missing(conn, "units", "bedrooms", "bedrooms INTEGER")
        add_col_if_missing(conn, "units", "bathrooms", "bathrooms NUMERIC(10,2)")
        add_col_if_missing(conn, "units", "sqft", "sqft INTEGER")
        add_col_if_missing(conn, "units", "rent", "rent NUMERIC(12,2)")
        add_col_if_missing(conn, "units", "status", "status VARCHAR(32)")  # <-- your error
        add_col_if_missing(conn, "units", "notes", "notes TEXT")

        # backfill
        conn.execute(text("""
            UPDATE units
            SET label = COALESCE(NULLIF(TRIM(label), ''), 'Unit ' || id)
            WHERE label IS NULL OR TRIM(label) = ''
        """))
        conn.execute(text("""
            UPDATE units
            SET status = COALESCE(NULLIF(TRIM(status), ''), 'vacant')
            WHERE status IS NULL OR TRIM(status) = ''
        """))

        # ---- leases ----
        add_col_if_missing(conn, "leases", "state", "state VARCHAR(2)")  # <-- your error
        add_col_if_missing(conn, "leases", "lease_type", "lease_type VARCHAR(32)")
        add_col_if_missing(conn, "leases", "term_months", "term_months INTEGER")
        add_col_if_missing(conn, "leases", "security_deposit", "security_deposit NUMERIC(12,2)")
        add_col_if_missing(conn, "leases", "rent_due_day", "rent_due_day INTEGER")
        add_col_if_missing(conn, "leases", "clauses_json", "clauses_json TEXT")

        # backfill defaults
        conn.execute(text("""
            UPDATE leases
            SET state = COALESCE(NULLIF(TRIM(state), ''), 'MN')
            WHERE state IS NULL OR TRIM(state) = ''
        """))
        conn.execute(text("""
            UPDATE leases
            SET lease_type = COALESCE(NULLIF(TRIM(lease_type), ''), 'fixed_term')
            WHERE lease_type IS NULL OR TRIM(lease_type) = ''
        """))
        conn.execute(text("""
            UPDATE leases
            SET rent_due_day = COALESCE(rent_due_day, 1)
            WHERE rent_due_day IS NULL
        """))

    print("DONE")

if __name__ == "__main__":
    main()
