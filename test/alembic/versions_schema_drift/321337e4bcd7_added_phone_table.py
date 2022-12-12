"""Added phone table

Revision ID: 321337e4bcd7
Revises: 2e38e5884329
Create Date: 2022-12-12 20:58:35.843291

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "321337e4bcd7"
down_revision = "2e38e5884329"
branch_labels = "versions_schema_drift"
depends_on = None


def upgrade() -> None:
    op.create_table(
        "phone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pnone", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("user", sa.Column("phone_id", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column("user", "phone_id")
    # ### end Alembic commands ###
