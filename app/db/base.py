"""Aggregated metadata: importing this module registers every model on Base.

Use this (not ``base_class``) wherever full metadata is needed — table
creation at startup and Alembic autogeneration.
"""
from app.db.base_class import Base  # noqa: F401
import app.models  # noqa: F401  (populates Base.metadata)
