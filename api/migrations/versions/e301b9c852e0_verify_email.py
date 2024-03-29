"""Verify email.

Revision ID: e301b9c852e0
Revises: 673138f33cbb
Create Date: 2023-08-22 14:37:33.058719

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e301b9c852e0'
down_revision = '673138f33cbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verification_phrase', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('email_verification_phrase_sent_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('email_verification_phrase_check_counter', sa.Integer(), nullable=False, server_default="0"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('email_verification_phrase_check_counter')
        batch_op.drop_column('email_verification_phrase_sent_at')
        batch_op.drop_column('email_verification_phrase')

    # ### end Alembic commands ###
