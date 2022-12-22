"""Added car table

Revision ID: 5e38e5884320
Revises: 1f8a9d811105
Create Date: 2022-12-22 12:55:21.121045
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5e38e5884320"
down_revision = "1f8a9d811105"
branch_labels = "versions_check_nullable"
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "car",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column('user', 'first_name', nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("car")
    # ### end Alembic commands ###
