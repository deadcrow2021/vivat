class ApplicationError(Exception):
    pass


class UnhandledException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class DatabaseException(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class IdNotValidError(ApplicationError):
    pass

class TokenError(ApplicationError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)