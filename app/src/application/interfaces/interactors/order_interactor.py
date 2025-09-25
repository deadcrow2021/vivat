import random
import string
from src.domain.dto.order_dto import OrderRequest, CreateOrderResponse
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import order_repository, user_address_repository


class AddOrderInteractor:
    def __init__(
        self,
        order_repository: order_repository.IOrderRepository,
        user_address_repository: user_address_repository.IUserAddressRepository,
        transaction_manager: ITransactionManager
    ):
        self._order_repository = order_repository
        self._user_address_repository = user_address_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, order_request: OrderRequest, user_id: int) -> CreateOrderResponse:
        # TODO: возможно убрать отмечание адреса is_primary,
        # так при выборе адреса он уже делается is_primary
        await self._user_address_repository.untag_user_addresses(user_id)
        order = await self._order_repository.create_order(order_request, user_id)
        await self._user_address_repository.tag_user_address(user_id, order_request.user_info.address_id)

        await self._transaction_manager.commit()

        return CreateOrderResponse(
            id=order.id,
            user_id=order.user_id,
            restaurant_id=order.restaurant_id,
            address_id=order.address_id,
            order_action=order.order_action,
            total_price=order.total_price,
            status=order.status,
            unique_code=self._generate_unique_code()
        )


    def _generate_unique_code(self) -> str:
        letter = random.choice(string.ascii_uppercase)
        digits = random.randint(100, 999)
        return f"{letter}{digits}"
