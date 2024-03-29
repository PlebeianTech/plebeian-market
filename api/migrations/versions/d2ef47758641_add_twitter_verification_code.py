"""Add twitter verification phrase.

Revision ID: d2ef47758641
Revises: 8d076a2b6337
Create Date: 2022-11-01 11:36:28.183728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2ef47758641'
down_revision = '8d076a2b6337'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'twitter_username_verification_tweet_id')
    op.add_column('users', sa.Column('twitter_verification_phrase', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('twitter_verification_phrase_sent_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('twitter_verification_phrase_check_counter', sa.Integer(), nullable=False, server_default="0"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'twitter_verification_phrase_check_counter')
    op.drop_column('users', 'twitter_verification_phrase_sent_at')
    op.drop_column('users', 'twitter_verification_phrase')
    op.add_column('users', sa.Column('twitter_username_verification_tweet_id', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###
