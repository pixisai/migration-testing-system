"""primary key

Revision ID: 29bdb076c853
Revises: 1f8a9d811105
Create Date: 2022-12-22 13:38:35.658701

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "29bdb076c853"
down_revision = "1f8a9d811105"
branch_labels = "versions_primary_key"
depends_on = None


def upgrade() -> None:
    op.drop_constraint("user_pkey", "user")
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
    # ### end Alembic commands ###
