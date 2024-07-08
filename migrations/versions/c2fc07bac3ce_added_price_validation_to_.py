"""Added price validation to RestaurantPizza

Revision ID: c2fc07bac3ce
Revises: 17316dd497ff
Create Date: 2024-07-08 03:00:20.815497

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'c2fc07bac3ce'
down_revision = '17316dd497ff'
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with the new schema
    op.create_table(
        'pizzas_new',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ingredients', sa.String(), nullable=True),
    )

    # Copy data from the old table to the new table
    op.execute('''
        INSERT INTO pizzas_new (id, name, ingredients)
        SELECT id, name, ingredients
        FROM pizzas
    ''')

    # Drop the old table
    op.drop_table('pizzas')

    # Rename the new table to the old table name
    op.rename_table('pizzas_new', 'pizzas')


def downgrade():
    # Create the old table again
    op.create_table(
        'pizzas_old',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('ingredients', sa.String(), nullable=True),
    )

    # Copy data from the new table to the old table
    op.execute('''
        INSERT INTO pizzas_old (id, name, ingredients)
        SELECT id, name, ingredients
        FROM pizzas
    ''')

    # Drop the new table
    op.drop_table('pizzas')

    # Rename the old table to the new table name
    op.rename_table('pizzas_old', 'pizzas')
