"""Make verified_identities_required optional per-auction.

Revision ID: 7bfdc024cc59
Revises: 7218961e6757
Create Date: 2024-01-15 13:56:56.087179

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7bfdc024cc59'
down_revision = '7218961e6757'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verified_identities_required', sa.Integer(), nullable=False, server_default="0"))

def downgrade():
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.drop_column('verified_identities_required')
