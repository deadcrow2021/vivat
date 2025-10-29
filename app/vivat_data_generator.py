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
)


container: AsyncContainer = create_container()


feature_names = ["Wi-fi", "Мангал меню", "Кондиционер", "Открытая кухня", "Удобная мебель", "Алкоголь", "Оплата картой"]

data = {
    "menu_categories": {
        "Пицца": {
            "display_order": 1,
            "need_addings": True,
            "positions": [
                {
                    "ingredients": ["тунец (консерв.)", "сыр пармезан", "соус томатный", "оливки", "помидоры"],
                    "name": "С тунцом",
                    "prices": (560, 950, 1210),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "соус томатный",
                        "свинина",
                        "буженина",
                        "пепперони",
                        "шампиньоны",
                        "зелень",
                    ],
                    "name": "Маргаритта",
                    "prices": (490, 650, 850),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "соус томатный",
                        "свинина",
                        "буженина",
                        "пепперони",
                        "шампиньоны",
                        "зелень",
                    ],
                    "name": "Vivat",
                    "prices": (690, 950, 1080),
                },
                {"ingredients": ["соус томатный", "4 вида сыра"], "name": "4 сыра", "prices": (560, 950, 1080)},
                {
                    "ingredients": [
                        "соус томатный",
                        "сыр моцарелла",
                        "помидоры",
                        "шампиньоны",
                        "зелень",
                        "болгарский перец",
                    ],
                    "name": "Грибная",
                    "prices": (490, 750, 950),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "соус томатный",
                        "салями",
                        "шампиньоны",
                        "болгарский перец",
                        "кукуруза",
                        "зелень",
                    ],
                    "name": "Антонио",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "ветчина", "шампиньоны", "помидоры"],
                    "name": "Классика",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "буженина", "помидоры", "кукуруза"],
                    "name": "Пикассо",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "помидоры", "ветчина", "шампиньоны"],
                    "name": "Прошутто",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "помидоры", "соус томатный", "курица", "шампиньоны", "зелень"],
                    "name": "Курица с грибами",
                    "prices": (560, 820, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "курица", "ананас"],
                    "name": "Гавайская с курицей",
                    "prices": (560, 820, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "ветчина", "ананас"],
                    "name": "Гавайская с ветчиной",
                    "prices": (560, 820, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "маслины", "морской коктейль", "зелень"],
                    "name": "Морская",
                    "prices": (650, 1010, 1210),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "соус томатный",
                        "салями",
                        "ветчина",
                        "буженина",
                        "курица",
                        "шампиньоны",
                        "болгарский перец",
                    ],
                    "name": "Микс",
                    "prices": (690, 950, 1210),
                },
                {
                    "ingredients": ["сыр пармезан", "соус томатный", "свинина", "помидоры"],
                    "name": "Пармезан",
                    "prices": (690, 820, 1080),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "оливки", "красная рыба", "креветки"],
                    "name": "С красной рыбой",
                    "prices": (890, 1210, 1410),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "болгарский перец"],
                    "name": "Пепперони",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "соус томатный",
                        "помидоры",
                        "кукуруза",
                        "болгарский перец",
                        "шампиньоны",
                        "брокколи",
                        "маслины",
                    ],
                    "name": "Вегетарианская",
                    "prices": (490, 690, 950),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "маслины", "корнишоны"],
                    "name": "Салями",
                    "prices": (560, 750, 950),
                },
                {
                    "ingredients": [
                        "сыр моцарелла",
                        "говядина",
                        "салями",
                        "буженина",
                        "шампиньоны",
                        "соус томатный",
                        "соус терияки",
                        "зелень",
                    ],
                    "name": "Манзо",
                    "prices": (690, 950, 1080),
                },
                {
                    "ingredients": [
                        "говядина",
                        "сыр моцарелла",
                        "сыр пармезан",
                        "помидоры",
                        "соус томатный",
                        "соус терияки",
                        "зелень",
                    ],
                    "name": "Филичи",
                    "prices": (690, 810, 1080),
                },
                {
                    "ingredients": [
                        "груша",
                        "сыр дорблю",
                        "сыр пармезан",
                        "сыр моцарелла",
                        "трюфельное масло",
                        "белый соус",
                    ],
                    "name": "Груша с Дорблю",
                    "prices": (750, 1200, 1400),
                },
            ],
        },
        "Мангал": {"display_order": 2, "need_addings": True, "positions": {"Шаурма с курицей": {"ingredients": []}}},
        "Напитки": {"display_order": 3, "need_addings": False, "positions": {"Чай черный": {"ingredients": []}}},
    }
}

ingredients_data = [
    '4 вида сыра', 'ананас', 'белый соус', 'болгарский перец', 'брокколи',
    'буженина', 'ветчина', 'говядина', 'груша', 'зелень', 'корнишоны', 'красная рыба',
    'креветки', 'кукуруза', 'курица', 'маслины', 'морской коктейль', 'оливки',
    'пепперони', 'помидоры', 'салями', 'свинина', 'соус терияки', 'соус томатный',
    'сыр дорблю', 'сыр моцарелла', 'сыр пармезан', 'трюфельное масло', 'тунец (консерв.)', 'шампиньоны'
]

ingredients_price_data = {
    'сыр моцарелла': 100,
    'сыр пармезан': 100,
    'помидоры': 70,
    'шампиньоны': 70,
    'кукуруза': 70,
    'болгарский перец': 70,
    'салями': 100,
    'ветчина': 100,
    'буженина': 100,
    'курица': 100,
    'креветки': 140,
    'морской коктейль': 200,
    'свинина': 140,
    'ананас': 80,
    'маслины': 80,
    'оливки': 80,
    'зелень': 40,
    'пепперони': 100,
    'красная рыба': 200,
    'говядина': 140,
    'корнишоны': 70,
    'брокколи': 70,
    'груша': 100,
}

restaurants_data = [
    {
        "name": "Виват на ул. Горького",
        "address": "г. Алушта, ул. Горького, 54-А",
        "phone": "+79787048806",
        "coords": (44.673718, 34.404694),
    },
    {
        "name": "Мангал Виват на Набережной",
        "address": "г. Алушта, ул. Ленина, 13Д",
        "phone": "+79786247915",
        "coords": (44.669978, 34.413874),
    },
]


async def generate_data(session: AsyncSession):
    cities = [City(name="Алушта", latitude=44.673718, longitude=34.404694)]
    session.add_all(cities)
    await session.flush()

    # 2. Генерация фич
    features = [Feature(name=name, icon_url="/") for name in feature_names]
    session.add_all(features)

    restaurants: list[Restaurant] = []

    categories = [
        MenuCategory(name=category, display_order=data["menu_categories"][category]["display_order"])
        for category in data["menu_categories"]
    ]
    session.add_all(categories)
    await session.flush()

    for city in cities:
        for rest in restaurants_data:
            restaurant = Restaurant(
                name=rest["name"],
                phone=rest["phone"],
                address=rest["address"],
                city_id=city.id,
                latitude=rest["coords"][0],
                longitude=rest["coords"][1],
                has_delivery=True,
                has_takeaway=True,
                has_dine_in=True,
            )
            # Связь M2M с фичами
            restaurant.features = features
            restaurant.menu_categories = categories
            restaurants.append(restaurant)
    session.add_all(restaurants)
    await session.flush()

    # 4. Рабочие часы для ресторанов
    working_hours = []
    for restaurant in restaurants:
        for day in range(7):
            wh = WorkingHours(restaurant_id=restaurant.id, day_of_week=day, opens_at=time(9, 0), closes_at=time(22, 0))
            working_hours.append(wh)
    session.add_all(working_hours)

    # 6. Ингредиенты
    ingredients: List[Ingredient] = []

    for ingredient in ingredients_data:
        ingredients.append(
            Ingredient(
                name=ingredient.capitalize(),
                price=ingredients_price_data[ingredient] if ingredient in ingredients_price_data else 99,
                is_available=True,
                image_url="/",
            )
        )
    session.add_all(ingredients)

    # 7. Характеристики еды
    characteristics = [FoodCharacteristic(measure_value=f"{value}") for value in (32, 40, 50)]
    session.add_all(characteristics)

    # 8. Генерация блюд
    foods: List[Food] = []
    modifiers = (1.0, 2.0, 3.0)

    pizza_positions = data["menu_categories"]["Пицца"]["positions"]
    for position in pizza_positions:
        variants = []

        for i in range(3):
            variant = FoodVariant(price=position["prices"][i], ingredient_price_modifier=modifiers[i])
            # Правильное присвоение характеристик
            variant.characteristics = [characteristics[i]]
            variants.append(variant)

        food = Food(
            name=position["name"],
            category_id=categories[0].id,
            image_url="/",
            description=None,
            measure_name="см",
            variants=variants,
        )
        foods.append(food)

    session.add_all(foods)
    await session.flush()

    # 9. Связь блюд с ингредиентами через ассоциацию
    for category in categories:
        # Получаем все блюда этой категории
        category_foods = [food for food in foods if food.category_id == category.id]

        for food in category_foods:
            food_ingredients = [position for position in pizza_positions if position["name"] == food.name][0][
                "ingredients"
            ]
            selected_ingredients: List[Ingredient] = []

            for ingredient in ingredients:
                if ingredient.name.lower() in food_ingredients:
                    selected_ingredients.append(ingredient)

            for ingredient in selected_ingredients:
                assoc = FoodIngredientAssociation(
                    food_id=food.id,
                    ingredient_id=ingredient.id,
                    is_adding=True if ingredient.name.lower() in ingredients_price_data else False,
                    is_default=True,
                )
                session.add(assoc)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def main():
        async with container() as request_container:
            # Получаем зависимости через контейнер
            session = await request_container.get(AsyncSession)

            try:
                await generate_data(session)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    asyncio.run(main())
