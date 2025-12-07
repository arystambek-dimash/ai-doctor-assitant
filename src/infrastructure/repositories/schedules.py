from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.schedules import ScheduleEntity
from src.domain.interfaces.schedule_repository import IScheduleRepository
from src.infrastructure.database.models.schedules import Schedule
from src.use_cases.schedules.dto import CreateScheduleDTO, UpdateScheduleDTO


class ScheduleRepository(IScheduleRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_schedule(self, schedule: CreateScheduleDTO) -> ScheduleEntity:
        stmt = (
            insert(Schedule)
            .values(**schedule.to_payload(exclude_none=True))
            .returning(Schedule)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def update_schedule(self, schedule_id: int, schedule: UpdateScheduleDTO) -> ScheduleEntity:
        stmt = (
            update(Schedule)
            .where(Schedule.id == schedule_id)
            .values(**schedule.to_payload(exclude_none=True))
            .returning(Schedule)
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one()
        return self._from_orm(obj)

    async def get_schedule_by_id(self, schedule_id: int) -> ScheduleEntity | None:
        stmt = select(Schedule).where(Schedule.id == schedule_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_schedules_by_doctor_id(self, doctor_id: int) -> list[ScheduleEntity]:
        stmt = (
            select(Schedule)
            .where(Schedule.doctor_id == doctor_id)
            .order_by(Schedule.day_of_week, Schedule.start_time)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def get_schedule_by_doctor_and_day(
            self, doctor_id: int, day_of_week: int
    ) -> ScheduleEntity | None:
        stmt = select(Schedule).where(
            and_(
                Schedule.doctor_id == doctor_id,
                Schedule.day_of_week == day_of_week,
            )
        )
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    async def get_active_schedules_by_doctor_id(self, doctor_id: int) -> list[ScheduleEntity]:
        stmt = (
            select(Schedule)
            .where(
                and_(
                    Schedule.doctor_id == doctor_id,
                    Schedule.is_active == True,
                )
            )
            .order_by(Schedule.day_of_week, Schedule.start_time)
        )
        result = await self._session.execute(stmt)
        objects = result.scalars().all()
        return [self._from_orm(obj) for obj in objects]

    async def delete_schedule(self, schedule_id: int) -> bool:
        stmt = delete(Schedule).where(Schedule.id == schedule_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def get_schedule_by_id_doctor_id(self, schedule_id: int, doctor_id: int) -> ScheduleEntity | None:
        stmt = select(Schedule).where(Schedule.doctor_id == doctor_id)
        result = await self._session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None
        return self._from_orm(obj)

    @staticmethod
    def _from_orm(obj: Schedule) -> ScheduleEntity:
        return ScheduleEntity(
            id=obj.id,
            day_of_week=obj.day_of_week,
            start_time=obj.start_time,
            end_time=obj.end_time,
            slot_duration_minutes=obj.slot_duration_minutes,
            is_active=obj.is_active,
            doctor_id=obj.doctor_id,
        )
