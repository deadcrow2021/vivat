class InfrastructureError(Exception):
    pass


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
