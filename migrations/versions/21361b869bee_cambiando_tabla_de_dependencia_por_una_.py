"""cambiando tabla de dependencia por una tabla relación m-m

Revision ID: 21361b869bee
Revises: ec383ce7f19c
Create Date: 2025-06-23 12:04:36.131692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21361b869bee'
down_revision: Union[str, Sequence[str], None] = 'ec383ce7f19c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
