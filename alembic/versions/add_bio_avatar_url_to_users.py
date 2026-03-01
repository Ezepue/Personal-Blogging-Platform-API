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


def upgrade() -> None:
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
