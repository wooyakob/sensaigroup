"""Removed design_rationale from Product

Revision ID: 9de62ac5bab5
Revises: 49974524c1f6
Create Date: 2023-08-22 14:39:06.916812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9de62ac5bab5'
down_revision = '49974524c1f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('design_rationale')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('design_rationale', sa.TEXT(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###