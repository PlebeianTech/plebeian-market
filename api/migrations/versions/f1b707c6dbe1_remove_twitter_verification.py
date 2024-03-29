"""Remove Twitter verification.

Revision ID: f1b707c6dbe1
Revises: e301b9c852e0
Create Date: 2023-08-24 08:33:40.846725

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f1b707c6dbe1'
down_revision = 'e301b9c852e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('twitter_verification_phrase_check_counter')
        batch_op.drop_column('twitter_verification_phrase')
        batch_op.drop_column('twitter_verification_phrase_sent_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('twitter_verification_phrase_sent_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('twitter_verification_phrase', sa.VARCHAR(length=32), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('twitter_verification_phrase_check_counter', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
