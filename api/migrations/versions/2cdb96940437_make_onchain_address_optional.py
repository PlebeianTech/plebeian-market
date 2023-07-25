"""Make onchain address optional.

Revision ID: 2cdb96940437
Revises: fe81d57b48b4
Create Date: 2023-07-25 07:53:35.436366

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2cdb96940437'
down_revision = 'fe81d57b48b4'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('on_chain_address', sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column('lightning_address', sa.String(length=128), nullable=True))
        batch_op.drop_index('ix_orders_payment_address')
        batch_op.create_index(batch_op.f('ix_orders_lightning_address'), ['lightning_address'], unique=False)
        batch_op.create_index(batch_op.f('ix_orders_on_chain_address'), ['on_chain_address'], unique=True)
        batch_op.drop_column('payment_address')

def downgrade():
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_address', sa.VARCHAR(length=128), autoincrement=False, nullable=False))
        batch_op.drop_index(batch_op.f('ix_orders_on_chain_address'))
        batch_op.drop_index(batch_op.f('ix_orders_lightning_address'))
        batch_op.create_index('ix_orders_payment_address', ['payment_address'], unique=False)
        batch_op.drop_column('lightning_address')
        batch_op.drop_column('on_chain_address')
