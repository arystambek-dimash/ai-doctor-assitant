from src.domain.constants import DoctorStatus
from src.domain.entities.doctors import DoctorEntity, DoctorWithDetailsEntity
from src.domain.errors import BadRequestException, NotFoundException, ForbiddenException
from src.domain.interfaces.doctor_repository import IDoctorRepository
from src.domain.interfaces.speicailization_repository import ISpecializationRepository
from src.domain.interfaces.uow import IUoW
from src.domain.interfaces.user_repository import IUserRepository
from src.use_cases.doctors.dto import (
    CreateDoctorDTO,
    AdminCreateDoctorDTO,
    RegisterDoctorDTO,
    UpdateDoctorDTO,
    ApproveDoctorDTO,
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

    # ==================== ADMIN OPERATIONS ====================

    async def admin_create_doctor(
            self, dto: AdminCreateDoctorDTO, admin_user_id: int, is_admin: bool
    ) -> DoctorEntity:
        """Admin creates a doctor profile for an existing user."""
        if not is_admin:
            raise ForbiddenException("Only admins can create doctor profiles")

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

        create_dto = CreateDoctorDTO(
            bio=dto.bio,
            experience_years=dto.experience_years,
            license_number=dto.license_number,
            user_id=dto.user_id,
            specialization_id=dto.specialization_id,
            rating=dto.rating,
            status=DoctorStatus.APPROVED,  # Admin-created = auto-approved
        )

        async with self._uow:
            doctor = await self._doctor_repo.create_doctor(create_dto)
        return doctor

    async def approve_doctor(
            self, doctor_id: int, admin_user_id: int, is_admin: bool
    ) -> DoctorEntity:
        """Admin approves a pending doctor application."""
        if not is_admin:
            raise ForbiddenException("Only admins can approve doctors")

        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.PENDING:
            raise BadRequestException(f"Doctor is already {doctor.status.value}")

        dto = ApproveDoctorDTO(status=DoctorStatus.APPROVED)

        async with self._uow:
            updated = await self._doctor_repo.update_doctor_status(doctor_id, dto)
        return updated

    async def reject_doctor(
            self, doctor_id: int, reason: str, admin_user_id: int, is_admin: bool
    ) -> DoctorEntity:
        """Admin rejects a pending doctor application."""
        if not is_admin:
            raise ForbiddenException("Only admins can reject doctors")

        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.PENDING:
            raise BadRequestException(f"Doctor is already {doctor.status.value}")

        dto = ApproveDoctorDTO(status=DoctorStatus.REJECTED, rejection_reason=reason)

        async with self._uow:
            updated = await self._doctor_repo.update_doctor_status(doctor_id, dto)
        return updated

    async def suspend_doctor(
            self, doctor_id: int, reason: str, admin_user_id: int, is_admin: bool
    ) -> DoctorEntity:
        """Admin suspends an approved doctor."""
        if not is_admin:
            raise ForbiddenException("Only admins can suspend doctors")

        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.APPROVED:
            raise BadRequestException("Can only suspend approved doctors")

        dto = ApproveDoctorDTO(status=DoctorStatus.SUSPENDED, rejection_reason=reason)

        async with self._uow:
            updated = await self._doctor_repo.update_doctor_status(doctor_id, dto)
        return updated

    async def reinstate_doctor(
            self, doctor_id: int, admin_user_id: int, is_admin: bool
    ) -> DoctorEntity:
        """Admin reinstates a suspended doctor."""
        if not is_admin:
            raise ForbiddenException("Only admins can reinstate doctors")

        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.SUSPENDED:
            raise BadRequestException("Can only reinstate suspended doctors")

        dto = ApproveDoctorDTO(status=DoctorStatus.APPROVED, rejection_reason=None)

        async with self._uow:
            updated = await self._doctor_repo.update_doctor_status(doctor_id, dto)
        return updated

    async def get_pending_doctors(
            self, admin_user_id: int, is_admin: bool, skip: int = 0, limit: int = 20
    ) -> list[DoctorWithDetailsEntity]:
        """Admin gets list of pending doctor applications."""
        if not is_admin:
            raise ForbiddenException("Only admins can view pending applications")

        return await self._doctor_repo.get_pending_doctors(skip=skip, limit=limit)

    # ==================== USER SELF-REGISTRATION ====================

    async def register_as_doctor(self, dto: RegisterDoctorDTO, user_id: int) -> DoctorEntity:
        """User self-registers as a doctor (pending approval)."""
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
            status=DoctorStatus.PENDING,  # Self-registered = pending
        )

        async with self._uow:
            doctor = await self._doctor_repo.create_doctor(create_dto)
        return doctor

    async def get_my_doctor_profile(self, user_id: int) -> DoctorWithDetailsEntity:
        """User gets their own doctor profile."""
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            raise NotFoundException("You don't have a doctor profile")

        return await self._doctor_repo.get_doctor_with_details(doctor.id)

    async def get_my_application_status(self, user_id: int) -> dict:
        """User checks their doctor application status."""
        doctor = await self._doctor_repo.get_doctor_by_user_id(user_id)
        if not doctor:
            return {"has_application": False}

        return {
            "has_application": True,
            "status": doctor.status.value,
            "rejection_reason": doctor.rejection_reason,
        }

    # ==================== COMMON OPERATIONS ====================

    async def update_doctor(
            self, doctor_id: int, dto: UpdateDoctorDTO, user_id: int, is_admin: bool = False
    ) -> DoctorEntity:
        """Update doctor profile (by doctor themselves or admin)."""
        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if not is_admin and doctor.user_id != user_id:
            raise ForbiddenException("Cannot update another doctor's profile")

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
        """Get doctor by ID (public, but only approved doctors)."""
        doctor = await self._doctor_repo.get_doctor_with_details(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if doctor.status != DoctorStatus.APPROVED:
            raise NotFoundException("Doctor not found")

        return doctor

    async def get_all_doctors(
            self,
            status: DoctorStatus | None = None,
            skip: int = 0,
            limit: int = 10,
            is_admin: bool = False,
    ) -> list[DoctorWithDetailsEntity]:
        """Get all doctors. Non-admins only see approved doctors."""
        if not is_admin:
            status = DoctorStatus.APPROVED

        return await self._doctor_repo.get_all_doctors(status=status, skip=skip, limit=limit)

    async def get_doctors_by_specialization(
            self, specialization_id: int
    ) -> list[DoctorWithDetailsEntity]:
        """Get approved doctors by specialization (public)."""
        return await self._doctor_repo.get_doctors_by_specialization(
            specialization_id, only_approved=True
        )

    async def delete_doctor(
            self, doctor_id: int, user_id: int, is_admin: bool = False
    ) -> bool:
        """Delete doctor profile (admin only or self-delete pending application)."""
        doctor = await self._doctor_repo.get_doctor_by_id(doctor_id)
        if not doctor:
            raise NotFoundException("Doctor not found")

        if not is_admin:
            if doctor.user_id != user_id:
                raise ForbiddenException("Cannot delete another doctor's profile")
            if doctor.status != DoctorStatus.PENDING:
                raise ForbiddenException("Can only withdraw pending applications")

        async with self._uow:
            return await self._doctor_repo.delete_doctor(doctor_id)
