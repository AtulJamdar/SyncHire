"""create users table

Revision ID: d2de6f0426ea
Revises: 
Create Date: 2026-07-10 00:11:53.053709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2de6f0426ea'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create custom user_role enum type
    op.execute("CREATE TYPE user_role AS ENUM ('student', 'admin')")

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('profile_picture_url', sa.String(length=500), nullable=True),
        sa.Column('role', sa.Enum('student', 'admin', name='user_role'), server_default='student', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('telegram_linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create custom indexes matching the schema
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index(
        'idx_users_telegram_id',
        'users',
        ['telegram_id'],
        unique=True,
        postgresql_where=sa.text('telegram_id IS NOT NULL')
    )
    op.create_index(
        'idx_users_google_id',
        'users',
        ['google_id'],
        unique=True,
        postgresql_where=sa.text('google_id IS NOT NULL')
    )
    op.create_index(
        'idx_users_is_deleted',
        'users',
        ['is_deleted'],
        postgresql_where=sa.text('is_deleted = false')
    )
    op.create_index('idx_users_role', 'users', ['role'])


def downgrade() -> None:
    # 1. Drop custom indexes
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_is_deleted', table_name='users')
    op.drop_index('idx_users_google_id', table_name='users')
    op.drop_index('idx_users_telegram_id', table_name='users')
    op.drop_index('idx_users_email', table_name='users')

    # 2. Drop users table
    op.drop_table('users')

    # 3. Drop custom user_role enum type
    op.execute("DROP TYPE user_role")

