"""Add listings.

Revision ID: c6d089d54e86
Revises: c4493279d631
Create Date: 2022-08-23 08:03:00.157954

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6d089d54e86'
down_revision = 'c4493279d631'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('title', sa.String(length=210), nullable=False),
    sa.Column('description', sa.String(length=21000), nullable=False),
    sa.Column('shipping_from', sa.String(length=64), nullable=True),
    sa.Column('shipping_domestic_usd', sa.Float(), nullable=False),
    sa.Column('shipping_worldwide_usd', sa.Float(), nullable=False),
    sa.Column('is_hidden', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('listings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=12), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('price_usd', sa.Float(), nullable=False),
    sa.Column('available_quantity', sa.Integer(), nullable=False),
    sa.Column('twitter_id', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_listings_key'), 'listings', ['key'], unique=True)
    op.create_table('sales',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=True),
    sa.Column('listing_id', sa.Integer(), nullable=True),
    sa.Column('buyer_id', sa.Integer(), nullable=False),
    sa.Column('requested_at', sa.DateTime(), nullable=False),
    sa.Column('state', sa.Integer(), nullable=False),
    sa.Column('settled_at', sa.DateTime(), nullable=True),
    sa.Column('txid', sa.String(length=128), nullable=True),
    sa.Column('tx_value', sa.Integer(), nullable=True),
    sa.Column('expired_at', sa.DateTime(), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('shipping_domestic', sa.Integer(), nullable=False),
    sa.Column('shipping_worldwide', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('contribution_amount', sa.Integer(), nullable=False),
    sa.Column('contribution_payment_request', sa.String(length=512), nullable=False),
    sa.Column('contribution_settled_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ),
    sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_contribution_payment_request'), 'sales', ['contribution_payment_request'], unique=True)
    op.create_index(op.f('ix_sales_address'), 'sales', ['address'], unique=True)
    op.add_column('auctions', sa.Column('item_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_auctions_item_id', 'auctions', 'items', ['item_id'], ['id'])
    op.drop_column('auctions', 'is_featured')
    op.add_column('media', sa.Column('item_id', sa.Integer(), nullable=True))
    op.alter_column('media', 'auction_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key('fk_media_item_id', 'media', 'items', ['item_id'], ['id'])
    op.add_column('users', sa.Column('xpub_index', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'xpub_index')
    op.drop_constraint('fk_media_item_id', 'media', type_='foreignkey')
    op.alter_column('media', 'auction_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('media', 'item_id')
    op.add_column('auctions', sa.Column('is_featured', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_constraint('fk_auctions_item_id', 'auctions', type_='foreignkey')
    op.drop_column('auctions', 'item_id')
    op.drop_index(op.f('ix_sales_contribution_payment_request'), table_name='sales')
    op.drop_index(op.f('ix_sales_address'), table_name='sales')
    op.drop_table('sales')
    op.drop_index(op.f('ix_listings_key'), table_name='listings')
    op.drop_table('listings')
    op.drop_table('items')
    # ### end Alembic commands ###