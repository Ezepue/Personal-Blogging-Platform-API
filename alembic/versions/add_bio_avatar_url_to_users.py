"""add bio and avatar_url to users

Revision ID: a1b2c3d4e5f6
Revises: 3f5a9351c149
Create Date: 2026-03-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = '3f5a9351c149'
branch_labels = None
depends_on = None


def _existing_columns(table: str):
    inspector = sa.inspect(op.get_bind())
    return {col["name"] for col in inspector.get_columns(table)}


def upgrade() -> None:
    # Idempotent: the base migration already creates these columns from the ORM
    # models on a fresh database. Only add whatever is genuinely missing (e.g. when
    # upgrading an older database whose base schema predates these columns).
    existing = _existing_columns('users')
    if 'bio' not in existing:
        op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    if 'avatar_url' not in existing:
        op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    if 'is_active' not in existing:
        op.add_column(
            'users',
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        )


def downgrade() -> None:
    existing = _existing_columns('users')
    if 'is_active' in existing:
        op.drop_column('users', 'is_active')
    if 'avatar_url' in existing:
        op.drop_column('users', 'avatar_url')
    if 'bio' in existing:
        op.drop_column('users', 'bio')
