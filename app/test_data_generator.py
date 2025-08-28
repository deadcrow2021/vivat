import asyncio
import random
import sys
from datetime import time
import json
from typing import List

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
    MenuCategory,
    Food,
    FoodCharacteristic,
    FoodIngredientAssociation,
    FoodVariant,
    Ingredient,
    # User,
    # UserAddress,
)

# Импортируйте все ваши модели здесь

fake = Faker("ru_RU")

container: AsyncContainer = create_container()


async def generate_test_data(session: AsyncSession):
    with open('./test_data_generator.json', 'r') as file:
        json_data = json.loads(file.read())

    # 1. Генерация городов
    cities = [
        City(
            name=fake.city(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
        )
        for _ in range(json_data['city_num'])
    ]
    session.add_all(cities)
    await session.flush()  # Получаем ID

    # 2. Генерация фич
    features = [Feature(name=fake.word(), icon_url=fake.image_url()) for _ in range(json_data['features_num'])]
    session.add_all(features)

    # 3. Генерация ресторанов
    restaurants: list[Restaurant] = []

        # 5. Категории меню
    categories = [
        MenuCategory(
            name=fake.word(),
            display_order=random.randint(1, 999),
        )
        for i in range(json_data['categories_num'])
    ]
    session.add_all(categories)
    await session.flush()

    num_cats = min(len(categories), random.randint(8, 10))
    selected_categories = random.sample(categories, k=num_cats)
    

    for city in cities:
        for _ in range(json_data['restaurants_per_city_num']):
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
            restaurant.menu_categories = selected_categories
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
                closes_at=time(22, 0),
            )
            working_hours.append(wh)
    session.add_all(working_hours)

    # 6. Ингредиенты
    ingredients = [
        Ingredient(
            name=fake.word() + str(random.randint(100, 999)),
            price=round(random.uniform(50, 150), 2),
            is_available=False if random.randint(0, 10) == 1 else True,
            image_url=fake.image_url(),
        )
        for _ in range(json_data['ingredients_num'])
    ]
    session.add_all(ingredients)

    # 7. Характеристики еды
    characteristics = [
        FoodCharacteristic(
            measure_value=f"{random.randint(30, 500)}"
        ) for _ in range(json_data['characteristics_num'])
    ]
    session.add_all(characteristics)

    # 8. Генерация блюд
    foods: List[Food] = []
    for _ in range(json_data['food_num']):
        variants = []
        for _ in range(random.randint(1, 3)):
            variant = FoodVariant(
                price=round(random.uniform(100, 1000), 2),
                ingredient_price_modifier=round(random.uniform(1, 2.0), 4),
            )
            # Правильное присвоение характеристик
            variant.characteristics = [random.choice(characteristics)]
            variants.append(variant)

        food = Food(
            name=fake.sentence(2),
            category_id=random.choice(categories).id,
            image_url=fake.image_url(),
            description=fake.text(),
            measure_name=random.choice(["см", "г", "мл"]),
            variants=variants
        )
        foods.append(food)

    session.add_all(foods)
    await session.flush()

    # 9. Связь блюд с ингредиентами через ассоциацию
    for category in categories:
        num_ingredients = random.randint(3, min(8, len(ingredients)))
        selected_ingredients = random.sample(ingredients, k=num_ingredients)
        
        # Получаем все блюда этой категории
        category_foods = [food for food in foods if food.category_id == category.id]
        
        for food in category_foods:
            for ingredient in selected_ingredients:
                assoc = FoodIngredientAssociation(
                    food_id=food.id,
                    ingredient_id=ingredient.id,
                    is_adding=fake.boolean(),
                    is_removable=fake.boolean(),
                    is_default=fake.boolean()
                )
                session.add(assoc)


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
                await generate_test_data(session)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

        # async with _session() as session:
        #     await generate_test_data(session, num_records=5)

    asyncio.run(main())
