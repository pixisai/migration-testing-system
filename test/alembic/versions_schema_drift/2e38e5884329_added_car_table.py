"""Added car table

Revision ID: 2e38e5884329
Revises: 1f8a9d811105
Create Date: 2022-12-12 20:56:10.774889

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2e38e5884329"
down_revision = "1f8a9d811105"
branch_labels = "versions_schema_drift"
depends_on = None


def upgrade() -> None:
    op.create_table(
        "car",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("car", "model")
    # op.drop_table(table_name="car")
    # ### end Alembic commands ###
