"""Make skin in the game optional per-auction.

Revision ID: 8e5794f2abd4
Revises: 0f52341f4fa1
Create Date: 2023-09-04 15:19:05.944150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e5794f2abd4'
down_revision = '0f52341f4fa1'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skin_in_the_game_required', sa.Boolean(), nullable=False, server_default="false"))

def downgrade():
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.drop_column('skin_in_the_game_required')
