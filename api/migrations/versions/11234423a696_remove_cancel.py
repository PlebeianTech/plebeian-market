"""Remove cancel.

Revision ID: 11234423a696
Revises: ba6b5760534a
Create Date: 2022-05-11 07:53:25.961557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11234423a696'
down_revision = 'ba6b5760534a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('auctions', 'canceled')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auctions', sa.Column('canceled', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
