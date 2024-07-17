"""empty message

Revision ID: 7c9fe9d122bb
Revises: 4d87fc222fa7
Create Date: 2024-07-10 18:17:50.447003

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7c9fe9d122bb'
down_revision = '4d87fc222fa7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), nullable=False))
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('artist_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.alter_column('time',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
        batch_op.alter_column('artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('id')

    # ### end Alembic commands ###
