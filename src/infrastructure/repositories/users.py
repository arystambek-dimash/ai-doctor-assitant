from typing import List

from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.users import UserEntity, UserEntityWithDetails
from src.infrastructure.database.models.users import User
from src.use_cases.users.dto import CreateUserDTO, UpdateUserDTO


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_user(self, user: CreateUserDTO) -> UserEntity:
        stmt = insert(User).values(**user.to_payload(exclude_none=True)).returning(User)
        result = await self._session.execute(stmt)
        user = result.scalar_one()
        return self._from_orm(user)

    async def update_user(self, user_id: int, user: UpdateUserDTO) -> UserEntity:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user.to_payload(exclude_none=True))
            .returning(User)
        )
        result = await self._session.execute(stmt)
        updated_user = result.scalar_one()
        return self._from_orm(updated_user)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return self._from_orm(user)

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return self._from_orm(user)

    async def get_user_with_details(self, user_id: int) -> UserEntityWithDetails | None:
        stmt = select(User).where(User.id == user_id).options(
            joinedload(User.doctor_profile)
        )
        result = await self._session.execute(stmt)
        user = result.unique().scalar_one_or_none()
        if user is None:
            return None
        return self._from_orm_with_details(user)

    @staticmethod
    def _from_orm(obj: User) -> UserEntity:
        return UserEntity(
            id=obj.id,
            email=obj.email,
            full_name=obj.full_name,
            phone=obj.phone,
            is_admin=obj.is_admin,
            password_hash=obj.password_hash,
        )

    async def get_all_users(self, skip: int = 0, limit: int = 20) -> List[UserEntity]:
        stmt = select(User).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [self._from_orm(user) for user in users]

    async def get_all_patients(self, skip: int = 0, limit: int = 20) -> List[UserEntity]:
        stmt = (
            select(User)
            .where(User.is_admin == False)
            .where(User.is_doctor == False)
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [self._from_orm(user) for user in users]

    async def delete_user(self, user_id: int) -> None:
        stmt = delete(User).where(User.id == user_id)
        await self._session.execute(stmt)

    async def count_all_users(self) -> int:
        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    def _from_orm_with_details(obj: User) -> UserEntityWithDetails:
        return UserEntityWithDetails(
            id=obj.id,
            email=obj.email,
            full_name=obj.full_name,
            phone=obj.phone,
            is_admin=obj.is_admin,
            password_hash=obj.password_hash,
            doctor_id=obj.doctor_profile.id if obj.doctor_profile else None,
            is_doctor=obj.is_doctor,
        )
