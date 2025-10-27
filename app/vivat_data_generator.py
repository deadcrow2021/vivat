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
                    "ingredients": ["тунец (консервированный)", "пармезан", "соус томатный", "оливки", "помидоры"],
                    "name": "С тунцом",
                    'prices': (560, 950, 1210)
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "помидоры", "зелень"],
                    "name": "Маргаритта"
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
                },
                {
                    "ingredients": ["сыр моцарелла", "сыр пармезан", "сыр гуда", "сыр эдам"],
                    "name": "4 сыра"
                },
                {
                    "ingredients": ["шампиньоны", "зелень", "болгарский перец"],
                    "name": "Грибная"
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
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "ветчина", "шампиньоны", "помидоры"],
                    "name": "Классика",
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "буженина", "помидоры", "кукуруза"],
                    "name": "Пикассо",
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "помидоры", "ветчина", "шампиньоны"],
                    "name": "Прошутто",
                },
                {
                    "ingredients": ["сыр моцарелла", "помидоры", "соус томатный", "курица", "шампиньоны"],
                    "name": "Курица с грибами",
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "курица", "ананас"],
                    "name": "Гавайская с курицей"    
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "ветчина", "ананас"],
                    "name": "Гавайская с ветчиной",
                },
                {
                    "ingredients": ["маслины", "морской коктейль (осьминог", "мидии", "креветки", "кальмар)"],
                    "name": "Морская",
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
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "свинина", "помидоры"],
                    "name": "Пармезан"
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "оливки", "красная рыба (семга)", "креветки"],
                    "name": "С красной рыбой",
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "пепперони", "болгарский перец"],
                    "name": "Пепперони",
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
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "маслины"],
                    "name": "Салями"    
                },
                {
                    "ingredients": [
                        "говядина",
                        "салями",
                        "буженина",
                        "шампиньоны",
                        "соус томатный",
                        "соус терияки",
                        "зелень",
                    ],
                    "name": "Манзо",
                },
                {
                    "ingredients": [
                        "говядина",
                        "сыр моцарелла",
                        "пармезан",
                        "помидоры",
                        "соус томатный",
                        "соус терияки",
                        "зелень",
                    ],
                    "name": "Филичи",
                },
                {
                    "ingredients": [
                        "груша",
                        "сыр дорблю",
                        "пармезан",
                        "сыр моцарелла",
                        "трюфельное масло",
                        "белый соус",
                    ],
                    "name": "Груша с Дорблю",
                },
            ],
        },
        "Мангал": {"display_order": 2, "need_addings": True, "positions": {"Шаурма с курицей": {"ingredients": []}}},
        "Напитки": {"display_order": 3, "need_addings": False, "positions": {"Чай черный": {"ingredients": []}}},
    }
}

ingredients_data = [
    'ананас', 'белый соус', 'болгарский перец', 'брокколи', 'буженина',
    'ветчина', 'говядина', 'груша', 'сыр гуда', 'сыр дорблю', 'зелень',
    'красная рыба (семга)', 'креветки', 'кукуруза', 'курица', 'маслины',
    'морской коктейль (осьминог, мидии, креветки, кальмар)', 'оливки', 'сыр пармезан',
    'пепперони', 'помидоры', 'салями', 'свинина', 'соус терияки', 'соус томатный',
    'сыр моцарелла', 'трюфельное масло', 'тунец', 'шампиньоны', 'сыр эдам'
]

ingredients_price_data = {
    'ананас': 80,
    'пепперони': 100,
    'сыр моцарелла': 100,
    'помидоры': 70,
    'шампиньоны': 70,
    'кукуруза': 70,
    'болгарский перец': 70,
    'салями': 100,
    'ветчина': 100,
    'буженина': 100,
    'курица': 100,
    'красная рыба (семга)': 200,
    'креветки': 140,
    'свинина': 140,
    'говядина': 140,
    'зелень': 40,
    'маслины': 80,
    'оливки': 80,
    'морской коктейль (осьминог, мидии, креветки, кальмар)': 200,
}

restaurants_data = [
    {
        "name": "Виват на ул. Горького",
        "address": "г. Алушта, ул. Горького, 54-А",
        "phone": "+79787048806",
        "coords": (44.673718, 34.404694),
    },
    {
        "name": "Виват на Набережной",
        "address": "г. Алушта, ул. Ленина, 13Д",
        "phone": "+79787048806",
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
        MenuCategory(
            name=category,
            display_order=data["menu_categories"][category]["display_order"]
        )
        for category in range(data["menu_categories"])
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
                price=ingredients_price_data[ingredient],
                is_available=True,
                image_url='/',
            )
        )
    session.add_all(ingredients)

    # 7. Характеристики еды
    characteristics = [
        FoodCharacteristic(
            measure_value=f"{value}"
        ) for value in (32, 40, 50)
    ]
    session.add_all(characteristics)
    
    # 8. Генерация блюд
    foods: List[Food] = []
    modifiers = (1.0, 2.0, 3.0)

    pizza_positions = data['menu_categories']['Пицца']['positions']
    for position in pizza_positions:
        variants = []

        for i in range(3):
            variant = FoodVariant(
                price=position['prices'][i],
                ingredient_price_modifier=modifiers[i],
            )
            # Правильное присвоение характеристик
            variant.characteristics = characteristics[i]
            variants.append(variant)

        food = Food(
            name=position['name'],
            category_id=categories[0].id,
            image_url='/',
            description=None,
            measure_name="см",
            variants=variants
        )
        foods.append(food)

    session.add_all(foods)
    await session.flush()

    # 9. Связь блюд с ингредиентами через ассоциацию
    for category in categories:
        # Получаем все блюда этой категории
        category_foods = [food for food in foods if food.category_id == category.id]

        for food in category_foods:
            food_ingredients = pizza_positions['ingredients']
            selected_ingredients = [
                ingredient for ingredient in ingredients
                if ingredient.name in food_ingredients
            ]

            for ingredient in selected_ingredients:
                assoc = FoodIngredientAssociation(
                    food_id=food.id,
                    ingredient_id=ingredient.id,
                    is_adding=True if ingredient.name in ingredients_price_data else False,
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