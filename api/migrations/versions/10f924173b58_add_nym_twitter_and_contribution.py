"""Add nym, Twitter and contribution.

Revision ID: 10f924173b58
Revises: 2df52c99b451
Create Date: 2022-04-20 17:04:50.514311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10f924173b58'
down_revision = '2df52c99b451'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('nym', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('twitter_username', sa.String(length=32), nullable=True))
    op.add_column('users', sa.Column('twitter_username_verified', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('twitter_username_challenge', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('contribution_percent', sa.Float(), nullable=True))
    op.create_index(op.f('ix_users_nym'), 'users', ['nym'], unique=True)
    op.create_index(op.f('ix_users_twitter_username'), 'users', ['twitter_username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_twitter_username'), table_name='users')
    op.drop_index(op.f('ix_users_nym'), table_name='users')
    op.drop_column('users', 'contribution_percent')
    op.drop_column('users', 'twitter_username_challenge')
    op.drop_column('users', 'twitter_username_verified')
    op.drop_column('users', 'twitter_username')
    op.drop_column('users', 'nym')
    # ### end Alembic commands ###
