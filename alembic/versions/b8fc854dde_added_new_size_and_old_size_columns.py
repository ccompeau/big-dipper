"""Added new_size and old_size columns

Revision ID: b8fc854dde
Revises: 2e2d85d6529
Create Date: 2015-08-09 13:52:50.685354

"""

# revision identifiers, used by Alembic.
revision = 'b8fc854dde'
down_revision = '2e2d85d6529'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coinbase_messages', sa.Column('new_size', sa.Numeric(), nullable=True))
    op.add_column('coinbase_messages', sa.Column('old_size', sa.Numeric(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coinbase_messages', 'old_size')
    op.drop_column('coinbase_messages', 'new_size')
    ### end Alembic commands ###
