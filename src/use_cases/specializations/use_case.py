from src.domain.entities.specializations import SpecializationEntity, SpecializationWithCountEntity
from src.domain.errors import BadRequestException, NotFoundException
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.use_cases.specializations.dto import CreateSpecializationDTO, UpdateSpecializationDTO


class SpecializationUseCase:
    def __init__(
            self,
            uow: IUoW,
            specialization_repository: ISpecializationRepository,
    ):
        self._uow = uow
        self._specialization_repo = specialization_repository

    async def create_specialization(self, specialization: CreateSpecializationDTO) -> SpecializationEntity:
        existing = await self._specialization_repo.get_specialization_by_title(specialization.title)
        if existing:
            raise BadRequestException("Specialization with this title already exists")

        async with self._uow:
            created = await self._specialization_repo.create_specialization(specialization)
        return created

    async def update_specialization(
            self, specialization_id: int, specialization: UpdateSpecializationDTO
    ) -> SpecializationEntity:
        existing = await self._specialization_repo.get_specialization_by_id(specialization_id)
        if not existing:
            raise NotFoundException("Specialization not found")

        if specialization.title:
            title_exists = await self._specialization_repo.get_specialization_by_title(specialization.title)
            if title_exists and title_exists.id != specialization_id:
                raise BadRequestException("Specialization with this title already exists")

        async with self._uow:
            updated = await self._specialization_repo.update_specialization(specialization_id, specialization)
        return updated

    async def get_specialization_by_id(self, specialization_id: int) -> SpecializationEntity:
        specialization = await self._specialization_repo.get_specialization_by_id(specialization_id)
        if not specialization:
            raise NotFoundException("Specialization not found")
        return specialization

    async def get_all_specializations(self) -> list[SpecializationEntity]:
        return await self._specialization_repo.get_all_specializations()

    async def get_all_specializations_with_count(self) -> list[SpecializationWithCountEntity]:
        return await self._specialization_repo.get_all_specializations_with_count()

    async def delete_specialization(self, specialization_id: int) -> bool:
        existing = await self._specialization_repo.get_specialization_by_id(specialization_id)
        if not existing:
            raise NotFoundException("Specialization not found")

        async with self._uow:
            return await self._specialization_repo.delete_specialization(specialization_id)
