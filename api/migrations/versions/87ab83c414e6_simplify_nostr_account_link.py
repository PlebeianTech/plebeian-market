"""Simplify nostr account link.

Revision ID: 87ab83c414e6
Revises: 2cdb96940437
Create Date: 2023-07-28 10:01:16.534905
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '87ab83c414e6'
down_revision = '2cdb96940437'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("UPDATE users SET nostr_public_key = NULL WHERE NOT nostr_public_key_verified")

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('nostr_public_key_verified')
        batch_op.drop_column('nostr_verification_phrase_check_counter')
        batch_op.drop_column('nostr_verification_phrase_sent_at')
        batch_op.drop_column('nostr_verification_phrase')

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nostr_verification_phrase', sa.VARCHAR(length=32), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('nostr_verification_phrase_sent_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('nostr_verification_phrase_check_counter', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('nostr_public_key_verified', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False))
