"""Remove constraints on old sales.

Revision ID: bc9e3f681186
Revises: a41ce996abe0
Create Date: 2023-11-29 10:37:59.089139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc9e3f681186'
down_revision = 'a41ce996abe0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.drop_constraint('sales_listing_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('sales_auction_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('sales_item_id_fkey', type_='foreignkey')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.create_foreign_key('sales_item_id_fkey', 'items', ['item_id'], ['id'])
        batch_op.create_foreign_key('sales_auction_id_fkey', 'auctions', ['auction_id'], ['id'])
        batch_op.create_foreign_key('sales_listing_id_fkey', 'listings', ['listing_id'], ['id'])

    # ### end Alembic commands ###
