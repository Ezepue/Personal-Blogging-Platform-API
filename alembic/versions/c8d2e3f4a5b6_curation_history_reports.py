"""Curation, history, and reporting: unlisted/featured/word-count articles,
verified/pinned users, view_history and reports tables

Revision ID: c8d2e3f4a5b6
Revises: b7c1d2e3f4a5
Create Date: 2026-07-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c8d2e3f4a5b6'
down_revision = 'b7c1d2e3f4a5'
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _existing_columns(table: str):
    return {col["name"] for col in _inspector().get_columns(table)}


def _table_exists(table: str) -> bool:
    return _inspector().has_table(table)


def upgrade() -> None:
    cols = _existing_columns('articles')
    if 'word_count' not in cols:
        op.add_column('articles', sa.Column('word_count', sa.Integer(), nullable=False, server_default='0'))
    if 'is_unlisted' not in cols:
        op.add_column('articles', sa.Column('is_unlisted', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'is_featured' not in cols:
        op.add_column('articles', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.false()))

    cols = _existing_columns('users')
    if 'is_verified' not in cols:
        op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'pinned_article_id' not in cols:
        op.add_column('users', sa.Column(
            'pinned_article_id', sa.Integer(),
            sa.ForeignKey('articles.id', ondelete='SET NULL'), nullable=True,
        ))

    if not _table_exists('view_history'):
        op.create_table(
            'view_history',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('viewed_at', sa.DateTime(), nullable=False),
            sa.UniqueConstraint('user_id', 'article_id', name='unique_view_history'),
        )

    if not _table_exists('reports'):
        op.create_table(
            'reports',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('reporter_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('comment_id', sa.Integer(), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('reason', sa.String(500), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='open'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
        )


def downgrade() -> None:
    for table in ('reports', 'view_history'):
        if _table_exists(table):
            op.drop_table(table)

    cols = _existing_columns('users')
    for name in ('pinned_article_id', 'is_verified'):
        if name in cols:
            op.drop_column('users', name)

    cols = _existing_columns('articles')
    for name in ('is_featured', 'is_unlisted', 'word_count'):
        if name in cols:
            op.drop_column('articles', name)
