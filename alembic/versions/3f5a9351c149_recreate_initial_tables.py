"""Recreate initial tables

Revision ID: 3f5a9351c149
Revises: 
Create Date: 2025-03-17 15:06:54.376268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Import the model metadata so we can materialize the full schema from the ORM
# definitions. This keeps the initial migration in lockstep with the models.
from app.db.base import Base
import app.models  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = '3f5a9351c149'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables defined by the ORM models."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Drop all tables defined by the ORM models."""
    Base.metadata.drop_all(bind=op.get_bind())
