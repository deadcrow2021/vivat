"""Add is_banned to user

Revision ID: 3ef45a1ad75d
Revises: 1e0493f0a550
Create Date: 2025-10-13 17:58:58.937713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ef45a1ad75d'
down_revision: Union[str, None] = '1e0493f0a550'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_banned column to user table
    op.add_column('user', sa.Column('is_banned', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_banned column from user table
    op.drop_column('user', 'is_banned')
