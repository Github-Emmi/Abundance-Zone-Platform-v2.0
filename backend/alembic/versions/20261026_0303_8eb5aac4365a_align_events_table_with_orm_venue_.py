"""align events table with ORM (venue, created_by_id, is_recurring, is_regional)

Revision ID: 8eb5aac4365a
Revises: 9471c7994e8e
Create Date: 2026-10-26 03:03:57.136107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eb5aac4365a'
down_revision: Union[str, None] = '9471c7994e8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Since you already ran these changes manually via SQL,
    # this migration encodes them for fresh environments.
    op.alter_column('events', 'created_by', new_column_name='created_by_id')

    with op.batch_alter_table('events') as batch:
        batch.drop_column('location')
    with op.batch_alter_table('events') as batch:
        batch.drop_column('start_time')
    with op.batch_alter_table('events') as batch:
        batch.drop_column('end_time')
    with op.batch_alter_table('events') as batch:
        batch.drop_column('event_status')

    with op.batch_alter_table('events') as batch:
        batch.add_column(sa.Column('venue', sa.String(255), nullable=True))
    with op.batch_alter_table('events') as batch:
        batch.add_column(sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table('events') as batch:
        batch.add_column(sa.Column('is_regional', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.alter_column('events', 'created_by_id', new_column_name='created_by')
    op.add_column('events', sa.Column('location', sa.String(255), nullable=True))
    op.add_column('events', sa.Column('start_time', sa.Time(), nullable=False, server_default='09:00'))
    op.add_column('events', sa.Column('end_time', sa.Time(), nullable=True))
    op.drop_column('events', 'venue')
    op.drop_column('events', 'is_recurring')
    op.drop_column('events', 'is_regional')