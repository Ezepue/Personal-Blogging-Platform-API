from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'new_revision_id'  # Replace with actual ID
down_revision = 'd4616cc8ef2f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('refresh_tokens', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))

def downgrade():
    op.drop_column('refresh_tokens', 'is_active')
