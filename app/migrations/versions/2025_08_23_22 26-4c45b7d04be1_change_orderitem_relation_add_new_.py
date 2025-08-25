"""Change OrderItem relation, add new columns

Revision ID: 4c45b7d04be1
Revises: cbede47f7bc9
Create Date: 2025-08-23 22:26:06.669146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c45b7d04be1'
down_revision: Union[str, None] = 'cbede47f7bc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Сначала создаем ENUM тип
    order_action_enum = sa.Enum('unknown', 'delivery', 'takeaway', 'inside', name='order_action_enum')
    order_action_enum.create(op.get_bind())
    
    # Затем добавляем колонку с этим типом
    op.add_column('order', sa.Column('order_action', order_action_enum, nullable=False, server_default='unknown'))
    
    # Остальные изменения
    op.add_column('food_ingredient', sa.Column('is_adding', sa.Boolean(), nullable=False))
    op.add_column('order_item', sa.Column('food_variant_id', sa.Integer(), nullable=False))
    op.drop_constraint('order_item_food_id_fkey', 'order_item', type_='foreignkey')
    op.create_foreign_key('order_item_food_variant_id_fkey', 'order_item', 'food_variant', ['food_variant_id'], ['id'], ondelete='RESTRICT')
    op.drop_column('order_item', 'food_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем колонку
    op.drop_column('order', 'order_action')
    
    # Удаляем ENUM тип
    order_action_enum = sa.Enum('unknown', 'delivery', 'takeaway', 'inside', name='order_action_enum')
    order_action_enum.drop(op.get_bind())
    
    # Остальные откаты
    op.add_column('order_item', sa.Column('food_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint('order_item_food_variant_id_fkey', 'order_item', type_='foreignkey')
    op.create_foreign_key('order_item_food_id_fkey', 'order_item', 'food', ['food_id'], ['id'], ondelete='RESTRICT')
    op.drop_column('order_item', 'food_variant_id')
    op.drop_column('food_ingredient', 'is_adding')