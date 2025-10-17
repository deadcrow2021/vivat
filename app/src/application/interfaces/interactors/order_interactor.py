from math import ceil
import random
import string
from typing import Optional

from src.infrastructure.exceptions import UserNotFoundError
from src.application.exceptions import IdNotValidError
from src.domain.dto.auth_dto import CurrentUserDTO
from src.domain.dto.order_dto import OrderAction, GetOrderResponse, IngredientModel, OrderItemModel, OrderModel, OrderRequest, CreateOrderResponse, OrderStatus
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import order_repository, user_address_repository, users_repository
from src.application.interfaces.notification.notifier import INotifier
from src.logger import logger


class GetUserOrdersInteractor:
    def __init__(
        self,
        order_repository: order_repository.IOrderRepository,
    ):
        self._order_repository = order_repository

    async def __call__(self, user_id: int) -> GetOrderResponse:
        if user_id < 1:
            raise IdNotValidError

        orders = await self._order_repository.get_user_orders(user_id)
        orders_list = []

        for order in orders:
            order_items = []
            status = order.status
            delivery_address = order.address.get_full_address()
            order_date = order.created_at.strftime("%d.%m.%Y.")
            total_price = order.total_price
            restaurant_phone = order.restaurant.phone.e164

            for item in order.items:
                add_ingredients_dict = {}
                add_list = []
                remove_list = []

                food_variant = item.food_variant
                food = food_variant.food

                price_modifier = food_variant.ingredient_price_modifier

                measure_value = ''
                if food_variant.characteristics:
                    measure_value = food_variant.characteristics[0].measure_value
                    if not measure_value:
                        measure_value = ''

                item_name = ' '.join(
                    [
                        x for x in
                        [food.name, measure_value, food.measure_name]
                        if x
                    ]
                )

                for add_ingredient in item.added_ingredients:
                    if add_ingredient.id in add_ingredients_dict:
                        add_ingredients_dict[add_ingredient.id]['quantity'] += 1
                    else:
                        add_ingredients_dict[add_ingredient.id] = {
                            'name': add_ingredient.name,
                            'price': add_ingredient.price,
                            'ingredient_obj' : add_ingredient,
                            'quantity': 1
                        }

                for _, add_ingredient in add_ingredients_dict.items():
                    price = add_ingredient['price']
                    add_list.append(
                        IngredientModel(
                            name=add_ingredient['name'],
                            price=ceil(price * price_modifier),
                            quantity=add_ingredient['quantity'],
                        )
                    )

                for remove in item.removed_ingredients:
                    remove_list.append(
                        IngredientModel(
                            name=remove.name
                        )
                    )

                order_items.append(
                    OrderItemModel(
                        name=item_name,
                        quantity=item.quantity,
                        price=food_variant.price,
                        add=add_list,
                        remove=remove_list
                    )
                )

            orders_list.append(
                OrderModel(
                    order_items=order_items,
                    status=status,
                    delivery_address=delivery_address,
                    positions_quantity=len(order_items),
                    order_date=order_date,
                    total_price=total_price,
                    restaurant_phone=restaurant_phone,
                )
            )

        return GetOrderResponse(orders=orders_list)


class AddOrderInteractor:
    def __init__(
        self,
        order_repository: order_repository.IOrderRepository,
        user_repository: users_repository.IUsersRepository,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager,
        notifier: INotifier
    ):
        self._order_repository = order_repository
        self._user_repository = user_repository
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager
        self._notifier = notifier

    async def __call__(self, order_request: OrderRequest, user_dto: CurrentUserDTO) -> CreateOrderResponse:
        user = await self._user_repository.get_user_by_phone(user_dto.phone)
        
        if not user:
            raise UserNotFoundError

        if user.is_banned:
            raise ValueError('Неизвестная ошибка при создании заказа. Попробуйте позже.')

        action = order_request.selected_restaurant.action
        if action == OrderAction.DELIVERY:
            if not order_request.user_info:
                raise ValueError('Для доставки необходимо указать адрес пользователя.')

        order_data = await self._order_repository.create_order(order_request, user_dto.id)
        await self._transaction_manager.commit()

        order = order_data['order_obj']
        unique_code = self._generate_unique_code()
        cook_start = order_request.cook_start
        comment = order_request.comment
        count = 1
        msg = ''

        if order_request.payment_method == 'card':
            payment_method = 'По карте'
        if order_request.payment_method == 'cash':
            payment_method = 'Наличными'

        msg += f'Заказ № {unique_code}.\n'
        msg += f'Время начала готовки: {"Как можно скорее" if cook_start == "asap" else cook_start}.\n'
        msg += f'Способ оплаты: {payment_method}.\n'
        msg += f'Телефон клиента: {user_dto.phone}.\n'
        msg += f'Адрес доставки: {order_data['delivery_address']}\n\n'
        msg += f'Комментарий к заказу: {comment}\n\n' if comment else ''
        
        for name, items_variations in order_data['order'].items():
            for item in items_variations:
                position_name = ' '.join(
                    [
                        x for x in
                        [name, item['measure_value'], item['measure_name']]
                        if x
                    ]
                )
                msg += f'{count}. {position_name} - {item['price']} р. - {item['quantity']} шт\n'
                ingredients = item['ingredients']
                if ingredients['add']:
                    msg += 'Добавить:\n'
                    msg += '\n'.join(
                        f'\t- {add_ingredient} - {ingredients['add'][add_ingredient]['price']} р. - {ingredients['add'][add_ingredient]['quantity']} шт'
                        for add_ingredient in ingredients['add']
                    )
                if ingredients['remove']:
                    msg += '\nУбрать:\n'
                    msg += '\n'.join(
                        f'\t- {remove_ingredient}'
                        for remove_ingredient in ingredients['remove']
                    )
                msg += '\n\n'
                count += 1

        msg += 'Общая сумма: ' + str(order_data['total_price']) + ' р.'

        print(msg)
        logger.info(msg)
        await self._notifier.send_new_order(order.restaurant_id, order.id, msg, order.status.value)

        return CreateOrderResponse(
            id=order.id,
            user_id=order.user_id,
            restaurant_id=order.restaurant_id,
            address_id=order.address_id,
            order_action=order.order_action,
            total_price=order.total_price,
            status=order.status,
            unique_code=unique_code
        )


    def _generate_unique_code(self) -> str:
        letter = random.choice(string.ascii_uppercase)
        digits = random.randint(100, 999)
        return f"{letter}{digits}"
