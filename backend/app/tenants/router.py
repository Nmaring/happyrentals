# backend/app/tenants/router.py
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import MetaData, Table, select, insert, update, delete, text
from sqlalchemy.orm import Session

from . import schemas


# --- DB imports (robust) ---
try:
    from app.db import get_db, engine  # type: ignore
except Exception:
    from app.db import get_db  # type: ignore
    try:
        from app.db import get_engine  # type: ignore

        engine = get_engine()
    except Exception as e:
        raise RuntimeError("Could not import DB engine from app.db") from e


router = APIRouter(prefix="/tenants", tags=["tenants"])

_migrated = False


def _pragma_table_info(db: Session, table_name: str):
    return db.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()


def _migrate_tenants_if_needed(db: Session):
    """
    Fix legacy schema where tenants.unit_id is NOT NULL (breaks POST /tenants),
    by recreating tenants table without the required unit_id constraint.
    """
    global _migrated
    if _migrated:
        return

    cols = _pragma_table_info(db, "tenants")
    if not cols:
        _migrated = True
        return

    col_names = {c["name"] for c in cols}
    unit_col = next((c for c in cols if c["name"] == "unit_id"), None)

    if unit_col and int(unit_col.get("notnull", 0)) == 1:
        # Create a new tenants table with a flexible schema the app expects.
        db.execute(text("BEGIN"))

        db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tenants__new (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    notes TEXT
                )
                """
            )
        )

        # Copy what we can from old schema
        select_parts = []
        insert_cols = []

        # id
        if "id" in col_names:
            insert_cols.append("id")
            select_parts.append("id")

        # name columns
        if "first_name" in col_names:
            insert_cols.append("first_name")
            select_parts.append("first_name")
        else:
            insert_cols.append("first_name")
            select_parts.append("NULL as first_name")

        if "last_name" in col_names:
            insert_cols.append("last_name")
            select_parts.append("last_name")
        else:
            insert_cols.append("last_name")
            select_parts.append("NULL as last_name")

        if "full_name" in col_names:
            insert_cols.append("full_name")
            select_parts.append("full_name")
        else:
            insert_cols.append("full_name")
            select_parts.append("NULL as full_name")

        for f in ("email", "phone", "notes"):
            insert_cols.append(f)
            if f in col_names:
                select_parts.append(f)
            else:
                select_parts.append(f"NULL as {f}")

        db.execute(
            text(
                f"""
                INSERT INTO tenants__new ({", ".join(insert_cols)})
                SELECT {", ".join(select_parts)} FROM tenants
                """
            )
        )

        db.execute(text("DROP TABLE tenants"))
        db.execute(text("ALTER TABLE tenants__new RENAME TO tenants"))
        db.execute(text("COMMIT"))

    _migrated = True


def _reflect_tenants_table() -> Table:
    md = MetaData()
    return Table("tenants", md, autoload_with=engine)


def _pk_col(t: Table):
    if t.primary_key and len(t.primary_key.columns) > 0:
        return list(t.primary_key.columns)[0]
    for name in ("id", "tenant_id", "pk"):
        if name in t.c:
            return t.c[name]
    cols = list(t.c)
    if not cols:
        raise RuntimeError("Tenants table has no columns (reflection failed).")
    return cols[0]


def _row_to_tenant_out(t: Table, row) -> Dict[str, Any]:
    m = dict(row._mapping)
    pk = _pk_col(t).name
    if "id" not in m and pk in m:
        m["id"] = m[pk]

    # Support either schema:
    # - first_name/last_name columns
    # - OR full_name column
    first = m.get("first_name")
    last = m.get("last_name")
    full = m.get("full_name")

    if (not full) and (first or last):
        full = f"{first or ''} {last or ''}".strip()

    return {
        "id": m.get("id"),
        "first_name": first or "",
        "last_name": last or "",
        "email": m.get("email"),
        "phone": m.get("phone"),
        "notes": m.get("notes"),
    }


@router.get("", response_model=List[schemas.TenantOut])
def list_tenants(db: Session = Depends(get_db)):
    _migrate_tenants_if_needed(db)
    t = _reflect_tenants_table()

    # IMPORTANT: always select actual columns (prevents "SELECT FROM tenants" bug)
    stmt = select(*t.c).order_by(_pk_col(t).desc())
    rows = db.execute(stmt).fetchall()
    return [_row_to_tenant_out(t, r) for r in rows]


@router.get("/{tenant_id}", response_model=schemas.TenantOut)
def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    _migrate_tenants_if_needed(db)
    t = _reflect_tenants_table()
    pk = _pk_col(t)

    row = db.execute(select(*t.c).where(pk == tenant_id)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return _row_to_tenant_out(t, row)


@router.post("", response_model=schemas.TenantOut)
def create_tenant(payload: schemas.TenantCreate, db: Session = Depends(get_db)):
    _migrate_tenants_if_needed(db)
    t = _reflect_tenants_table()

    data = payload.model_dump()
    values: Dict[str, Any] = {}

    # Write whatever columns exist
    if "first_name" in t.c:
        values["first_name"] = data.get("first_name") or ""
    if "last_name" in t.c:
        values["last_name"] = data.get("last_name") or ""

    full_name = (f"{data.get('first_name') or ''} {data.get('last_name') or ''}").strip()
    if "full_name" in t.c:
        values["full_name"] = full_name

    for f in ("email", "phone", "notes"):
        if f in t.c:
            values[f] = data.get(f)

    res = db.execute(insert(t).values(**values))
    db.commit()

    pk = _pk_col(t)
    new_id = res.inserted_primary_key[0] if res.inserted_primary_key else None
    if new_id is None:
        row = db.execute(select(*t.c).order_by(pk.desc())).fetchone()
    else:
        row = db.execute(select(*t.c).where(pk == new_id)).fetchone()

    if not row:
        raise HTTPException(status_code=500, detail="Failed to read created tenant")
    return _row_to_tenant_out(t, row)


@router.put("/{tenant_id}", response_model=schemas.TenantOut)
def update_tenant(tenant_id: int, payload: schemas.TenantUpdate, db: Session = Depends(get_db)):
    _migrate_tenants_if_needed(db)
    t = _reflect_tenants_table()
    pk = _pk_col(t)

    patch = payload.model_dump(exclude_unset=True)
    values: Dict[str, Any] = {}

    if "first_name" in patch and "first_name" in t.c:
        values["first_name"] = patch["first_name"]
    if "last_name" in patch and "last_name" in t.c:
        values["last_name"] = patch["last_name"]

    if "full_name" in t.c and ("first_name" in patch or "last_name" in patch):
        fn = patch.get("first_name") or ""
        ln = patch.get("last_name") or ""
        values["full_name"] = f"{fn} {ln}".strip()

    for f in ("email", "phone", "notes"):
        if f in patch and f in t.c:
            values[f] = patch[f]

    if not values:
        row = db.execute(select(*t.c).where(pk == tenant_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")
        return _row_to_tenant_out(t, row)

    res = db.execute(update(t).where(pk == tenant_id).values(**values))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")

    row = db.execute(select(*t.c).where(pk == tenant_id)).fetchone()
    return _row_to_tenant_out(t, row)


@router.delete("/{tenant_id}")
def delete_tenant(tenant_id: int, db: Session = Depends(get_db)):
    _migrate_tenants_if_needed(db)
    t = _reflect_tenants_table()
    pk = _pk_col(t)

    res = db.execute(delete(t).where(pk == tenant_id))
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"ok": True}
