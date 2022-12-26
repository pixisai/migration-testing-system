"""Unique Constraints

Revision ID: 8db619964b80
Revises: 1f8a9d811105
Create Date: 2022-12-22 13:06:51.918462

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "8db619964b80"
down_revision = "1f8a9d811105"
branch_labels = "versions_unique_constraints"
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_user_name", "user", ["first_name"])
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
    # ### end Alembic commands ###
