"""create_tables

Revision ID: 8c71eeff3d00
Revises: a9537759e547
Create Date: 2025-06-28 01:46:47.733746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8c71eeff3d00'
down_revision: Union[str, None] = 'a9537759e547'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin_users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('two_factor_secret', sa.String(length=255), nullable=True),
    sa.Column('is_two_factor_enabled', sa.Boolean(), nullable=True),
    sa.Column('creation_date', sa.String(length=19), nullable=False),
    sa.Column('last_login', sa.String(length=19), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_table('employees',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('employee_name', sa.String(length=30), nullable=False),
    sa.Column('employee_script', mysql.JSON(), nullable=False),
    sa.Column('ia_name', sa.String(length=30), nullable=False),
    sa.Column('endpoint_url', sa.String(length=255), nullable=False),
    sa.Column('endpoint_key', sa.String(length=255), nullable=False),
    sa.Column('headers_template', mysql.JSON(), nullable=False),
    sa.Column('body_template', mysql.JSON(), nullable=False),
    sa.Column('last_update', sa.String(length=19), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('employee_name')
    )
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('nickname', sa.String(length=30), nullable=False),
    sa.Column('google_id', sa.String(length=255), nullable=True),
    sa.Column('github_id', sa.String(length=255), nullable=True),
    sa.Column('two_factor_secret', sa.String(length=255), nullable=True),
    sa.Column('is_two_factor_enabled', sa.Boolean(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('creation_date', sa.String(length=19), nullable=False),
    sa.Column('last_login', sa.String(length=19), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('github_id'),
    sa.UniqueConstraint('google_id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('briefings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('content', mysql.JSON(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('development_roteiro', mysql.JSON(), nullable=True),
    sa.Column('creation_date', sa.String(length=19), nullable=False),
    sa.Column('update_date', sa.String(length=19), nullable=True),
    sa.Column('last_edited_by', sa.String(length=5), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'title', name='_user_title_uc')
    )
    op.create_index(op.f('ix_briefings_id'), 'briefings', ['id'], unique=False)
    op.create_table('conversation_histories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('briefing_id', sa.Integer(), nullable=False),
    sa.Column('sender_type', sa.String(length=30), nullable=False),
    sa.Column('message_content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.String(length=19), nullable=False),
    sa.ForeignKeyConstraint(['briefing_id'], ['briefings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_histories_id'), 'conversation_histories', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_conversation_histories_id'), table_name='conversation_histories')
    op.drop_table('conversation_histories')
    op.drop_index(op.f('ix_briefings_id'), table_name='briefings')
    op.drop_table('briefings')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_table('employees')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    op.drop_table('admin_users')
    # ### end Alembic commands ###
