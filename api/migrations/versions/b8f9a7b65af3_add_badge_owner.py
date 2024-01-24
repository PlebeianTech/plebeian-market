"""Add badge owner.

Revision ID: b8f9a7b65af3
Revises: 4ff050ac2527
Create Date: 2024-01-24 11:10:25.686793

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b8f9a7b65af3'
down_revision = '4ff050ac2527'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('badges', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_public_key', sa.String(length=64), nullable=False, server_default="28c62ad00fe085a7b2b54a05fdf333367e3e6a4d9650ad1c159f964705b76928"))
        batch_op.alter_column('nostr_event_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)

def downgrade():
    with op.batch_alter_table('badges', schema=None) as batch_op:
        batch_op.alter_column('nostr_event_id',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
        batch_op.drop_column('owner_public_key')
