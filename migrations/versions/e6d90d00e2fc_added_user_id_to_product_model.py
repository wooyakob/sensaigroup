"""Added user_id to Product model

Revision ID: e6d90d00e2fc
Revises: 5c149ef31b83
Create Date: 2023-09-08 15:02:46.762498

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'e6d90d00e2fc'
down_revision = '5c149ef31b83'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('products', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'products', 'users', ['user_id'], ['id'])

def downgrade():
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'user_id')