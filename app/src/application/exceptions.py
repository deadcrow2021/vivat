class ApplicationError(Exception):
    pass


class IdNotValidError(ApplicationError):
    pass

class TokenError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)