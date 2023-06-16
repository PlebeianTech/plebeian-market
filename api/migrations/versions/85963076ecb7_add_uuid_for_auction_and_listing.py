"""Add uuid for auction and listing.

Revision ID: 85963076ecb7
Revises: d1022fde9513
Create Date: 2023-06-16 07:08:41.345520

"""
from alembic import op
import sqlalchemy as sa, text

# revision identifiers, used by Alembic.
revision = '85963076ecb7'
down_revision = 'd1022fde9513'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.UUID(), nullable=False, server_default=text("gen_random_uuid()")))
        batch_op.create_index(batch_op.f('ix_auctions_uuid'), ['uuid'], unique=True)

    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', sa.UUID(), nullable=False, server_default=text("gen_random_uuid()")))
        batch_op.create_index(batch_op.f('ix_listings_uuid'), ['uuid'], unique=True)

def downgrade():
    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_listings_uuid'))
        batch_op.drop_column('uuid')

    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_auctions_uuid'))
        batch_op.drop_column('uuid')
