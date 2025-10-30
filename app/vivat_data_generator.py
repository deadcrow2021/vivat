import asyncio
import random
import sys
from datetime import time
import json
from typing import Dict, List, Set

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
            "measure_name": "см",
            "measure_values": (32, 40, 50),
            "addings": set(
                (
                    "сыр моцарелла",
                    "сыр пармезан",
                    "помидоры",
                    "шампиньоны",
                    "кукуруза",
                    "болгарский перец",
                    "салями",
                    "ветчина",
                    "буженина",
                    "курица",
                    "креветки",
                    "морской коктейль",
                    "свинина",
                    "ананас",
                    "маслины",
                    "оливки",
                    "зелень",
                    "пепперони",
                    "красная рыба",
                    "говядина",
                    "корнишоны",
                    "брокколи",
                    "груша",
                )
            ),
            "positions": [
                {
                    "ingredients": ["тунец (консерв.)", "сыр пармезан", "соус томатный", "оливки", "помидоры"],
                    "name": "С тунцом",
                    "prices": (560, 950, 1210),
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["соус томатный", "4 вида сыра"],
                    "name": "4 сыра",
                    "prices": (560, 950, 1080),
                    "measure_values": (32, 40, 50),
                },
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
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "ветчина", "шампиньоны", "помидоры"],
                    "name": "Классика",
                    "prices": (560, 750, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "буженина", "помидоры", "кукуруза"],
                    "name": "Пикассо",
                    "prices": (560, 750, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "помидоры", "ветчина", "шампиньоны"],
                    "name": "Прошутто",
                    "prices": (560, 750, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "помидоры", "соус томатный", "курица", "шампиньоны", "зелень"],
                    "name": "Курица с грибами",
                    "prices": (560, 820, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "курица", "ананас"],
                    "name": "Гавайская с курицей",
                    "prices": (560, 820, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "ветчина", "ананас"],
                    "name": "Гавайская с ветчиной",
                    "prices": (560, 820, 950),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "маслины", "морской коктейль", "зелень"],
                    "name": "Морская",
                    "prices": (650, 1010, 1210),
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр пармезан", "соус томатный", "свинина", "помидоры"],
                    "name": "Пармезан",
                    "prices": (690, 820, 1080),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "оливки", "красная рыба", "креветки"],
                    "name": "С красной рыбой",
                    "prices": (890, 1210, 1410),
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "болгарский перец"],
                    "name": "Пепперони",
                    "prices": (560, 750, 950),
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
                },
                {
                    "ingredients": ["сыр моцарелла", "соус томатный", "салями", "маслины", "корнишоны"],
                    "name": "Салями",
                    "prices": (560, 750, 950),
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
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
                    "measure_values": (32, 40, 50),
                },
            ],
        },
        "Шаурма": {
            "display_order": 2,
            "need_addings": True,
            "measure_name": "шт",
            "addings": set(("сыр", "халапеньо")),
            "positions": [
                {
                    "ingredients": ["курица", "соус красный", "соус сметанный", "помидоры", "овощной салат"],
                    "name": "Шаурма с курицей",
                    "prices": (300,),
                    "measure_values": (1,),
                },
                {
                    "ingredients": ["свинина", "соус красный", "соус сметанный", "помидоры", "овощной салат"],
                    "name": "Шаурма со свининой",
                    "prices": (350,),
                    "measure_values": (1,),
                },
                {
                    "ingredients": ["говядина", "соус красный", "соус сметанный", "помидоры", "овощной салат"],
                    "name": "Шаурма с говядиной",
                    "prices": (450,),
                    "measure_values": (1,),
                },
                {
                    "ingredients": ["люля-кебаб", "соус красный", "соус сметанный", "помидоры", "овощной салат"],
                    "name": "Шаурма с люля-кебабом",
                    "prices": (400,),
                    "measure_values": (1,),
                },
                {
                    "ingredients": ["соус красный", "соус сметанный", "помидоры", "овощной салат"],
                    "name": "Шаурма вегетарианская",
                    "prices": (200,),
                    "measure_values": (1,),
                },
            ],
        },
        "Шашлык": {
            "display_order": 3,
            "need_addings": False,
            "measure_name": "г",
            "addings": set(),
            "positions": [
                {
                    "ingredients": ["баранина", "соус шашлычный", "маринованный лук", "лаваш"],
                    "name": "Шашлык из баранины",
                    "prices": (400,),
                    "measure_values": (100,),
                },
                {
                    "ingredients": ["курица", "соус шашлычный", "маринованный лук", "лаваш"],
                    "name": "Шашлык из курицы",
                    "prices": (200,),
                    "measure_values": (100,),
                },
                {
                    "ingredients": ["свинина", "соус шашлычный", "маринованный лук", "лаваш"],
                    "name": "Шашлык из свинины",
                    "prices": (240,),
                    "measure_values": (100,),
                },
                {
                    "ingredients": ["говядина", "соус шашлычный", "маринованный лук", "лаваш"],
                    "name": "Шашлык из говядины",
                    "prices": (350,),
                    "measure_values": (100,),
                },
                {
                    "ingredients": ["люля-кебаб", "соус шашлычный", "маринованный лук", "лаваш"],
                    "name": "Люля-кебаб",
                    "prices": (300,),
                    "measure_values": (100,),
                },
            ],
        },
        "Овощи гриль": {
            "display_order": 4,
            "need_addings": False,
            "measure_name": "г",
            "addings": set(),
            "positions": [
                {
                    "ingredients": ["картофель", "сало", "лаваш"],
                    "name": "Картошка с салом",
                    "prices": (130,),
                    "measure_values": (120,),
                }
            ],
        },
        "Напитки": {
            "display_order": 5,
            "need_addings": False,
            "measure_name": "мл",
            "addings": set(),
            "positions": [
                {
                    "ingredients": [],
                    "name": "Кола",
                    "prices": (150,),
                    "measure_values": (500,),
                },
                {
                    "ingredients": [],
                    "name": "Фанта",
                    "prices": (150,),
                    "measure_values": (500,),
                },
                {
                    "ingredients": [],
                    "name": "Спрайт",
                    "prices": (150,),
                    "measure_values": (500,),
                },
            ],
        },
    }
}

modifiers = (1.0, 2.0, 3.0)

# Собираю все возможные *ингредиенты*
ingredients_data: Set[str] = set()

# Собираю все возможные *единицы измерения* для характеристик
characteristics_data: Set[str] = set()

for category in data["menu_categories"]:
    for position in data["menu_categories"][category]["positions"]:

        for ingredient in position["ingredients"]:
            ingredients_data.add(ingredient)

        for value in position["measure_values"]:
            characteristics_data.add(str(value))


addings_price_data = {
    "сыр моцарелла": 100,
    "сыр пармезан": 100,
    "помидоры": 70,
    "шампиньоны": 70,
    "кукуруза": 70,
    "болгарский перец": 70,
    "салями": 100,
    "ветчина": 100,
    "буженина": 100,
    "курица": 100,
    "креветки": 140,
    "морской коктейль": 200,
    "свинина": 140,
    "ананас": 80,
    "маслины": 80,
    "оливки": 80,
    "зелень": 40,
    "пепперони": 100,
    "красная рыба": 200,
    "говядина": 140,
    "корнишоны": 70,
    "брокколи": 70,
    "груша": 100,

    "сыр": 50,
    "халапеньо": 30,
}

for adding in addings_price_data:
    ingredients_data.add(adding)


restaurants_data = [
    {
        "name": "Виват на ул. Горького",
        "address": "г. Алушта, ул. Горького, 54-А",
        "phone": "+79787048806",
        "coords": (44.673718, 34.404694),
        "delivery_price": 0
    },
    {
        "name": "Мангал Виват на Набережной",
        "address": "г. Алушта, ул. Ленина, 13Д",
        "phone": "+79786247915",
        "coords": (44.669978, 34.413874),
        "delivery_price": 100
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
            display_order=data["menu_categories"][category]["display_order"],
            need_addings=data["menu_categories"][category]["need_addings"],
        )
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
                delivery_price=rest["delivery_price"]
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
            wh = WorkingHours(
                restaurant_id=restaurant.id,
                day_of_week=day,
                opens_at=time(9, 0),
                closes_at=time(22, 0)
            )
            working_hours.append(wh)
    session.add_all(working_hours)

    # 6. Ингредиенты
    name_ingredient_map: Dict[str, Ingredient] = {}
    ingredients: List[Ingredient] = []

    for ingredient_name in ingredients_data:
        ingredient_obj = Ingredient(
            name=ingredient_name.capitalize(),
            price=addings_price_data[ingredient_name] if ingredient_name in addings_price_data else 99,
            is_available=True,
            image_url="/",
        )
        name_ingredient_map[ingredient_name] = ingredient_obj
        ingredients.append(ingredient_obj)
    session.add_all(ingredients)


    # 7. Характеристики
    characteristics_value_to_obj: Dict[str, FoodCharacteristic] = {}
    characteristics: List[FoodCharacteristic] = []

    for characteristics_value in characteristics_data:
        characteristic_obj = FoodCharacteristic(measure_value=f"{characteristics_value}")
        characteristics_value_to_obj[characteristics_value] = characteristic_obj
        characteristics.append(characteristic_obj)
    session.add_all(characteristics)


    # 8. Генерация блюд
    foods: List[Food] = []

    for category in data["menu_categories"]:
        for position in data["menu_categories"][category]["positions"]:
            variants: List[FoodVariant] = []

            for i in range(len(position['prices'])):
                characteristic_obj = characteristics_value_to_obj[ str(position['measure_values'][i]) ]

                variant = FoodVariant(
                    price=position["prices"][i],
                    ingredient_price_modifier=int(modifiers[i])
                )
                _characteristic_obj = characteristics_value_to_obj[str(position['measure_values'][i])]
                variant.characteristics = [_characteristic_obj]
                variants.append(variant)

            food = Food(
                name=position["name"],
                category_id=[c for c in categories if c.name == category][0].id,
                image_url="/",
                description=None,
                measure_name=data["menu_categories"][category]['measure_name'],
                variants=variants,
            )
            foods.append(food)

    session.add_all(foods)
    await session.flush()



    # 9. Связь блюд с ингредиентами через ассоциацию
    for category in categories:
        # Получаем все блюда этой категории
        category_foods = [food for food in foods if food.category_id == category.id]
        category_addings: Set[str] = data["menu_categories"][category.name]["addings"]

        for food in category_foods:
            # selected_ingredients: List[Ingredient] = []
            food_ingr_assocs: Dict[str, FoodIngredientAssociation] = {}

            for adding in category_addings:
                food_ingr_assocs[adding] = FoodIngredientAssociation(
                    food_id=food.id,
                    ingredient_id=name_ingredient_map[adding].id,
                    is_adding=True,
                    is_default=False,
                )

            position_ingredients: List[str] = [
                position for position in data["menu_categories"][category.name]['positions']
                if position['name'] == food.name
            ][0]['ingredients']

            for ingredient in position_ingredients:
                if ingredient in food_ingr_assocs:
                    food_ingr_assocs[ingredient].is_default = True
                else:
                    food_ingr_assocs[ingredient] = FoodIngredientAssociation(
                        food_id=food.id,
                        ingredient_id=name_ingredient_map[ingredient].id,
                        is_adding=False,
                        is_default=True,
                    )
            session.add_all([ingr for ingr in food_ingr_assocs.values()])


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
