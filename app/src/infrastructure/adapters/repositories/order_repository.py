from decimal import Decimal
from math import ceil
from typing import Dict, List, Optional, Set

from sqlalchemy import Tuple, and_, exists, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import OrderNotFoundError, RestaurantNotFoundError
from src.domain.dto.order_dto import OrderRequest, OrderAction, OrderStatus
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.infrastructure.drivers.db.tables import (
    Food,
    FoodIngredientAssociation,
    FoodVariant,
    Ingredient,
    Order,
    OrderItem,
    User,
    Restaurant,
    UserAddress,
    order_item_added_ingredient,
    order_item_removed_ingredient
)


class OrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_order(
        self,
        order_request: OrderRequest,
        user_id: int
    ) -> Order:
        address_id = order_request.user_info.address_id
        restaurant_id = order_request.selected_restaurant.id
        action = order_request.selected_restaurant.action

        # 1. Проерка данных о ресторане
        restaurant_stmt = (
            select(Restaurant)
            .filter(
                Restaurant.id == restaurant_id
            )
        )
        restaurant_result = await self._session.execute(restaurant_stmt)
        restaurant = restaurant_result.scalars().first()

        if not restaurant:
            raise RestaurantNotFoundError(restaurant_id)
        
        if not self._has_action(restaurant, action):
            raise ValueError(f"Действие {action.value} не доступно для этого ресторана")

        if restaurant.address != order_request.selected_restaurant.address:
            raise ValueError(f"Адрес {order_request.selected_restaurant.address} не совпадает с адресом ресторана")

        if restaurant.phone.e164 != order_request.selected_restaurant.phone:
            raise ValueError(f"Телефон {order_request.selected_restaurant.address} не совпадает с телефоном ресторана")

        # 2. Проверяем адрес
        address_stmt = (
            select(UserAddress)
            .where(
                UserAddress.id == address_id,
                UserAddress.user_id == user_id
            )
        )
        address_result = await self._session.execute(address_stmt)
        delivery_address = address_result.scalars().first()

        if not delivery_address:
            raise ValueError(f"Адрес пользователя с id {address_id} не найден")

        # 3. Собираем ID для batch-запросов
        food_variant_ids = {position.size for position in order_request.order_list}
        all_adding_ids = set()
        all_remove_ids = set()

        # Сопоставляем варианты еды с их ингредиентами
        position_ingredients: Dict[int, Tuple[Set[int], Set[int]]] = {}

        for position in order_request.order_list:
            adding_ids = set(position.addings.keys() if position.addings else []) # TODO: проверить
            remove_ids = set(position.removed_ingredients or [])

            ids_intersections = adding_ids.intersection(remove_ids)
            if ids_intersections:
                raise ValueError(
                    f"Ингредиент с id {', '.join(ids_intersections)} добавлены и удалены одновременно"
                )

            all_adding_ids.update(adding_ids)
            all_remove_ids.update(remove_ids)
            position_ingredients[position.size] = (adding_ids, remove_ids)


        # 4. Проверяем существование всех FoodVariant и загружаем их с ингредиентами
        if not food_variant_ids:
            raise ValueError("В заказе нет вариантов блюд")

        food_variant_stmt = (
            select(FoodVariant)
            .options(
                selectinload(FoodVariant.food)
                .selectinload(Food.ingredient_associations),
                selectinload(FoodVariant.characteristics)
            )
            .filter(FoodVariant.id.in_(food_variant_ids))
        )
        food_variant_result = await self._session.execute(food_variant_stmt)
        # Dict[FoodVariant.id, FoodVariant]
        food_variants = {fv.id: fv for fv in food_variant_result.scalars()}

        missing_food_variants = food_variant_ids - set(food_variants.keys())
        if missing_food_variants: 
            raise ValueError(f"Вариант блюда не найден: {missing_food_variants}")

        # Проверка совпадения имен вариантов из запроса и из БД
        for position in order_request.order_list:
            if position.price != food_variants[position.size].price:
                raise ValueError(f"Цена в запросе {position.price} не совпадает с ценой в БД {food_variants[position.size].price}")

            if position.size not in food_variants:
                raise ValueError(f"Вариант блюда с id {position.size} не найден")

            if not food_variants[position.size].food.name == position.name:
                raise ValueError(
                    f"Вариант блюда с id {position.size} имеет разные названия: "
                    f"{food_variants[position.size].food.name} != {position.name}"
                )

        # 5. Проверяем валидность ингредиентов для каждого варианта еды
        invalid_ingredients = []

        for position in order_request.order_list:
            adding_ids = set(position.addings.keys() if position.addings else []) # TODO: проверить
            remove_ids = set(position.removed_ingredients or [])
            fv_id = position.size
            food_variant = food_variants[position.size]

            if not food_variant.food:
                raise ValueError(f"Блюдо не найдено для варианта {fv_id}")

            # Создаем маппинг ингредиентов блюда
            food_ingredients_map = {}
            for assoc in food_variant.food.ingredient_associations:
                food_ingredients_map[assoc.ingredient_id] = assoc

            # Проверяем добавляемые ингредиенты
            for adding_id in adding_ids:
                if adding_id not in food_ingredients_map:
                    invalid_ingredients.append(f"Ингредиент {adding_id} не доступен для варианта {fv_id}")

            # Проверяем удаляемые ингредиенты
            for remove_id in remove_ids:
                if remove_id not in food_ingredients_map:
                    invalid_ingredients.append(f"Ингредиент {remove_id} не доступен для варианта {fv_id}")
                else:
                    assoc: FoodIngredientAssociation = food_ingredients_map[remove_id]
                    if not assoc.is_default: # только дефолтные можно убрать
                        invalid_ingredients.append(f"Ингредиент {remove_id} нельзя убрать для варианта {fv_id}")
        
        if invalid_ingredients:
            raise ValueError(f"Недоступные ингредиенты: {', '.join(invalid_ingredients)}")

        # 6. Предзагружаем все нужные ингредиенты
        ingredients_map = {}
        all_ingredient_ids = all_adding_ids | all_remove_ids

        if all_ingredient_ids:
            ingredients_stmt = (
                select(Ingredient)
                .filter(Ingredient.id.in_(all_ingredient_ids))
            )
            ingredients_result = await self._session.execute(ingredients_stmt)
            for ingredient in ingredients_result.scalars():
                ingredients_map[ingredient.id] = ingredient

        # Проверяем, что все ингредиенты существуют
        missing_ingredients = all_ingredient_ids - set(ingredients_map.keys())
        if missing_ingredients:
            raise ValueError(f"Ингредиенты не найдены: {missing_ingredients}")

        # 7. Создаем заказ
        new_order = Order(
            user_id=user_id,
            restaurant_id=restaurant_id,
            address_id=address_id,
            order_action=order_request.selected_restaurant.action,
            status=OrderStatus.CREATED,
            total_price=0,
        )
        self._session.add(new_order)
        await self._session.flush()
        
        total_price = 0
        order_items: List[OrderItem] = []
        total_quantity = 0

        # Создаем все OrderItem
        for position in order_request.order_list:
            ingredients_price = 0

            food_variant_obj = food_variants[position.size]
            modifier = food_variant_obj.ingredient_price_modifier

            if position.addings: ##### Цена ебланит ######
                for adding_id, addings_amount in position.addings.items():
                    ingredients_price += ceil(ingredients_map[adding_id].price * modifier) * addings_amount

            position_clear_price = food_variant_obj.price + ingredients_price
            position_total_price = position_clear_price * position.quantity

            total_price += position_total_price
            total_quantity += position.quantity

            new_order_item = OrderItem(
                food_variant_id=position.size,
                order_id=new_order.id,
                quantity=position.quantity,
                final_price=position_clear_price,
            )
            self._session.add(new_order_item)
            order_items.append(new_order_item)

        if order_request.order_quantity != total_quantity:
            raise ValueError(f'Общее количество позиций в заказе не совпадает с количеством в заказе. Общее количество: {total_quantity}')

        new_order.total_price = total_price
        await self._session.flush()  # Ensure order items have IDs

        # Add Many-to-Many relationships using async-safe approach
        for i, position in enumerate(order_request.order_list):
            order_item = order_items[i]

            if position.addings:
                for adding_id, _ in position.addings.items():
                    added_ingredient = ingredients_map.get(adding_id)
                    if added_ingredient:
                        # Use session to create the association record
                        assoc = order_item_added_ingredient.insert().values(
                            order_item_id=order_item.id,
                            added_id=added_ingredient.id
                        )
                        await self._session.execute(assoc)

            if position.removed_ingredients:
                for removed_id in position.removed_ingredients:
                    removed_ingredient = ingredients_map.get(removed_id)
                    if removed_ingredient:
                        assoc = order_item_removed_ingredient.insert().values(
                            order_item_id=order_item.id,
                            removed_id=removed_ingredient.id
                        )
                        await self._session.execute(assoc)

        data = {
            'delivery_address': delivery_address.get_full_address(),
            'total_price': total_price,
            'order': {},
            'order_obj': new_order
        }
        order = data['order']

        for item in order_request.order_list:
            fv = food_variants[item.size]
            food = fv.food

            name = food.name
            measure_name = food.measure_name

            measure_value = ''
            if fv.characteristics:
                measure_value = fv.characteristics[0].measure_value
                if not measure_value:
                    measure_value = ''

            order[name] = []
            price = fv.price
            modifier = fv.ingredient_price_modifier
            quantity = item.quantity

            current = {
                'measure_name' : measure_name,
                'measure_value' : measure_value,
                'price' : price,
                'modifier' : modifier,
                'quantity' : quantity,
                'ingredients': {
                    'add': {},
                    'remove': []
                }
            }
            if item.addings:
                for adding_id, addings_amount in item.addings.items():
                    addings = current['ingredients']['add']
                    addings[ingredients_map[adding_id].name] = {
                        'quantity': addings_amount,
                        'price': ceil(ingredients_map[adding_id].price * modifier)
                    }
            if item.removed_ingredients:
                for removed_id in item.removed_ingredients:
                    removed = current['ingredients']['remove']
                    removed.append(ingredients_map[removed_id].name)

            order[name].append(current)

        return data


    def _has_action(self, restaurant: Restaurant, restaurant_action: OrderAction) -> bool:
        if OrderAction.DELIVERY == restaurant_action and restaurant.has_delivery:
            return True
        if OrderAction.INSIDE == restaurant_action and restaurant.has_dine_in:
            return True
        if OrderAction.TAKEAWAY == restaurant_action and restaurant.has_takeaway:
            return True

        return False


    async def update_order_status(self, order_id: int, new_status: OrderStatus) -> Order:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
        )
        result = await self._session.execute(stmt)
        order: Optional[Order] = result.scalars().first()

        if not order:
            raise OrderNotFoundError(order_id)

        order.status = new_status
        await self._session.flush()
        return order
