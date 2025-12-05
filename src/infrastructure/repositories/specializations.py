from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.specializations import SpecializationEntity, SpecializationWithCountEntity
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.infrastructure.database.models.doctors import Doctor
from src.infrastructure.database.models.specializations import Specialization
from src.use_cases.specializations.dto import CreateSpecializationDTO, UpdateSpecializationDTO


class SpecializationRepository(ISpecializationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_specialization(self, specialization: CreateSpecializationDTO) -> SpecializationEntity:
        stmt = (
            insert(Specialization)
            .values(**specialization.to_payload(exclude_none=True))
            .returning(Specialization)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_specialization(
            self, specialization_id: int, specialization: UpdateSpecializationDTO
    ) -> SpecializationEntity:
        stmt = (
            update(Specialization)
            .where(Specialization.id == specialization_id)
            .values(**specialization.to_payload(exclude_none=True))
            .returning(Specialization)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_specialization_by_id(self, specialization_id: int) -> SpecializationEntity | None:
        stmt = select(Specialization).where(Specialization.id == specialization_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_specialization_by_title(self, title: str) -> SpecializationEntity | None:
        stmt = select(Specialization).where(Specialization.title == title)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_all_specializations(self) -> list[SpecializationEntity]:
        stmt = select(Specialization).order_by(Specialization.title)
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def get_all_specializations_with_count(self) -> list[SpecializationWithCountEntity]:
        stmt = (
            select(
                Specialization,
                func.count(Doctor.id).label("doctors_count")
            )
            .outerjoin(Doctor, Doctor.specialization_id == Specialization.id)
            .group_by(Specialization.id)
            .order_by(Specialization.title)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            SpecializationWithCountEntity(
                id=row.Specialization.id,
                title=row.Specialization.title,
                description=row.Specialization.description,
                doctors_count=row.doctors_count,
            )
            for row in rows
        ]

    async def delete_specialization(self, specialization_id: int) -> bool:
        stmt = delete(Specialization).where(Specialization.id == specialization_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    @staticmethod
    def _from_orm(obj: Specialization) -> SpecializationEntity:
        return SpecializationEntity(
            id=obj.id,
            title=obj.title,
            description=obj.description,
        )
