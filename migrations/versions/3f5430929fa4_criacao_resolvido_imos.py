"""criacao resolvido IMOS

Revision ID: 3f5430929fa4
Revises: 2040958f61b9
Create Date: 2015-11-21 15:14:18.293528

"""

# revision identifiers, used by Alembic.
revision = '3f5430929fa4'
down_revision = '2040958f61b9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('item_manutencao_ordem_servico', sa.Column('criacao', sa.DateTime(), nullable=True))
    op.add_column('item_manutencao_ordem_servico', sa.Column('resolucao', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('item_manutencao_ordem_servico', 'resolucao')
    op.drop_column('item_manutencao_ordem_servico', 'criacao')
