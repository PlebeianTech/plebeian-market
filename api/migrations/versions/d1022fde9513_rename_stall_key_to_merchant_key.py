"""Rename stall key to merchant key.

Revision ID: d1022fde9513
Revises: a0a088a1ee6c
Create Date: 2023-06-15 10:18:31.597022

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd1022fde9513'
down_revision = 'a0a088a1ee6c'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_stall_private_key')
        batch_op.drop_index('ix_users_stall_public_key')
        batch_op.alter_column(column_name='stall_private_key', new_column_name='merchant_private_key')
        batch_op.alter_column(column_name='stall_public_key', new_column_name='merchant_public_key')
        batch_op.create_index(batch_op.f('ix_users_merchant_private_key'), ['merchant_private_key'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_merchant_public_key'), ['merchant_public_key'], unique=True)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_merchant_private_key')
        batch_op.drop_index('ix_users_merchant_public_key')
        batch_op.alter_column(column_name='merchant_private_key', new_column_name='stall_private_key')
        batch_op.alter_column(column_name='merchant_public_key', new_column_name='stall_public_key')
        batch_op.create_index(batch_op.f('ix_users_stall_private_key'), ['stall_private_key'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_stall_public_key'), ['stall_public_key'], unique=True)
