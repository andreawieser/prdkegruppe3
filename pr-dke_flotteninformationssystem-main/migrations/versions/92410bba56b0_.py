"""empty message

Revision ID: 92410bba56b0
Revises: 207da8bed468
Create Date: 2022-11-15 17:39:38.207760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92410bba56b0'
down_revision = '207da8bed468'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])

    with op.batch_alter_table('waggons', schema=None) as batch_op:
        batch_op.add_column(sa.Column('zug', sa.Integer(), nullable=False))
        batch_op.create_unique_constraint(batch_op.f('uq_waggons_fg_nummer'), ['fg_nummer'])
        batch_op.create_foreign_key(batch_op.f('fk_waggons_zug_zuege'), 'zuege', ['zug'], ['id'])

    with op.batch_alter_table('zuege', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_zuege_nummer'), ['nummer'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('zuege', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_zuege_nummer'), type_='unique')

    with op.batch_alter_table('waggons', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_waggons_zug_zuege'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('uq_waggons_fg_nummer'), type_='unique')
        batch_op.drop_column('zug')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    # ### end Alembic commands ###
