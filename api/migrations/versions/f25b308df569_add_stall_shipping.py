"""Add stall shipping.

Revision ID: f25b308df569
Revises: 4c6c784e30e1
Create Date: 2023-05-09 11:49:06.148397

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f25b308df569'
down_revision = '4c6c784e30e1'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_from', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('shipping_domestic_usd', sa.Float(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column('shipping_worldwide_usd', sa.Float(), nullable=False, server_default="0"))

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('shipping_worldwide_usd')
        batch_op.drop_column('shipping_domestic_usd')
        batch_op.drop_column('shipping_from')
