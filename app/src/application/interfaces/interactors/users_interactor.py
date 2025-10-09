from sqlalchemy.exc import SQLAlchemyError

from src.domain.dto.users_dto import DeleteUserResponse, GetUserResponse
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

        user = await self._users_repository.get_user_by_id(user_id)
        
        return GetUserResponse(
            id=user.id,
            name=user.name,
            phone=user.phone.e164,
            email=user.email
        )


class DeleteUserInteractor:
    def __init__(
        self, users_repository: users_repository.IUsersRepository,
        transaction_manager: ITransactionManager
    ):
        self._users_repository = users_repository
        self._transaction_manager = transaction_manager
  

    async def __call__(self, user_id: int) -> DeleteUserResponse:
        if user_id < 1:
            raise IdNotValidError

        user = await self._users_repository.delete_user(user_id)
        await self._transaction_manager.commit()

        return DeleteUserResponse(id=user.id)
