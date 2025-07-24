class InfrastructureError(Exception):
    pass


class CityNotFoundError(InfrastructureError):
    def __init__(self, id: int) -> None:
        super().__init__(f"Cannot find city with id: {id}")


class RestaurantNotFoundError(InfrastructureError):
    def __init__(self, id: int = None) -> None:
        msg = f"Cannot find restaurant"
        if id:
            msg += f" with id: {id}"
        super().__init__(msg)
