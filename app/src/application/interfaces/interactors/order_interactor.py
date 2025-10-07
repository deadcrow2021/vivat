import random
import string
from typing import Optional

from src.domain.dto.auth_dto import CurrentUserDTO
from src.domain.dto.order_dto import OrderRequest, CreateOrderResponse, OrderStatus
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import order_repository, user_address_repository
from src.application.interfaces.notification.notifier import IOrderNotifier
from src.logger import logger


class AddOrderInteractor:
    def __init__(
        self,
        order_repository: order_repository.IOrderRepository,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager,
        notifier: Optional[IOrderNotifier] = None
    ):
        self._order_repository = order_repository
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager
        self._notifier = notifier

    async def __call__(self, order_request: OrderRequest, user_dto: CurrentUserDTO) -> CreateOrderResponse:
        user_id = user_dto.id
        # TODO: возможно убрать отмечание адреса is_primary,
        # так при выборе адреса он уже делается is_primary
        order_data = await self._order_repository.create_order(order_request, user_id)
        await self._user_address_repository.untag_user_addresses(user_id)
        await self._user_address_repository.tag_user_address(user_id, order_request.user_info.address_id)

        await self._transaction_manager.commit()

        order = order_data['order_obj']
        msg = ''
        unique_code = self._generate_unique_code()
        cook_start = order_request.cook_start
        comment = order_request.comment
        count = 1

        if order_request.payment_method == 'card':
            payment_method = 'По карте'
        if order_request.payment_method == 'cash':
            payment_method = 'Наличными'

        msg += f'Заказ № {unique_code}.\n'
        msg += f'Время начала готовки: {cook_start}.\n'
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

        if self._notifier:
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


# class UpdateOrderStatusInteractor:
#     def __init__(
#         self,
#         order_repository: order_repository.IOrderRepository,
#         transaction_manager: ITransactionManager
#     ):
#         self._order_repository = order_repository
#         self._transaction_manager = transaction_manager

#     async def __call__(self, order_id: int, new_status: OrderStatus) -> CreateOrderResponse:
#         if order_id < 1:
#             raise IdNotValidError

#         # Простейшие правила переходов: из CREATED -> IN_PROGRESS, IN_PROGRESS -> IN_DELIVERY|DONE, IN_DELIVERY -> DONE
#         order = await self._order_repository.update_order_status(order_id, new_status)
#         await self._transaction_manager.commit()

#         return CreateOrderResponse(
#             id=order.id,
#             user_id=order.user_id,
#             restaurant_id=order.restaurant_id,
#             address_id=order.address_id,
#             order_action=order.order_action,
#             total_price=order.total_price,
#             status=order.status,
#             unique_code=""
#         )
