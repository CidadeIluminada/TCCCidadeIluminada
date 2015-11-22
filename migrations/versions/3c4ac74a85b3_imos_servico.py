"""imos -> servico

Revision ID: 3c4ac74a85b3
Revises: 3f5430929fa4
Create Date: 2015-11-22 16:22:42.836437

"""

# revision identifiers, used by Alembic.
revision = '3c4ac74a85b3'
down_revision = '3f5430929fa4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.rename_table('item_manutencao_ordem_servico', 'servico')


def downgrade():
    op.rename_table('servico', 'item_manutencao_ordem_servico')
