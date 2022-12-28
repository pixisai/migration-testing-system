"""First auto gen

Revision ID: 1f8a9d811105
Revises:
Create Date: 2022-12-02 11:21:44.407525

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1f8a9d811105"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("second_name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="user_pkey"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    # ### end Alembic commands ###
