from src.domain.constants import AppointmentStatus
from src.domain.interfaces.uow import IUoW
from src.infrastructure.repositories.appointments import AppointmentRepository
from src.infrastructure.repositories.doctors import DoctorRepository
from src.infrastructure.repositories.medical_records import MedicalRecordRepository
from src.infrastructure.repositories.users import UserRepository
from src.use_cases.stats.dto import AdminStatsDTO


class StatsUseCase:
    def __init__(
            self,
            uow: IUoW,
            user_repository: UserRepository,
            doctor_repository: DoctorRepository,
            appointment_repository: AppointmentRepository,
            medical_record_repository: MedicalRecordRepository,
    ):
        self._uow = uow
        self._user_repo = user_repository
        self._doctor_repo = doctor_repository
        self._appointment_repo = appointment_repository
        self._medical_record_repo = medical_record_repository

    async def get_admin_stats(self) -> AdminStatsDTO:
        async with self._uow:
            total_users = await self._user_repo.count_all_users()
            total_doctors = await self._doctor_repo.count_all_doctors()
            total_bookings = await self._appointment_repo.count_all_appointments()
            today_bookings = await self._appointment_repo.count_today_appointments()
            pending_bookings = await self._appointment_repo.count_appointments_by_status(
                AppointmentStatus.SCHEDULED
            )
            completed_bookings = await self._appointment_repo.count_appointments_by_status(
                AppointmentStatus.COMPLETED
            )
            total_emrs = await self._medical_record_repo.count_all_medical_records()

        return AdminStatsDTO(
            total_users=total_users,
            total_doctors=total_doctors,
            total_bookings=total_bookings,
            today_bookings=today_bookings,
            pending_bookings=pending_bookings,
            completed_bookings=completed_bookings,
            total_emrs=total_emrs,
        )
