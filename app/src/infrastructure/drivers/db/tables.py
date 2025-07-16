from datetime import datetime, time
from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean, DateTime, Numeric, SmallInteger, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy_utils import PhoneNumberType, EmailType

from src.infrastructure.drivers.db.base import Base


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

# Связь многие-ко-многим для категорий ресторана
restaurant_category_association = Table(
    'restaurant_category', Base.metadata,
    Column('restaurant_id', Integer, ForeignKey('restaurant.id')),
    Column('category_id', Integer, ForeignKey('menu_category.id'))
)

# Связь многие-ко-многим для любимых блюд
user_favorite_association = Table(
    'user_favorite', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('food_id', Integer, ForeignKey('food.id'))
)

restaurant_feature_association = Table(
    'restaurant_feature', Base.metadata,
    Column('restaurant_id', Integer, ForeignKey('restaurant.id')),
    Column('feature_id', Integer, ForeignKey('feature.id'))
)

# Таблица для отключения блюд
restaurant_food_disabled = Table(
    'restaurant_food_disabled', Base.metadata,
    Column('restaurant_id', Integer, ForeignKey('restaurant.id')),
    Column('food_id', Integer, ForeignKey('food.id'))
)


food_characteristic_variant_association = Table(
    'food_characteristic_variant', Base.metadata,
    Column('characteristic_id', Integer, ForeignKey('food_characteristic.id')),
    Column('variant_id', Integer, ForeignKey('food_variant.id'))
)


class City(Base):
    __tablename__ = 'city'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    restaurants: Mapped[list['Restaurant']] = relationship('Restaurant', back_populates='city')
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)  # Широта
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)  # Долгота


class Feature(Base):
    __tablename__ = 'feature'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    restaurant: Mapped[list['Restaurant']] = relationship('Restaurant', secondary=restaurant_feature_association, back_populates='features')


class WorkingHours(Base):
    __tablename__ = 'working_hours'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey('restaurant.id'))
    day_of_week: Mapped[int] = mapped_column(SmallInteger)  # 0-6 (пн-вс)
    # Основное время работы
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)
    # Для перерыва
    break_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    # Связи
    restaurant: Mapped['Restaurant'] = relationship('Restaurant', back_populates='working_hours')


class Restaurant(Base):
    __tablename__ = 'restaurant'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id'))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(PhoneNumberType(region='RU'), unique=False)
    address: Mapped[str] = mapped_column(String(length=5000), nullable=False)

    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)  # Широта
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)  # Долгота
    
    has_delivery: Mapped[bool] = mapped_column(Boolean, default=False) # Есть ли доставка
    has_takeaway: Mapped[bool] = mapped_column(Boolean, default=False) # Есть ли самовывоз
    has_dine_in: Mapped[bool] = mapped_column(Boolean, default=False) # Есть ли еда на месте

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Связи
    city : Mapped['City'] = relationship('City', back_populates='restaurants')
    # FK
    orders: Mapped[list['Order']] = relationship('Order', back_populates='restaurant')  # FK
    working_hours: Mapped[list['WorkingHours']] = relationship('WorkingHours', back_populates='restaurant')  # FK
    # M2M
    categories: Mapped[list['MenuCategory']] = relationship('MenuCategory', secondary=restaurant_category_association, back_populates='restaurants')
    features: Mapped[list['Feature']] = relationship('Features', secondary=restaurant_feature_association, back_populates='restaurants')
    disabled_foods: Mapped[list['Food']] = relationship(secondary=restaurant_food_disabled, back_populates='disabled_in_restaurants')


class MenuCategory(Base):
    __tablename__ = 'menu_category'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)  # 'Пицца', 'Напитки' и т.д.
    display_order: Mapped[int] = mapped_column(SmallInteger)  # Порядок отображения в меню

    # Связи
    restaurant: Mapped[list['Restaurant']] = relationship('Restaurant', secondary=restaurant_category_association, back_populates='categories')
    foods: Mapped[list['Food']] = relationship('Food', back_populates='menu_category')  # FK


class FoodCharacteristic(Base):
    __tablename__ = 'food_characteristic'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measure_value: Mapped[str] = mapped_column(String(200), nullable=True) # Подназвание. Для селектора
                        # на UI (30, 50 (см) и т.д. / Маленькая, Большая и т.д. / 300, 500 (г) и т.д.)
    measure_name: Mapped[str] = mapped_column(String(50), nullable=True) # Единица измерения (см, г, мл, шт и т.д.)


class FoodVariant(Base):
    __tablename__ = 'food_variant'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[int] = mapped_column(ForeignKey('food.id'))
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ingredient_price_modifier: Mapped[float] = mapped_column(Numeric(10, 4), default=1.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    food: Mapped['Food'] = relationship(back_populates='variants')


class Food(Base):
    __tablename__ = 'food'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('menu_category.id'))
    name: Mapped[str] = mapped_column(String(500), nullable=False) # Полное название
    image_url: Mapped[str] = mapped_column(String(2000), nullable=True)
    description: Mapped[str] = mapped_column(String(5000), nullable=True)

    # FK
    variants: Mapped[list['FoodVariant']] = relationship('FoodVariant', back_populates='food')
    category: Mapped['MenuCategory'] = relationship('MenuCategory', back_populates='category')
    # One2One
    order_item: Mapped['OrderItem'] = relationship('OrderItem', back_populates='food') 
    # M2M
    user: Mapped[list['User']] = relationship('User', secondary=user_favorite_association, back_populates='favorites')
    disabled_in_restaurants: Mapped[list['Restaurant']] = relationship(secondary=restaurant_food_disabled, back_populates='disabled_foods')
    ingredient_associations: Mapped[list['FoodIngredientAssociation']] = relationship(
        back_populates='food',
        cascade='save-update, merge, expunge, delete, delete-orphan',
        passive_deletes=True
    )


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
    __tablename__ = 'order_item'
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
