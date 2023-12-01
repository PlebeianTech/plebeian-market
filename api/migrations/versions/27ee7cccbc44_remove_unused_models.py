"""Remove unused models.

Revision ID: 27ee7cccbc44
Revises: 15905fe0375d
Create Date: 2023-11-28 15:40:21.456922

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '27ee7cccbc44'
down_revision = '15905fe0375d'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_table('messages')
    op.drop_table('user_notifications')

def downgrade():
    op.create_table('user_notifications',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('notification_type', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('action', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_notifications_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', 'notification_type', name='user_notifications_pkey')
    )
    op.create_table('messages',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('key', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('body', sa.VARCHAR(length=512), autoincrement=False, nullable=True),
    sa.Column('notified_via', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='messages_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='messages_pkey'),
    sa.UniqueConstraint('user_id', 'key', name='messages_user_id_key_key')
    )
