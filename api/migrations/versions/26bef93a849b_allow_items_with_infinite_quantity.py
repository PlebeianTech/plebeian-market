"""Allow items with infinite quantity.

Revision ID: 26bef93a849b
Revises: 906f050d11ff
Create Date: 2023-10-13 10:03:14.942223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26bef93a849b'
down_revision = '906f050d11ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.alter_column('available_quantity',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('listings', schema=None) as batch_op:
        batch_op.alter_column('available_quantity',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
