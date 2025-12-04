from src.domain.interfaces.repositories import IUserRepository


class UserUseCase:
    def __init__(
            self,
            user_repository: IUserRepository
    ):
        self._user_repo = user_repository
