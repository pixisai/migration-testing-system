"""Created products check

Revision ID: af34914e889e
Revises: bf9ab3f3ab73
Create Date: 2022-12-22 12:14:12.263595

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "af34914e889e"
down_revision = "bf9ab3f3ab73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint("ck_product_price", "products", sa.column("price") > 0)
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint("ck_product_price", "products")
    # ### end Alembic commands ###
