"""Add resume.

Revision ID: 08c154310b4a
Revises: c757a5632f69
Create Date: 2023-02-07 16:13:51.645001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08c154310b4a'
down_revision = 'c757a5632f69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('job_title', sa.String(length=210), nullable=True))
        batch_op.add_column(sa.Column('bio', sa.String(length=21000), nullable=True))
        batch_op.add_column(sa.Column('desired_salary_usd', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('bitcoiner_question', sa.String(length=2100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('bitcoiner_question')
        batch_op.drop_column('desired_salary_usd')
        batch_op.drop_column('bio')
        batch_op.drop_column('job_title')

    # ### end Alembic commands ###
