"""status_os

Revision ID: 2040958f61b9
Revises: 8fe36ec8590
Create Date: 2015-11-21 15:09:01.307189

"""

# revision identifiers, used by Alembic.
revision = '2040958f61b9'
down_revision = '8fe36ec8590'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('ordem_servico', sa.Column('status', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('ordem_servico', 'status')
