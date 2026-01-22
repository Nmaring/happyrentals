"""
Compatibility shim.

We keep all models in app/models.py as the single source of truth.
Some auth code imports User from app.models_user, so this file re-exports it.
"""

from app.models import User  # noqa: F401
