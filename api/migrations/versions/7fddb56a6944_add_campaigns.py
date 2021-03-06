"""Add campaigns.

Revision ID: 7fddb56a6944
Revises: f099812647a5
Create Date: 2022-07-18 14:32:06.850669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fddb56a6944'
down_revision = 'f099812647a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=24), nullable=False),
    sa.Column('title', sa.String(length=210), nullable=False),
    sa.Column('description', sa.String(length=2100), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_key'), 'campaigns', ['key'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_campaigns_key'), table_name='campaigns')
    op.drop_table('campaigns')
    # ### end Alembic commands ###
