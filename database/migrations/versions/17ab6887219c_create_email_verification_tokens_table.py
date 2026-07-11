"""create email_verification_tokens table

Revision ID: 17ab6887219c
Revises: 026aa877601d
Create Date: 2026-07-10 00:20:16.063883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17ab6887219c'
down_revision: Union[str, None] = '026aa877601d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create email_verification_tokens table
    op.create_table(
        'email_verification_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create unique index
    op.create_index('idx_email_verif_token', 'email_verification_tokens', ['token'], unique=True)


def downgrade() -> None:
    # 1. Drop unique index
    op.drop_index('idx_email_verif_token', table_name='email_verification_tokens')

    # 2. Drop email_verification_tokens table
    op.drop_table('email_verification_tokens')

