"""Add lnauth key name.

Revision ID: 906f050d11ff
Revises: 5b918d4f5903
Create Date: 2023-10-10 07:58:42.612864

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '906f050d11ff'
down_revision = '5b918d4f5903'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lnauth_key_name', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('lnauth_key_name')

    # ### end Alembic commands ###
