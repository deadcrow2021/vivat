from decimal import Decimal
from typing import Dict, List, Set
from sqlalchemy import Tuple, and_, exists, select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.exceptions import RestaurantNotFoundError
from src.domain.dto.order_dto import OrderRequest, OrderAction, OrderStatus
from src.application.interfaces.repositories.order_repository import IOrderRepository
from src.infrastructure.drivers.db.tables import Food, FoodIngredientAssociation, FoodVariant, Ingredient, Order, OrderItem, User, Restaurant, UserAddress


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
            raise ValueError(f"Действие {action} не доступно для этого ресторана")
        
        if restaurant.address == order_request.selected_restaurant.address:
            raise ValueError(f"Адрес {order_request.selected_restaurant.address} не совпадает с адресом ресторана")
        
        if restaurant.phone.e164 == order_request.selected_restaurant.phone:
            raise ValueError(f"Телефон {order_request.selected_restaurant.address} не совпадает с телефоном ресторана")

        # 2. Проверяем адрес
        validation_stmt = select(
            exists()
            .where(
                and_(
                    UserAddress.id == address_id,
                    UserAddress.user_id == user_id
                )    
            )
            .label('addr_exists')
        )
        validation_result = await self._session.execute(validation_stmt)
        validation_data = validation_result.first()

        if not validation_data.addr_exists:
            raise ValueError(f"Адрес пользователя с id {address_id} не найден")

        # 3. Собираем ID для batch-запросов
        food_variant_ids = {position.size for position in order_request.order_list}
        all_adding_ids = set()
        all_remove_ids = set()
        
        # Сопоставляем варианты еды с их ингредиентами
        position_ingredients: Dict[int, Tuple[Set[int], Set[int]]] = {}

        for position in order_request.order_list:
            adding_ids = set(position.addings or [])
            remove_ids = set(position.removed_ingredients or [])
            
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
                .selectinload(Food.ingredient_associations)
            )
            .filter(FoodVariant.id.in_(food_variant_ids))
        )
        food_variant_result = await self._session.execute(food_variant_stmt)
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
        
        for fv_id, (adding_ids, remove_ids) in position_ingredients.items():
            food_variant = food_variants[fv_id]
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
                else:
                    assoc: FoodIngredientAssociation = food_ingredients_map[adding_id]
                    if not assoc.is_adding:
                        invalid_ingredients.append(f"Ингредиент {adding_id} нельзя добавить для варианта {fv_id}")

            # Проверяем удаляемые ингредиенты
            for remove_id in remove_ids:
                if remove_id not in food_ingredients_map:
                    invalid_ingredients.append(f"Ингредиент {remove_id} не доступен для варианта {fv_id}")
                else:
                    assoc = food_ingredients_map[remove_id]
                    if not assoc.is_default: # только дефолтные можно убрать
                        invalid_ingredients.append(f"Ингредиент {remove_id} нельзя убрать для варианта {fv_id}")
        
        if invalid_ingredients:
            raise ValueError(f"Недоступные ингредиенты: {', '.join(invalid_ingredients)}")

        # 6. Предзагружаем все нужные ингредиенты
        ingredients_map = {}
        all_ingredient_ids = all_adding_ids | all_remove_ids
        if all_ingredient_ids:
            ingredients_stmt = select(Ingredient).filter(Ingredient.id.in_(all_ingredient_ids))
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
            total_price=Decimal('0.0'),
        )
        self._session.add(new_order)
        await self._session.flush()
        
        total_price = Decimal('0.0')
        order_items: List[OrderItem] = []
        total_quantity = 0

        # Создаем все OrderItem
        for position in order_request.order_list:
            ingredients_price = 0

            food_variant_obj = food_variants[position.size]
            modifier = food_variant_obj.ingredient_price_modifier

            for adding in position.addings:
                ingredients_price += ingredients_map[adding] * modifier

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

        await self._session.flush()

        # Добавляем отношения Many-to-Many
        for i, position in enumerate(order_request.order_list):
            order_item = order_items[i]
            
            if position.addings:
                for adding_id in position.addings:
                    added_ingredient = ingredients_map.get(adding_id)
                    if added_ingredient:
                        order_item.added_ingredients.append(added_ingredient)
            
            if position.removed_ingredients:
                for removed_id in position.removed_ingredients:
                    removed_ingredient = ingredients_map.get(removed_id)
                    if removed_ingredient:
                        order_item.removed_ingredients.append(removed_ingredient)

        return new_order


    def _has_action(restaurant: Restaurant, restaurant_action: OrderAction) -> bool:
        if OrderAction.DELIVERY == restaurant_action and restaurant.has_delivery:
            return True
        if OrderAction.INSIDE == restaurant_action and restaurant.has_dine_in:
            return True
        if OrderAction.TAKEAWAY == restaurant_action and restaurant.has_takeaway:
            return True

        return False
