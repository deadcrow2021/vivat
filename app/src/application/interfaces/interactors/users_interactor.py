from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.users_dto import GetUserResponse
from src.application.exceptions import DatabaseException, IdNotValidError
from src.application.interfaces.transaction_manager import ITransactionManager
from src.application.interfaces.repositories import users_repository


class GetUserInteractor:
    def __init__(
        self, users_repository: users_repository.IUsersRepository
    ):
        self._users_repository = users_repository

    async def __call__(self, user_id: int) -> GetUserResponse:
        if user_id < 1:
            raise IdNotValidError
        try:
            user = await self._users_repository.get_user_by_id(user_id)
            
            return GetUserResponse(
                id=user.id,
                name=user.name,
                phone=user.phone.e164,
                email=user.email
            )
        except SQLAlchemyError:
            raise DatabaseException("Не удалось получить пользователя в бд")
