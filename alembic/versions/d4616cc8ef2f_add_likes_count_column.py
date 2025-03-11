"""Add likes_count column"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "d4616cc8ef2f"
down_revision = "c8a8ba373c9e"
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade schema."""
    # Add the likes_count column to the articles table
    op.add_column('articles', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    """Downgrade schema."""
    # Remove the likes_count column if we roll back
    op.drop_column('articles', 'likes_count')
