"""initial_schema_creation

Revision ID: 4c8fa4ae0bc0
Revises: c6eaa648f7d7
Create Date: 2025-05-20 15:52:45.049746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c8fa4ae0bc0'
down_revision: Union[str, None] = 'c6eaa648f7d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
