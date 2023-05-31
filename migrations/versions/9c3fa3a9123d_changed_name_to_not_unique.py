"""Changed name to not unique

Revision ID: 9c3fa3a9123d
Revises: f60a925c797c
Create Date: 2023-05-30 19:39:00.409383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c3fa3a9123d'
down_revision = 'f60a925c797c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=False)

    # ### end Alembic commands ###
