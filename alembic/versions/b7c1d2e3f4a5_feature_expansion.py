"""Feature expansion: follows, bookmarks, comment likes, article/comment/user/notification columns

Revision ID: b7c1d2e3f4a5
Revises: a1b2c3d4e5f6
Create Date: 2026-07-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'b7c1d2e3f4a5'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def _inspector():
    return sa.inspect(op.get_bind())


def _existing_columns(table: str):
    return {col["name"] for col in _inspector().get_columns(table)}


def _table_exists(table: str) -> bool:
    return _inspector().has_table(table)


def upgrade() -> None:
    # --- New tables (skipped when the base migration already created them from the ORM) ---
    if not _table_exists('follows'):
        op.create_table(
            'follows',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('follower_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('followed_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),
        )

    if not _table_exists('bookmarks'):
        op.create_table(
            'bookmarks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.UniqueConstraint('user_id', 'article_id', name='unique_bookmark'),
        )

    if not _table_exists('comment_likes'):
        op.create_table(
            'comment_likes',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('comment_id', sa.Integer(), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.UniqueConstraint('user_id', 'comment_id', name='unique_comment_like'),
        )

    # --- articles ---
    cols = _existing_columns('articles')
    if 'subtitle' not in cols:
        op.add_column('articles', sa.Column('subtitle', sa.String(300), nullable=True))
    if 'slug' not in cols:
        op.add_column('articles', sa.Column('slug', sa.String(250), nullable=True))
        op.create_index('ix_articles_slug', 'articles', ['slug'], unique=True)
    if 'cover_image_url' not in cols:
        op.add_column('articles', sa.Column('cover_image_url', sa.String(500), nullable=True))
    if 'views_count' not in cols:
        op.add_column('articles', sa.Column('views_count', sa.Integer(), nullable=False, server_default='0'))
    if 'reading_time_minutes' not in cols:
        op.add_column('articles', sa.Column('reading_time_minutes', sa.Integer(), nullable=False, server_default='1'))

    # --- comments ---
    cols = _existing_columns('comments')
    if 'parent_id' not in cols:
        op.add_column('comments', sa.Column('parent_id', sa.Integer(), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True))
        op.create_index('ix_comments_parent_id', 'comments', ['parent_id'])
    if 'likes_count' not in cols:
        op.add_column('comments', sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'))

    # --- users ---
    cols = _existing_columns('users')
    if 'created_at' not in cols:
        op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    for name, col in (
        ('website', sa.Column('website', sa.String(300), nullable=True)),
        ('location', sa.Column('location', sa.String(120), nullable=True)),
        ('twitter', sa.Column('twitter', sa.String(80), nullable=True)),
        ('github', sa.Column('github', sa.String(80), nullable=True)),
    ):
        if name not in cols:
            op.add_column('users', col)
    for name in ('notify_likes', 'notify_comments', 'notify_follows'):
        if name not in cols:
            op.add_column('users', sa.Column(name, sa.Boolean(), nullable=False, server_default=sa.true()))

    # --- notifications ---
    cols = _existing_columns('notifications')
    if 'type' not in cols:
        op.add_column('notifications', sa.Column('type', sa.String(20), nullable=False, server_default='system'))


def downgrade() -> None:
    for table in ('comment_likes', 'bookmarks', 'follows'):
        if _table_exists(table):
            op.drop_table(table)

    cols = _existing_columns('notifications')
    if 'type' in cols:
        op.drop_column('notifications', 'type')

    cols = _existing_columns('users')
    for name in ('notify_follows', 'notify_comments', 'notify_likes', 'github', 'twitter', 'location', 'website', 'created_at'):
        if name in cols:
            op.drop_column('users', name)

    cols = _existing_columns('comments')
    if 'likes_count' in cols:
        op.drop_column('comments', 'likes_count')
    if 'parent_id' in cols:
        op.drop_index('ix_comments_parent_id', table_name='comments')
        op.drop_column('comments', 'parent_id')

    cols = _existing_columns('articles')
    for name in ('reading_time_minutes', 'views_count', 'cover_image_url', 'subtitle'):
        if name in cols:
            op.drop_column('articles', name)
    if 'slug' in cols:
        op.drop_index('ix_articles_slug', table_name='articles')
        op.drop_column('articles', 'slug')
