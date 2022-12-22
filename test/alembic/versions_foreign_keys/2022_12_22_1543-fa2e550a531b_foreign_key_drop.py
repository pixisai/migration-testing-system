"""Foreign key drop

Revision ID: fa2e550a531b
Revises: 86aa9158e6e0
Create Date: 2022-12-22 15:43:14.172264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa2e550a531b'
down_revision = '86aa9158e6e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fk_user_phone","user")
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
    # ### end Alembic commands ###
