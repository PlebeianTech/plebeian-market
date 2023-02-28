"""Rename xpub to wallet.

Revision ID: 3d5b3055fc79
Revises: f47e6e86bea8
Create Date: 2023-02-28 15:32:47.451301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d5b3055fc79'
down_revision = 'f47e6e86bea8'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.alter_column(column_name='xpub', new_column_name='wallet')
        batch_op.alter_column(column_name='xpub_index', new_column_name='wallet_index')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(column_name='xpub', new_column_name='wallet')
        batch_op.alter_column(column_name='xpub_index', new_column_name='wallet_index')

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(column_name='wallet_index', new_column_name='xpub_index')
        batch_op.alter_column(column_name='wallet', new_column_name='xpub')

    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.alter_column(column_name='wallet_index', new_column_name='xpub_index')
        batch_op.alter_column(column_name='wallet', new_column_name='xpub')
