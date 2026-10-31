"""add_inventory_events

Revision ID: 279df11571b5
Revises: a7efcffe1116
Create Date: 2026-10-31 13:57:46.508131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '279df11571b5'
down_revision: Union[str, Sequence[str], None] = 'a7efcffe1116'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    if 'inventory_events' not in tables:
        op.create_table(
            'inventory_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('product_id', sa.Integer(), nullable=False),
            sa.Column('event_type', sa.String(length=40), nullable=False),
            sa.Column('channel', sa.String(length=40), nullable=True),
            sa.Column('sold_price', sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column('quantity_change', sa.Integer(), nullable=False),
            sa.Column('remaining_stock', sa.Integer(), nullable=False),
            sa.Column('buyer_note', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['product_id'], ['products.id']),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('inventory_events', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_inventory_events_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_inventory_events_product_id'), ['product_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('inventory_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inventory_events_product_id'))
        batch_op.drop_index(batch_op.f('ix_inventory_events_id'))
    op.drop_table('inventory_events')
