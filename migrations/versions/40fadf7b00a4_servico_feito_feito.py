"""servico_feito -> feito

Revision ID: 40fadf7b00a4
Revises: 3a6010adbe08
Create Date: 2015-11-22 21:17:38.018859

"""

# revision identifiers, used by Alembic.
revision = '40fadf7b00a4'
down_revision = '3a6010adbe08'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('servico', 'servico_feito', new_column_name='feito')


def downgrade():
    op.alter_column('servico', 'feito', new_column_name='servico_feito')
