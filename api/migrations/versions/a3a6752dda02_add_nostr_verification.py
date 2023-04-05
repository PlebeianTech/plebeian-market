"""Add Nostr verification.

Revision ID: a3a6752dda02
Revises: 3d5b3055fc79
Create Date: 2023-04-04 13:11:09.199277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3a6752dda02'
down_revision = '3d5b3055fc79'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nostr_public_key_verified', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('nostr_verification_phrase', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('nostr_verification_phrase_sent_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('nostr_verification_phrase_check_counter', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('nostr_verification_phrase_check_counter')
        batch_op.drop_column('nostr_verification_phrase_sent_at')
        batch_op.drop_column('nostr_verification_phrase')
        batch_op.drop_column('nostr_public_key_verified')

    # ### end Alembic commands ###