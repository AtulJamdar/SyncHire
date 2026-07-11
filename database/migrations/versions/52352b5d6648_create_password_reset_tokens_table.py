"""create password_reset_tokens table

Revision ID: 52352b5d6648
Revises: 17ab6887219c
Create Date: 2026-07-10 00:22:54.117023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52352b5d6648'
down_revision: Union[str, None] = '17ab6887219c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create index
    op.create_index('idx_pw_reset_user_id', 'password_reset_tokens', ['user_id'])


def downgrade() -> None:
    # 1. Drop index
    op.drop_index('idx_pw_reset_user_id', table_name='password_reset_tokens')

    # 2. Drop password_reset_tokens table
    op.drop_table('password_reset_tokens')

