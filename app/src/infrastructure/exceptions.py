class InfrastructureError(Exception):
    pass

class InvalidCredentialsError(InfrastructureError):
    def __init__(self, msg: str = None) -> None:
        if msg:
            super().__init__(msg)
        else:
            super().__init__('Неверные имя пользователя или пароль.')


class FeatureNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти фичу с id: {id}"
        else:
            msg = "Не удалось найти ни одну фичу"
        super().__init__(msg)


class IngredientsNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти ингредиент с id: {id}"
        else:
            msg = "Не удалось найти ни одного ингредиента"
        super().__init__(msg)


class FoodNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти блюдо с id: {id}"
        else:
            msg = "Не удалось найти ни одного блюда"
        super().__init__(msg)


class MenuCategoryNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти категорию меню с id: {id}"
        else:
            msg = "Не удалось найти ни одну категорию меню"
        super().__init__(msg)


class CityNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти город с id: {id}"
        else:
            msg = "Не удалось найти ни одного города"
        super().__init__(msg)


class RestaurantNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Не удалось найти ресторан"
        if id:
            msg += f" с id: {id}"
        super().__init__(msg)


class UserNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Не удалось найти пользователя"
        if id:
            msg += f" с id: {id}"
        super().__init__(msg)


class UserExistsError(InfrastructureError):
    def __init__(self, phone: str) -> None:
        msg = f"Пользователь с телефоном: {phone} уже существует"
        super().__init__(msg)


class VariantNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти вариант с id: {id}"
        else:
            msg = "Не удалось найти ни одного варианта"
        super().__init__(msg)


class UserAddressNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Не удалось найти адрес пользователя с id: {id}"
        else:
            msg = "Не удалось найти ни одного адреса пользователя"
        super().__init__(msg)


class OrderNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Не удалось найти заказ"
        if id:
            msg += f" с id: {id}"
        super().__init__(msg)
