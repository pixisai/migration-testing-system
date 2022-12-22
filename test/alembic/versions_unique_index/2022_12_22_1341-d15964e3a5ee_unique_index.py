"""Unique Index

Revision ID: d15964e3a5ee
Revises: 1f8a9d811105
Create Date: 2022-12-22 13:41:57.851319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd15964e3a5ee'
down_revision = '1f8a9d811105'
branch_labels =  'versions_unique_index'
depends_on = None


def upgrade() -> None:
    op.create_index("ik_user", "user", ["first_name", "second_name"])
    # ### end Alembic commands ###

def downgrade() -> None:
    pass
    # ### end Alembic commands ###
