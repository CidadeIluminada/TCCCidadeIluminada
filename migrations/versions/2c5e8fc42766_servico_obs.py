"""servico obs

Revision ID: 2c5e8fc42766
Revises: 2ade01d955f4
Create Date: 2015-11-27 16:58:26.247084

"""

# revision identifiers, used by Alembic.
revision = '2c5e8fc42766'
down_revision = '2ade01d955f4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('servico', sa.Column('obs_secretaria', sa.Text(), nullable=True))
    op.add_column('servico', sa.Column('obs_urbam', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('servico', 'obs_urbam')
    op.drop_column('servico', 'obs_secretaria')
