"""align youths table with ORM model

Revision ID: 9471c7994e8e
Revises: 1af19b204f77
Create Date: 2026-10-16 01:42:09.765447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9471c7994e8e'
down_revision: Union[str, None] = '1af19b204f77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
