from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime, Numeric, SmallInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy_utils import PhoneNumberType, EmailType

from src.infrastructure.drivers.db.tables.base import Base


# Для добавленных ингредиентов
order_item_added_ingredient = Table(
    '__order_item_added_ingredient', Base.metadata,
    Column('order_item_id', Integer, ForeignKey('order_item.id')),
    Column('added_id', Integer, ForeignKey('ingredient.id'))
)

# Для удаленных ингредиентов
order_item_removed_ingredient = Table(
    '__order_item_removed_ingredient', Base.metadata,
    Column('order_item_id', Integer, ForeignKey('order_item.id')),
    Column('removed_id', Integer, ForeignKey('ingredient.id'))
)

# # Связь многие-ко-многим для категорий ресторана
# restaurant_category_association = Table(
#     'restaurant_category', Base.metadata,
#     Column('restaurant_id', Integer, ForeignKey('restaurant.id')),
#     Column('category_id', Integer, ForeignKey('menu_category.id'))
# )

# Связь многие-ко-многим для любимых блюд
user_favorite_association = Table(
    'user_favorite', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('food_id', Integer, ForeignKey('food.id'))
)


category_food_association = Table(
    'category_food', Base.metadata,
    Column('category_id', Integer, ForeignKey('menu_category.id')),
    Column('food_id', Integer, ForeignKey('food.id'))
)

class Restaurant(Base):
    __tablename__ = 'restaurant'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    address: Mapped[str] = mapped_column(String(length=5000), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categories: Mapped[list['MenuCategory']] = relationship('MenuCategory', back_populates='restaurant')  # FK
    orders: Mapped[list['Order']] = relationship('Order', back_populates='restaurant')  # FK


class MenuCategory(Base):
    __tablename__ = 'menu_category'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)  # 'Пицца', 'Напитки' и т.д.
    display_order: Mapped[int] = mapped_column(SmallInteger)  # Порядок отображения в меню
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey('restaurant.id'))

    # Связи
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='categories')
    foods: Mapped[list['Food']] = relationship('Food', secondary=category_food_association, back_populates='categories')


class Food(Base):
    __tablename__ = 'food'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(5000), nullable=True)
    food_type: Mapped[str] = mapped_column(String(200), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ingredient_price_modifier: Mapped[float] = mapped_column(Numeric(2, 4), default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    order_item: Mapped['OrderItem'] = relationship('OrderItem', back_populates='food') # One2One
    category: Mapped[list['MenuCategory']] = relationship('MenuCategory', secondary=category_food_association, back_populates='foods')
    ingredient_associations: Mapped[list['FoodIngredientAssociation']] = relationship(
        back_populates='food',
        cascade='save-update, merge, expunge, delete, delete-orphan',
        passive_deletes=True
    )
    user: Mapped[list['User']] = relationship('User', secondary=user_favorite_association, back_populates='favorites')


class FoodIngredientAssociation(Base):
    __tablename__ = 'food_ingredient'
    
    food_id: Mapped[int] = mapped_column(ForeignKey('food.id'), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredient.id'), primary_key=True)
    is_removable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Связи с основными моделями
    food: Mapped['Food'] = relationship(back_populates='ingredient_associations')
    ingredient: Mapped['Ingredient'] = relationship(back_populates='food_associations')


class Ingredient(Base):
    __tablename__ = 'ingredient'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    food_associations: Mapped[list['FoodIngredientAssociation']] = relationship(
        back_populates='ingredient',
        cascade='save-update, merge, expunge, delete, delete-orphan',
        passive_deletes=True
    )
    added_in_order_items: Mapped[list['OrderItem']] = relationship('OrderItem', secondary=order_item_added_ingredient, back_populates='added_ingredients')
    removed_in_order_items: Mapped[list['OrderItem']] = relationship('OrderItem', secondary=order_item_removed_ingredient, back_populates='removed_ingredients')


class Order(Base):
    __tablename__ = 'order'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey('restaurant.id'))
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_address.id'))
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Связи
    items: Mapped[list['OrderItem']] = relationship('OrderItem', back_populates='order')
    user: Mapped['User'] = relationship('User', back_populates='orders')
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='orders')
    address: Mapped['UserAddress'] = relationship('UserAddress', back_populates='orders')


class OrderItem(Base):
    __tablename__ = 'order'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[int] = mapped_column(Integer, ForeignKey('food.id')) # One2One
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('order.id'))
    final_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Связи
    food: Mapped['Food'] = relationship(back_populates='food')
    order: Mapped[list['Order']] = relationship(back_populates='items')
    added_ingredients: Mapped[list['Ingredient']] = relationship('Ingredient', secondary=order_item_added_ingredient, back_populates='added_in_order_items')
    removed_ingredients: Mapped[list['Ingredient']] = relationship('Ingredient', secondary=order_item_removed_ingredient, back_populates='removed_in_order_items')


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(PhoneNumberType(region='RU'), unique=True)
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False, info={'hidden': True})

    # Связи
    addresses: Mapped[list['UserAddress']] = relationship('UserAddress', back_populates='user')
    favorites: Mapped[list['Food']] = relationship('Food', secondary=user_favorite_association, back_populates='users_favorited')
    orders: Mapped[list['Order']] = relationship('Order', back_populates='user')


class UserAddress(Base):
    __tablename__ = 'user_address'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    address: Mapped[str] = mapped_column(String(1000), nullable=False)
    entrance: Mapped[str] = mapped_column(String(20))
    floor: Mapped[int] = mapped_column(SmallInteger)
    apartment: Mapped[str] = mapped_column(String(20))
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Связи
    user: Mapped['User'] = relationship('User', back_populates='addresses')
    orders: Mapped[list['Order']] = relationship('Order', back_populates='address')
