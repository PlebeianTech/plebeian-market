"""Nostr auth without DM.

Revision ID: f16c319d7a0f
Revises: fcecd5eab28d
Create Date: 2023-07-13 15:34:36.462852

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f16c319d7a0f'
down_revision = 'fcecd5eab28d'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('nostr_auth', schema=None) as batch_op:
        batch_op.drop_column('verification_phrase_check_counter')
        batch_op.drop_column('verification_phrase_sent_at')

def downgrade():
    with op.batch_alter_table('nostr_auth', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification_phrase_sent_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('verification_phrase_check_counter', sa.INTEGER(), autoincrement=False, nullable=False, server_default="0"))
