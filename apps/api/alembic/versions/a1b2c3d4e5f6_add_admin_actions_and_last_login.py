"""add_admin_actions_and_last_login

Revision ID: a1b2c3d4e5f6
Revises: 859e7fd7d564
Create Date: 2026-09-29 21:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '859e7fd7d564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add last_login to users
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))

    # 2. Create administrative_actions table
    op.create_table(
        'administrative_actions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('action_type', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.String(length=128), nullable=False),
        sa.Column('actor_role', sa.String(length=32), nullable=False, server_default='administrator'),
        sa.Column('target_resource_type', sa.String(length=64), nullable=False),
        sa.Column('target_resource_id', sa.String(length=128), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='EXECUTED'),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_administrative_actions_action_type'), 'administrative_actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_administrative_actions_actor_id'), 'administrative_actions', ['actor_id'], unique=False)
    op.create_index(op.f('ix_administrative_actions_target_resource_type'), 'administrative_actions', ['target_resource_type'], unique=False)
    op.create_index(op.f('ix_administrative_actions_target_resource_id'), 'administrative_actions', ['target_resource_id'], unique=False)
    op.create_index(op.f('ix_administrative_actions_created_at'), 'administrative_actions', ['created_at'], unique=False)
    op.create_index('idx_admin_actions_actor', 'administrative_actions', ['actor_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_admin_actions_actor', table_name='administrative_actions')
    op.drop_index(op.f('ix_administrative_actions_created_at'), table_name='administrative_actions')
    op.drop_index(op.f('ix_administrative_actions_target_resource_id'), table_name='administrative_actions')
    op.drop_index(op.f('ix_administrative_actions_target_resource_type'), table_name='administrative_actions')
    op.drop_index(op.f('ix_administrative_actions_actor_id'), table_name='administrative_actions')
    op.drop_index(op.f('ix_administrative_actions_action_type'), table_name='administrative_actions')
    op.drop_table('administrative_actions')
    op.drop_column('users', 'last_login')
