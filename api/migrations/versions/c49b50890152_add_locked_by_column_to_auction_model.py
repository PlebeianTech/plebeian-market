"""Add locked_by column to auction model.

Revision ID: c49b50890152
Revises: a5db732683bd
Create Date: 2022-07-11 00:07:25.673848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c49b50890152'
down_revision = 'a5db732683bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auctions', sa.Column('locked_by', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('auctions', 'locked_by')
    # ### end Alembic commands ###
