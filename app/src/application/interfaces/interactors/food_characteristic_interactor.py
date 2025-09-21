from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.food_characteristic_dto import AddCharacteristicsToVariantRequest, AddCharacteristicsToVariantResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import food_characteristic_repository


class AddCharacteristicsToVariantInteractor:
    def __init__(
        self,
        food_characteristic_repository: food_characteristic_repository.IFoodCharacteristicRepository,
        transaction_manager: ITransactionManager
    ):
        self._food_characteristic_repository = food_characteristic_repository
        self._transaction_manager = transaction_manager

    async def __call__(self, add_char_request: AddCharacteristicsToVariantRequest) -> AddCharacteristicsToVariantResponse:
        try:
            food_char = await self._food_characteristic_repository.add_characteristics_to_variant_by_id(
                add_char_request.variant_id,
                add_char_request.characteristic_value
            )

            await self._transaction_manager.commit()
            return AddCharacteristicsToVariantResponse(
                id=food_char.id,
                measure_value=food_char.measure_value
            )
        
        except SQLAlchemyError:
            raise DatabaseException("Не удалось добавить характеристику к варианту блюда в бд")
