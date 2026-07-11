"""create audit_logs table

Revision ID: 3ba0b32063c6
Revises: 52352b5d6648
Create Date: 2026-07-10 00:27:10.546222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ba0b32063c6'
down_revision: Union[str, None] = '52352b5d6648'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # 1. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('event', sa.String(length=100), nullable=False),
        sa.Column('actor_id', sa.UUID(), nullable=True),
        sa.Column('target_id', sa.UUID(), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Create indexes
    op.create_index('idx_audit_logs_actor', 'audit_logs', ['actor_id'])
    op.create_index('idx_audit_logs_event', 'audit_logs', ['event'])
    op.create_index('idx_audit_logs_created', 'audit_logs', [sa.text('created_at DESC')])


def downgrade() -> None:
    # 1. Drop indexes
    op.drop_index('idx_audit_logs_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_event', table_name='audit_logs')
    op.drop_index('idx_audit_logs_actor', table_name='audit_logs')

    # 2. Drop audit_logs table
    op.drop_table('audit_logs')

