from typing import Optional, List

from src.domain.constants import DoctorStatus
from src.domain.entities.doctors import DoctorEntity, DoctorWithDetailsEntity
from src.domain.errors import BadRequestException, NotFoundException
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.domain.interfaces.user_repository import IUserRepository
from src.use_cases.doctors.dto import (
    CreateDoctorDTO,
    RegisterDoctorDTO,
    UpdateDoctorDTO, AdminCreateDoctorDTO
)


class DoctorUseCase:
    def __init__(
            self,
            uow: IUoW,
            doctor_repository: IDoctorRepository,
            user_repository: IUserRepository,
            specialization_repository: ISpecializationRepository,
    ):
        self._uow = uow
        self._doctor_repo = doctor_repository
        self._user_repo = user_repository
        self._specialization_repo = specialization_repository

    async def admin_create_doctor(
            self, dto: AdminCreateDoctorDTO
    ) -> DoctorEntity:
        user = await self._user_repo.get_user_by_id(dto.user_id)
        if not user:
            raise NotFoundException("User not found")
        existing_doctor = await self._doctor_repo.get_doctor_by_user_id(dto.user_id)
        if existing_doctor:
            raise BadRequestException("User already has a doctor profile")
        license_exists = await self._doctor_repo.get_doctor_by_license_number(dto.license_number)
        if license_exists:
            raise BadRequestException("License number already registered")
        specialization = await self._specialization_repo.get_specialization_by_id(dto.specialization_id)
        if not specialization:
            raise NotFoundException("Specialization not found")

        async with self._uow:
            return await self._doctor_repo.create_doctor(
                CreateDoctorDTO(
                    bio=dto.bio,
                    experience_years=dto.experience_years,
                    license_number=dto.license_number,
                    user_id=dto.user_id,
                    specialization_id=dto.specialization_id,
                    rating=dto.rating,
                    status=DoctorStatus.APPROVED,
                )
            )

    async def get_pending_doctors(
            self, skip: int = 0, limit: int = 20
    ) -> List[DoctorWithDetailsEntity]:
        return await self._doctor_repo.get_pending_doctors(skip=skip, limit=limit)

    async def register_as_doctor(self, dto: RegisterDoctorDTO, user_id: int) -> DoctorEntity:
        existing_doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if existing_doctor:
            if existing_doctor.status == DoctorStatus.PENDING:
                raise BadRequestException("Your application is pending approval")
            elif existing_doctor.status == DoctorStatus.REJECTED:
                raise BadRequestException(
                    f"Your previous application was rejected: {existing_doctor.rejection_reason}"
                )
            else:
                raise BadRequestException("You already have a doctor profile")

        license_exists = await self._doctor_repo.get_doctor_by_license_number(dto.license_number)
        if license_exists:
            raise BadRequestException("License number already registered")

        specialization = await self._specialization_repo.get_specialization_by_id(dto.specialization_id)
        if not specialization:
            raise NotFoundException("Specialization not found")

        create_dto = CreateDoctorDTO(
            bio=dto.bio,
            experience_years=dto.experience_years,
            license_number=dto.license_number,
            user_id=user_id,
            specialization_id=dto.specialization_id,
            status=DoctorStatus.PENDING,
        )
        async with self._uow:
            doctor = await self._doctor_repo.create_doctor(create_dto)
        return doctor

    async def get_my_doctor_profile(self, user_id: int) -> DoctorWithDetailsEntity:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise NotFoundException("You don't have a doctor profile")

        return await self._doctor_repo.get_doctor_with_details(doctor.id)

    async def get_my_application_status(self, user_id: int) -> dict:
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            return {"has_application": False}

        return {
            "has_application": True,
            "status": doctor.status.value,
            "rejection_reason": doctor.rejection_reason,
        }

    async def update_doctor(
            self,
            doctor_id: int,
            dto: UpdateDoctorDTO
    ) -> DoctorEntity:
        db_doctor = await self._doctor_repo.get_doctor_by_user_id(doctor_id)
        if not db_doctor:
            raise NotFoundException("Doctor profile is not found")
        if dto.license_number:
            license_exists = await self._doctor_repo.get_doctor_by_license_number(dto.license_number)
            if license_exists and license_exists.id != doctor_id:
                raise BadRequestException("License number already registered")
        if dto.specialization_id:
            specialization = await self._specialization_repo.get_specialization_by_id(dto.specialization_id)
            if not specialization:
                raise NotFoundException("Specialization not found")
        async with self._uow:
            updated = await self._doctor_repo.update_doctor(doctor_id, dto)
        return updated

    async def get_doctor_by_id(self, doctor_id: int) -> DoctorWithDetailsEntity:
        doctor = await self._doctor_repo.get_doctor_with_details(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.APPROVED:
            raise NotFoundException("Doctor not found")

        return doctor

    async def get_all_doctors(
            self,
            specialization_id: Optional[int] = None,
            status: Optional[DoctorStatus] = None,
            skip: int = 0,
            limit: int = 10,
            is_admin: bool = False,
    ) -> list[DoctorWithDetailsEntity]:
        if not is_admin:
            status = DoctorStatus.APPROVED
        return await self._doctor_repo.get_all_doctors(
            specialization_id=specialization_id,
            status=status,
            skip=skip,
            limit=limit
        )

    async def delete_doctor(
            self, doctor_id: int
    ) -> bool:
        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")
        async with self._uow:
            return await self._doctor_repo.delete_doctor(doctor_id)
