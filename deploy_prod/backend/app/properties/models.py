from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, DateTime
from datetime import datetime
# backend/app/properties/models.py
import importlib
from sqlalchemy import Column, Integer, String, Text


def _import_attr(module_candidates: list[str], attr: str):
    """
    Try multiple likely modules and return the first matching attribute.
    This avoids guessing your project's exact db module layout.
    """
    last_err = None
    for modname in module_candidates:
        try:
            mod = importlib.import_module(modname)
            if hasattr(mod, attr):
                return getattr(mod, attr)
        except Exception as e:  # keep trying
            last_err = e
            continue
    raise ImportError(f"Could not import '{attr}' from any of: {module_candidates}. Last error: {last_err}")


# Find your SQLAlchemy Base in common locations
Base = _import_attr(
    [
        "app.db",
        "app.database",
        "app.db.base",
        "app.db.database",
        "app.core.db",
        "app.core.database",
    ],
    "Base",
)


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)

    # Local single-user mode default; DB enforces NOT NULL
    owner_user_id = Column(Integer, nullable=False, default=1)

    name = Column(String(255), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(20), nullable=False)
    zip = Column(String(20), nullable=False)

    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


