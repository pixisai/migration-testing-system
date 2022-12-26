"""Foreign Keys

Revision ID: 86aa9158e6e0
Revises: 1f8a9d811105
Create Date: 2022-12-22 13:39:46.195936

"""
import sqlalchemy as sa
from alembic import op
from alembic.op import batch_alter_table

# revision identifiers, used by Alembic.
revision = "86aa9158e6e0"
down_revision = "1f8a9d811105"
branch_labels = "versions_foreign_keys"
depends_on = None


def upgrade() -> None:
    op.create_table(
        "phone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pnone", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("user", sa.Column("phone_id", sa.Integer(), nullable=False))

    with batch_alter_table("user") as batch_op:
        batch_op.create_foreign_key("fk_user_phone", "phone", ["phone_id"], ["id"])

    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint("fk_user_phone", "user")
    op.drop_column("user", "phone_id")
    op.drop_table("phone")
    # ### end Alembic commands ###
