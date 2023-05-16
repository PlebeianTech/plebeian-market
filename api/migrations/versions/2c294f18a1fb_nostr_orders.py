"""Nostr orders.

Revision ID: 2c294f18a1fb
Revises: 4c6c784e30e1
Create Date: 2023-05-02 14:43:18.398353

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2c294f18a1fb'
down_revision = 'f25b308df569'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('orders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('event_id', sa.String(length=64), nullable=False),
    sa.Column('buyer_public_key', sa.String(length=64), nullable=False),
    sa.Column('requested_at', sa.DateTime(), nullable=False),
    sa.Column('payment_address', sa.String(length=128), nullable=False),
    sa.Column('txid', sa.String(length=128), nullable=True),
    sa.Column('tx_value', sa.Integer(), nullable=True),
    sa.Column('tx_confirmed', sa.Boolean(), nullable=False),
    sa.Column('expired_at', sa.DateTime(), nullable=True),
    sa.Column('shipping_usd', sa.Float(), nullable=False),
    sa.Column('total_usd', sa.Float(), nullable=False),
    sa.Column('total', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_orders_uuid'), ['uuid'], unique=True)
        batch_op.create_index(batch_op.f('ix_orders_buyer_public_key'), ['buyer_public_key'], unique=False)
        batch_op.create_index(batch_op.f('ix_orders_event_id'), ['event_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_orders_payment_address'), ['payment_address'], unique=True)

    op.create_table('order_items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stall_public_key', sa.String(length=64), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_stall_public_key'), ['stall_public_key'], unique=True)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_stall_public_key'))
        batch_op.drop_column('stall_public_key')

    op.drop_table('order_items')
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_orders_payment_address'))
        batch_op.drop_index(batch_op.f('ix_orders_event_id'))
        batch_op.drop_index(batch_op.f('ix_orders_buyer_public_key'))

    op.drop_table('orders')
