"""Add telegram username.

Revision ID: 8d076a2b6337
Revises: 526dd4c581ca
Create Date: 2022-10-28 08:42:29.373028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d076a2b6337'
down_revision = '526dd4c581ca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('telegram_username', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('telegram_username_verified', sa.Boolean(), nullable=False, server_default="false"))
    op.create_index(op.f('ix_users_telegram_username'), 'users', ['telegram_username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_telegram_username'), table_name='users')
    op.drop_column('users', 'telegram_username_verified')
    op.drop_column('users', 'telegram_username')
    # ### end Alembic commands ###