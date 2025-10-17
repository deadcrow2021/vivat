from datetime import datetime, time
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    Boolean,
    DateTime,
    Numeric,
    SmallInteger,
    Time,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy_utils import PhoneNumberType, EmailType
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from src.domain.dto.order_dto import OrderAction, OrderStatus
from src.infrastructure.drivers.db.base import Base
from src.config import ArgonConfig


# Для добавленных ингредиентов
order_item_added_ingredient = Table(
    "__order_item_added_ingredient",
    Base.metadata,
    Column("order_item_id", Integer, ForeignKey("order_item.id", ondelete="CASCADE")),
    Column("added_id", Integer, ForeignKey("ingredient.id", ondelete="CASCADE")),
)

# Для удаленных ингредиентов
order_item_removed_ingredient = Table(
    "__order_item_removed_ingredient",
    Base.metadata,
    Column("order_item_id", Integer, ForeignKey("order_item.id", ondelete="CASCADE")),
    Column("removed_id", Integer, ForeignKey("ingredient.id", ondelete="CASCADE")),
)

# Связь многие-ко-многим для категорий ресторана
restaurant_category_association = Table(
    "restaurant_category",
    Base.metadata,
    Column("restaurant_id", Integer, ForeignKey("restaurant.id", ondelete="CASCADE")),
    Column("category_id", Integer, ForeignKey("menu_category.id", ondelete="CASCADE")),
)

# Связь многие-ко-многим для любимых блюд
user_favorite_association = Table(
    "user_favorite",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE")),
    Column("food_id", Integer, ForeignKey("food.id", ondelete="CASCADE")),
)

restaurant_feature_association = Table(
    "restaurant_feature",
    Base.metadata,
    Column("restaurant_id", Integer, ForeignKey("restaurant.id", ondelete="CASCADE")),
    Column("feature_id", Integer, ForeignKey("feature.id", ondelete="CASCADE")),
)

# Связь многие-ко-многим для ресторанов и телеграм-чатов
restaurant_telegram_chat_association = Table(
    "restaurant_telegram_chat",
    Base.metadata,
    Column("restaurant_id", Integer, ForeignKey("restaurant.id", ondelete="CASCADE")),
    Column("chat_id", Integer, ForeignKey("telegram_chat.id", ondelete="CASCADE")),
)

# Таблица для отключения блюд
restaurant_food_disabled = Table(
    "restaurant_food_disabled",
    Base.metadata,
    Column("restaurant_id", Integer, ForeignKey("restaurant.id", ondelete="CASCADE")),
    Column("food_id", Integer, ForeignKey("food.id", ondelete="CASCADE")),
)


food_characteristic_variant_association = Table(
    "food_characteristic_variant",
    Base.metadata,
    Column(
        "characteristic_id",
        Integer,
        ForeignKey("food_characteristic.id", ondelete="CASCADE"),
    ),
    Column("variant_id", Integer, ForeignKey("food_variant.id", ondelete="CASCADE")),
)


class City(Base):
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(9, 6), nullable=True
    )  # Широта
    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(9, 6), nullable=True
    )  # Долгота

    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant", back_populates="city", cascade="all, delete-orphan"
    )


class Feature(Base):
    __tablename__ = "feature"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        secondary=restaurant_feature_association,
        back_populates="features",
    )


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurant.id", ondelete="CASCADE")
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger)  # 0-6 (пн-вс)
    # Основное время работы
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)
    # Для перерыва
    break_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    is_holiday: Mapped[bool] = mapped_column(Boolean, default=False, server_default='true')
    # Связи
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="working_hours"
    )


class Restaurant(Base):
    __tablename__ = "restaurant"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(PhoneNumberType(region="RU"), unique=False)
    address: Mapped[str] = mapped_column(String(length=5000), nullable=False)

    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(9, 6), nullable=True
    )  # Широта
    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(9, 6), nullable=True
    )  # Долгота

    has_delivery: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Есть ли доставка
    has_takeaway: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Есть ли самовывоз
    has_dine_in: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Есть ли еда на месте

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Связи
    city: Mapped["City"] = relationship("City", back_populates="restaurants")
    # FK
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="restaurant"
    )  # FK
    working_hours: Mapped[list["WorkingHours"]] = relationship(
        "WorkingHours", back_populates="restaurant", cascade="all, delete-orphan"
    )  # FK
    # M2M
    menu_categories: Mapped[list["MenuCategory"]] = relationship(
        "MenuCategory",
        secondary=restaurant_category_association,
        back_populates="restaurants",
        lazy="selectin"
    )
    features: Mapped[list["Feature"]] = relationship(
        "Feature",
        secondary=restaurant_feature_association,
        back_populates="restaurants",
    )
    disabled_foods: Mapped[list["Food"]] = relationship(
        secondary=restaurant_food_disabled, back_populates="disabled_in_restaurants"
    )
    telegram_chats: Mapped[list["TelegramChat"]] = relationship(
        "TelegramChat",
        secondary=restaurant_telegram_chat_association,
        back_populates="restaurants",
    )


class MenuCategory(Base):
    __tablename__ = "menu_category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # 'Пицца', 'Напитки' и т.д.
    display_order: Mapped[int] = mapped_column(
        SmallInteger
    )  # Порядок отображения в меню
    need_addings: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    # Связи
    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        secondary=restaurant_category_association,
        back_populates="menu_categories",
    )
    foods: Mapped[list["Food"]] = relationship(
        "Food", back_populates="menu_category"
    )  # FK


class Food(Base):
    __tablename__ = "food"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("menu_category.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)  # Полное название
    image_url: Mapped[str] = mapped_column(String(2000), nullable=True)
    description: Mapped[str] = mapped_column(String(5000), nullable=True)
    measure_name: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # Единица измерения (см, г, мл)
    # is_removed Не нужен, так как опираемся на FoodVariant

    # FK
    variants: Mapped[list["FoodVariant"]] = relationship(
        "FoodVariant", back_populates="food", cascade="all, delete-orphan"
    )
    menu_category: Mapped["MenuCategory"] = relationship(
        "MenuCategory", back_populates="foods"
    )
    # M2M
    users: Mapped[list["User"]] = relationship(
        "User", secondary=user_favorite_association, back_populates="favorites"
    )
    disabled_in_restaurants: Mapped[list["Restaurant"]] = relationship(
        secondary=restaurant_food_disabled, back_populates="disabled_foods"
    )
    ingredient_associations: Mapped[list["FoodIngredientAssociation"]] = relationship(
        back_populates="food",
        cascade="save-update, merge, expunge, delete, delete-orphan",
        passive_deletes=True,
    )


class FoodVariant(Base):
    __tablename__ = "food_variant"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_id: Mapped[int] = mapped_column(ForeignKey("food.id", ondelete="CASCADE"))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredient_price_modifier: Mapped[float] = mapped_column(
        Numeric(10, 4), default=1.0
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    food: Mapped["Food"] = relationship(back_populates="variants")
    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="food_variant")
    characteristics: Mapped[list["FoodCharacteristic"]] = relationship(
        "FoodCharacteristic",
        secondary=food_characteristic_variant_association,
        back_populates="variants",
    )


class FoodCharacteristic(Base):
    __tablename__ = "food_characteristic"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measure_value: Mapped[str] = mapped_column(
        String(200), nullable=True
    )  # Подназвание. Для селектора
    # на UI (30, 50 (см) и т.д. / Маленькая, Большая и т.д. / 300, 500 (г) и т.д.)
    variants: Mapped[list["FoodVariant"]] = relationship(
        "FoodVariant",
        secondary=food_characteristic_variant_association,
        back_populates="characteristics",
    )


class FoodIngredientAssociation(Base):
    __tablename__ = "food_ingredient"

    food_id: Mapped[int] = mapped_column(
        ForeignKey("food.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredient.id", ondelete="CASCADE"), primary_key=True
    )
    is_adding: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # is_removable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Связи с основными моделями
    food: Mapped["Food"] = relationship(back_populates="ingredient_associations")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="food_associations")


class Ingredient(Base):
    __tablename__ = "ingredient"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url : Mapped[str] = mapped_column(String(2000), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    food_associations: Mapped[list["FoodIngredientAssociation"]] = relationship(
        back_populates="ingredient",
        cascade="save-update, merge, expunge, delete, delete-orphan",
        passive_deletes=True,
    )
    added_in_order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        secondary=order_item_added_ingredient,
        back_populates="added_ingredients",
    )
    removed_in_order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        secondary=order_item_removed_ingredient,
        back_populates="removed_ingredients",
    )


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="RESTRICT")
    )
    restaurant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("restaurant.id", ondelete="SET NULL"), nullable=True
    )
    address_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user_address.id", ondelete="RESTRICT"),
        nullable=True
    )
    order_action: Mapped[OrderAction] = mapped_column(
        SQLEnum(
            OrderAction,
            createnative_enum=True,
            name="order_action_enum",
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=OrderAction.UNKNOWN
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(
            OrderStatus,
            createnative_enum=True,
            name="order_status_enum",
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=OrderStatus.CREATED
    )
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Связи
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship("User", back_populates="orders")
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="orders"
    )
    address: Mapped["UserAddress"] = relationship(
        "UserAddress", back_populates="orders"
    )


class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    food_variant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("food_variant.id", ondelete="RESTRICT")
    )  # One2One
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("order.id", ondelete="CASCADE")
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    final_price: Mapped[int] = mapped_column(Integer, nullable=False) # price for one item with addings

    # Связи
    food_variant: Mapped["FoodVariant"] = relationship(back_populates="order_item")
    order: Mapped["Order"] = relationship(back_populates="items")
    added_ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        secondary=order_item_added_ingredient,
        back_populates="added_in_order_items",
    )
    removed_ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        secondary=order_item_removed_ingredient,
        back_populates="removed_in_order_items",
    )


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=True)
    phone: Mapped[str] = mapped_column(PhoneNumberType(region="RU"), unique=True)
    email: Mapped[str] = mapped_column(EmailType, unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(
        String(), nullable=False, info={"hidden": True}
    )
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    addresses: Mapped[list["UserAddress"]] = relationship(
        "UserAddress", back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Food"]] = relationship(
        "Food", secondary=user_favorite_association, back_populates="users"
    )
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, password: str, argon_config: ArgonConfig):
        """Установка пароля с использованием Argon2"""

        ph = PasswordHasher(
            time_cost=argon_config.argon2_time_cost,
            memory_cost=argon_config.argon2_memory_cost,
            parallelism=argon_config.argon2_parallelism,
        )
        self.hashed_password = ph.hash(password)

    def check_password(self, password: str) -> bool:
        """Проверка пароля с защитой от атак по времени"""
        if not self.hashed_password:
            return False
        try:
            ph = PasswordHasher()
            return ph.verify(self.hashed_password, password)
        except (VerifyMismatchError, InvalidHashError):
            return False
    
    def needs_rehash(self) -> bool:
        """Проверка, нужно ли перехешировать пароль (при изменении параметров)"""
        ph = PasswordHasher()
        return ph.check_needs_rehash(self.hashed_password)


class UserAddress(Base):
    __tablename__ = "user_address"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )
    address: Mapped[str] = mapped_column(String(1000))
    entrance: Mapped[str] = mapped_column(String(20), nullable=True)
    floor: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    apartment: Mapped[str] = mapped_column(String(20), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # TODO: возможно добавить логику

    # Связи
    user: Mapped["User"] = relationship("User", back_populates="addresses")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="address")

    def get_full_address(self) -> str:
        address_parts = [
            ("Адрес: " + self.address) if self.address else '',
            "Вход: " + self.entrance if self.entrance else '',
            "Этаж: " + self.floor if self.floor else '',
            "Квартира: " + self.apartment if self.apartment else '',
        ]
        return ', '.join(x for x in address_parts if x)


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    # Связи
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


class TelegramChat(Base):
    __tablename__ = "telegram_chat"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), default="telegram")
    chat_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    restaurants: Mapped[list["Restaurant"]] = relationship(
        "Restaurant",
        secondary=restaurant_telegram_chat_association,
        back_populates="telegram_chats",
    )
