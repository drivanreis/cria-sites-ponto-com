"""initial_schema_creation

Revision ID: b5b3a942be24
Revises: d90eeda8560f
Create Date: 2025-05-20 16:25:14.443082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5b3a942be24'
down_revision: Union[str, None] = 'd90eeda8560f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
