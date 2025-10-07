"""Add in_delivery status

Revision ID: 1e0493f0a550
Revises: b6e99bc0da7c
Create Date: 2025-10-07 21:50:04.857258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e0493f0a550'
down_revision: Union[str, None] = 'b6e99bc0da7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Переименовываем старый enum
    op.execute("ALTER TYPE order_status_enum RENAME TO order_status_enum_old")

    # Создаем новый enum с правильными значениями
    order_status_enum = sa.Enum('created', 'in_progress', 'in_delivery', 'done', 'cancelled', name='order_status_enum')
    order_status_enum.create(op.get_bind())

    # Конвертируем существующие данные
    op.execute('''
        ALTER TABLE "order" 
        ALTER COLUMN status TYPE order_status_enum 
        USING CASE 
            WHEN status = 'created' THEN 'created'::order_status_enum
            WHEN status = 'in_progress' THEN 'in_progress'::order_status_enum
            WHEN status = 'done' THEN 'done'::order_status_enum
            WHEN status = 'cancelled' THEN 'cancelled'::order_status_enum
            ELSE 'created'::order_status_enum
        END
    ''')

    # Удаляем старый enum
    op.execute('DROP TYPE order_status_enum_old')


def downgrade() -> None:
    # Возвращаемся к старому enum
    op.execute("ALTER TYPE order_status_enum RENAME TO order_status_enum_old")
    
    # Создаем старый enum
    order_status_enum = sa.Enum('created', 'in_progress', 'done', 'cancelled', name='order_status_enum')
    order_status_enum.create(op.get_bind())
    
    # Конвертируем данные обратно
    op.execute('''
        ALTER TABLE "order" 
        ALTER COLUMN status TYPE order_status_enum 
        USING CASE 
            WHEN status = 'created' THEN 'created'::order_status_enum
            WHEN status = 'in_progress' THEN 'in_progress'::order_status_enum
            WHEN status = 'in_delivery' THEN 'done'::order_status_enum  -- преобразуем in_delivery в done
            WHEN status = 'done' THEN 'done'::order_status_enum
            WHEN status = 'cancelled' THEN 'cancelled'::order_status_enum
            ELSE 'created'::order_status_enum
        END
    ''')
    
    op.execute('DROP TYPE order_status_enum_old')
