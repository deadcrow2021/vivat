class InfrastructureError(Exception):
    pass

class InvalidCredentialsError(InfrastructureError):
    def __init__(self, msg: str = None) -> None:
        if msg:
            super().__init__(msg)
        else:
            super().__init__('Invalid username or password.')


class FeatureNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find feature with id: {id}"
        else:
            msg = "Cannot find any feature"
        super().__init__(msg)


class IngredientsNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find ingredient with id: {id}"
        else:
            msg = "Cannot find any ingredients"
        super().__init__(msg)


class FoodNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find food with id: {id}"
        else:
            msg = "Cannot find any food"
        super().__init__(msg)


class MenuCategoryNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find menu category with id: {id}"
        else:
            msg = "Cannot find any menu category"
        super().__init__(msg)


class CityNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find city with id: {id}"
        else:
            msg = "Cannot find any city"
        super().__init__(msg)


class RestaurantNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Cannot find restaurant"
        if id:
            msg += f" with id: {id}"
        super().__init__(msg)


class UserNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Cannot find user"
        if id:
            msg += f" with id: {id}"
        super().__init__(msg)


class UserExistsError(InfrastructureError):
    def __init__(self, phone: str) -> None:
        msg = f"User with phone: {phone} already exists"
        super().__init__(msg)


class VariantNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        if id:
            msg = f"Cannot find variant with id: {id}"
        else:
            msg = "Cannot find any variant"
        super().__init__(msg)

