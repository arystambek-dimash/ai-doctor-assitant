from typing import List

from src.domain.entities.users import UserEntity
from src.domain.errors import BadRequestException, NotFoundException
from src.domain.interfaces.uow import IUoW
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.password_service import PasswordService
from src.use_cases.users.dto import CreateUserDTO, LoginUserDTO, UpdateUserDTO


class UserUseCase:
    def __init__(
            self,
            uow: IUoW,
            user_repository: IUserRepository,
            jwt_service: JWTService,
            password_service: PasswordService,
    ):
        self._uow = uow
        self._user_repo = user_repository
        self._jwt_service = jwt_service
        self._password_service = password_service

    async def register(self, user: CreateUserDTO) -> UserEntity:
        db_user = await self._user_repo.get_user_by_email(user.email)
        if db_user:
            raise BadRequestException("User already exists")

        user.password_hash = self._password_service.encrypt(user.password_hash)
        async with self._uow:
            created_user = await self._user_repo.create_user(user)
        return created_user

    async def login(self, user: LoginUserDTO) -> dict:
        db_user = await self._user_repo.get_user_by_email(user.email)
        if not db_user:
            raise NotFoundException("User does not exist")

        if not self._password_service.verify(user.password, db_user.password_hash):
            raise BadRequestException("Invalid credentials")

        access_token = self._jwt_service.encode_access_token({"sub": str(db_user.id)})
        refresh_token = self._jwt_service.encode_refresh_token({"sub": str(db_user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def get_all_users(self, skip: int = 0, limit: int = 20) -> List[UserEntity]:
        async with self._uow:
            return await self._user_repo.get_all_users(skip=skip, limit=limit)

    async def get_all_patients(self, skip: int = 0, limit: int = 20) -> List[UserEntity]:
        async with self._uow:
            return await self._user_repo.get_all_patients(skip=skip, limit=limit)

    async def get_user_by_id(self, user_id: int) -> UserEntity:
        async with self._uow:
            user = await self._user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")
            return user

    async def update_user(self, user_id: int, dto: UpdateUserDTO) -> UserEntity:
        async with self._uow:
            user = await self._user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")
            return await self._user_repo.update_user(user_id, dto)

    async def delete_user(self, user_id: int) -> None:
        async with self._uow:
            user = await self._user_repo.get_user_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")
            await self._user_repo.delete_user(user_id)
