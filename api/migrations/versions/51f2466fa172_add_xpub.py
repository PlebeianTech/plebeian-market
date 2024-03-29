"""Add xpub.

Revision ID: 51f2466fa172
Revises: 7fddb56a6944
Create Date: 2022-07-29 07:53:39.332097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51f2466fa172'
down_revision = '7fddb56a6944'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('xpub', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'xpub')
    # ### end Alembic commands ###
