import asyncio
import random
import sys
from datetime import time

from faker import Faker
from dishka import FromDishka, AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from src.ioc.ioc_main import create_container
from src.infrastructure.drivers.db.base import Base  # Импортируйте ваши зависимости
from src.infrastructure.drivers.db.tables import (
    City,
    Feature,
    Restaurant,
    WorkingHours,
    # Food,
    # FoodCharacteristic,
    # FoodIngredientAssociation,
    # FoodVariant,
    # Ingredient,
    # MenuCategory,
    # User,
    # UserAddress,
)

# Импортируйте все ваши модели здесь

fake = Faker("ru_RU")

container: AsyncContainer = create_container()


async def generate_test_data(session: AsyncSession, num_records: int = 10):
    # 1. Генерация городов
    cities = [
        City(
            name=fake.city(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
        )
        for _ in range(1)
    ]
    session.add_all(cities)
    await session.flush()  # Получаем ID

    # 2. Генерация фич
    features = [Feature(name=fake.word(), icon_url=fake.image_url()) for _ in range(10)]
    session.add_all(features)

    # 3. Генерация ресторанов
    restaurants: list[Restaurant] = []

    for city in cities:
        for _ in range(num_records):
            restaurant = Restaurant(
                name=fake.company(),
                phone=fake.phone_number(),
                address=fake.address(),
                city_id=city.id,
                latitude=float(fake.latitude()),
                longitude=float(fake.longitude()),
                has_delivery=fake.boolean(),
                has_takeaway=fake.boolean(),
                has_dine_in=fake.boolean(),
            )
            # Связь M2M с фичами
            restaurant.features = random.sample(features, k=random.randint(3, 8))
            restaurants.append(restaurant)
    session.add_all(restaurants)
    await session.flush()

    # 4. Рабочие часы для ресторанов
    working_hours = []
    for restaurant in restaurants:
        for day in range(7):
            wh = WorkingHours(
                restaurant_id=restaurant.id,
                day_of_week=day,
                opens_at=time(9, 0),
                closes_at=time(23, 0),
            )
            working_hours.append(wh)
    session.add_all(working_hours)

    # # 5. Категории меню
    # categories = [MenuCategory(name=fake.word(), display_order=i) for i in range(10)]
    # session.add_all(categories)
    # session.flush()

    # # Связь M2M: рестораны и категории
    # for restaurant in restaurants:
    #     restaurant.categories = random.sample(categories, k=random.randint(2, 5))

    # # 6. Ингредиенты
    # ingredients = [Ingredient(name=fake.word(), price=round(random.uniform(10, 100), 2)) for _ in range(20)]
    # session.add_all(ingredients)

    # # 7. Характеристики еды
    # characteristics = [
    #     FoodCharacteristic(
    #         measure_value=f"{random.randint(10, 50)}",
    #         measure_name=random.choice(["см", "г", "мл"])
    #     ) for _ in range(15)
    # ]
    # session.add_all(characteristics)

    # # 8. Генерация блюд
    # foods = []
    # for _ in range(num_records * 2):
    #     food = Food(
    #         name=fake.sentence(3),
    #         category_id=random.choice(categories).id,
    #         image_url=fake.image_url(),
    #         description=fake.text()
    #     )
    #     # Варианты блюд
    #     food.variants = [
    #         FoodVariant(
    #             price=round(random.uniform(100, 1000), 2),
    #             ingredient_price_modifier=round(random.uniform(0.5, 2.0), 4)
    #         ) for _ in range(random.randint(1, 3))
    #     ]
    #     # Связь с ингредиентами через ассоциацию
    #     for _ in range(random.randint(3, 8)):
    #         assoc = FoodIngredientAssociation(
    #             ingredient=random.choice(ingredients),
    #             is_removable=fake.boolean(),
    #             is_default=fake.boolean()
    #         )
    #         food.ingredient_associations.append(assoc)
    #     foods.append(food)
    # session.add_all(foods)

    # # 9. Отключение блюд в ресторанах (M2M)
    # for restaurant in restaurants:
    #     restaurant.disabled_foods = random.sample(foods, k=random.randint(1, 3))

    # # 10. Пользователи
    # users = []
    # for _ in range(num_records):
    #     user = User(
    #         name=fake.name(),
    #         phone=fake.unique.phone_number(),
    #         email=fake.unique.email(),
    #         hashed_password=fake.sha256()
    #     )
    #     # Адреса пользователей
    #     user.addresses = [
    #         UserAddress(
    #             address=fake.address(),
    #             entrance=str(random.randint(1, 5)),
    #             floor=random.randint(1, 20),
    #             apartment=str(random.randint(1, 300)),
    #             is_primary=(i == 0)
    #         ) for i in range(random.randint(1, 3))
    #     ]
    #     # Избранные блюда (M2M)
    #     user.favorites = random.sample(foods, k=random.randint(0, 5))
    #     users.append(user)
    # session.add_all(users)
    # session.flush()

    #####

    # # 11. Заказы
    # orders = []
    # for user in users:
    #     for _ in range(random.randint(0, 4)):
    #         order = Order(
    #             user_id=user.id,
    #             restaurant_id=random.choice(restaurants).id,
    #             address_id=random.choice(user.addresses).id,
    #             total_price=0,  # Будет расчитано позже
    #             status=random.choice(["created", "processing", "delivered"])
    #         )
    #         orders.append(order)
    # session.add_all(orders)
    # session.flush()

    # # 12. Позиции заказов
    # order_items = []
    # for order in orders:
    #     total = 0
    #     for _ in range(random.randint(1, 5)):
    #         food = random.choice(foods)
    #         variant = random.choice(food.variants)
    #         item = OrderItem(
    #             food_id=food.id,
    #             order_id=order.id,
    #             final_price=variant.price
    #         )
    #         # Добавленные/удаленные ингредиенты (M2M через ассоциативные таблицы)
    #         all_ingredients = [a.ingredient for a in food.ingredient_associations]

    #         if all_ingredients:
    #             item.added_ingredients = random.sample(all_ingredients, k=random.randint(0, 2))
    #             item.removed_ingredients = random.sample(all_ingredients, k=random.randint(0, 2))

    #             # Корректировка цены
    #             for ingr in item.added_ingredients:
    #                 item.final_price += ingr.price * variant.ingredient_price_modifier
    #             for ingr in item.removed_ingredients:
    #                 item.final_price -= ingr.price * variant.ingredient_price_modifier

    #         total += item.final_price
    #         order_items.append(item)

    #     # Обновляем итоговую цену заказа
    #     order.total_price = round(total, 2)

    # session.add_all(order_items)

    # await session.commit()


# Пример использования
# if __name__ == "__main__":
# Base.metadata.create_all(engine)  # Создать таблицы если их нет
# with session as session:
#     generate_test_data(session, num_records=20)
if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # _session = FromDishka[AsyncSession]

    async def main():
        async with container() as request_container:
            # Получаем зависимости через контейнер
            session = await request_container.get(AsyncSession)

            try:
                await generate_test_data(session, num_records=5)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

        # async with _session() as session:
        #     await generate_test_data(session, num_records=5)

    asyncio.run(main())
