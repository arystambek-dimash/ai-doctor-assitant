from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.users import UserEntity
from src.infrastructure.database.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_user(self, user: UserEntity) -> UserEntity:
        stmt = insert(User).values(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            phone=user.phone,
            is_admin=user.phone
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return UserEntity(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_admin=user.phone
        )
