"""Add nostr profile image.

Revision ID: 1a2cb89c865c
Revises: 9172e04eca3b
Create Date: 2023-02-23 09:10:25.784913

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1a2cb89c865c'
down_revision = '9172e04eca3b'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(column_name='twitter_profile_image_url', new_column_name='profile_image_url')

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(column_name='profile_image_url', new_column_name='twitter_profile_image_url')
