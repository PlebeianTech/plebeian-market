"""Add categories.

Revision ID: 15905fe0375d
Revises: 26bef93a849b
Create Date: 2023-11-23 13:41:30.163211

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '15905fe0375d'
down_revision = '26bef93a849b'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tag', sa.String(length=210), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_categories_tag'), ['tag'], unique=True)

    op.create_table('item_categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_column('category')

def downgrade():
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.VARCHAR(length=21), autoincrement=False, nullable=True))

    op.drop_table('item_categories')

    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_categories_tag'))

    op.drop_table('categories')
