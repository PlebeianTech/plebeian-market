"""Initial migration.

Revision ID: 2df52c99b451
Revises: 
Create Date: 2022-04-19 12:14:04.370258

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import insert
from sqlalchemy import orm

# revision identifiers, used by Alembic.
revision = '2df52c99b451'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lnauth',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('k1', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('key', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lnauth_k1'), 'lnauth', ['k1'], unique=True)
    tbl_state = op.create_table('state',
    sa.Column('key', sa.String(length=32), nullable=False),
    sa.Column('value', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('key')
    )

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    session.execute(insert(tbl_state).values({"key": "LAST_SETTLE_INDEX", "value": "0"}))

    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.Column('key', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_key'), 'users', ['key'], unique=True)
    op.create_table('auctions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(length=12), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('starting_bid', sa.Integer(), nullable=False),
    sa.Column('reserve_bid', sa.Integer(), nullable=False),
    sa.Column('winning_bid_id', sa.Integer(), nullable=True),
    sa.Column('canceled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auctions_key'), 'auctions', ['key'], unique=True)
    op.create_table('bids',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=True),
    sa.Column('buyer_id', sa.Integer(), nullable=True),
    sa.Column('requested_at', sa.DateTime(), nullable=False),
    sa.Column('settled_at', sa.DateTime(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('payment_request', sa.String(length=512), nullable=False),
    sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ),
    sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bids_payment_request'), 'bids', ['payment_request'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bids_payment_request'), table_name='bids')
    op.drop_table('bids')
    op.drop_index(op.f('ix_auctions_key'), table_name='auctions')
    op.drop_table('auctions')
    op.drop_index(op.f('ix_users_key'), table_name='users')
    op.drop_table('users')
    op.drop_table('state')
    op.drop_index(op.f('ix_lnauth_k1'), table_name='lnauth')
    op.drop_table('lnauth')
    # ### end Alembic commands ###
