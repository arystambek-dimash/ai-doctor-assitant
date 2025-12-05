from datetime import date

from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.schedules import ScheduleCreateRequest, ScheduleUpdateRequest
from src.presentation.api.schemas.responses.schedules import ScheduleResponse, TimeSlotResponse
from src.presentation.dependencies import get_current_user, get_schedule_use_case
from src.use_cases.schedules.dto import CreateScheduleDTO, UpdateScheduleDTO
from src.use_cases.schedules.use_case import ScheduleUseCase

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new schedule for current doctor",
)
async def create_schedule(
        request: ScheduleCreateRequest,
        current_user: UserEntity = Depends(get_current_user),
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    doctor = await schedule_use_case._doctor_repo.get_doctor_by_user_id(current_user.id)

    dto = CreateScheduleDTO(
        day_of_week=request.day_of_week,
        start_time=request.start_time,
        end_time=request.end_time,
        slot_duration_minutes=request.slot_duration_minutes,
        is_active=request.is_active,
        doctor_id=doctor.id,
    )
    entity = await schedule_use_case.create_schedule(dto, current_user.id)
    return ScheduleResponse.from_entity(entity)


@router.get(
    "/me",
    response_model=list[ScheduleResponse],
    summary="Get my schedules (current doctor)",
)
async def get_my_schedules(
        current_user: UserEntity = Depends(get_current_user),
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    entities = await schedule_use_case.get_my_schedules(current_user.id)
    return [ScheduleResponse.from_entity(e) for e in entities]


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[ScheduleResponse],
    summary="Get schedules by doctor ID",
)
async def get_doctor_schedules(
        doctor_id: int,
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    entities = await schedule_use_case.get_schedules_by_doctor_id(doctor_id)
    return [ScheduleResponse.from_entity(e) for e in entities]


@router.get(
    "/doctor/{doctor_id}/slots",
    response_model=list[TimeSlotResponse],
    summary="Get available time slots for a doctor on a specific date",
)
async def get_available_slots(
        doctor_id: int,
        date: date = Query(..., description="Date to check availability"),
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await schedule_use_case.get_available_slots(doctor_id, date)


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Get schedule by ID",
)
async def get_schedule(
        schedule_id: int,
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    entity = await schedule_use_case.get_schedule_by_id(schedule_id)
    return ScheduleResponse.from_entity(entity)


@router.patch(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="Update schedule",
)
async def update_schedule(
        schedule_id: int,
        request: ScheduleUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    dto = UpdateScheduleDTO(
        day_of_week=request.day_of_week,
        start_time=request.start_time,
        end_time=request.end_time,
        slot_duration_minutes=request.slot_duration_minutes,
        is_active=request.is_active,
    )
    entity = await schedule_use_case.update_schedule(schedule_id, dto, current_user.id)
    return ScheduleResponse.from_entity(entity)


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete schedule",
)
async def delete_schedule(
        schedule_id: int,
        current_user: UserEntity = Depends(get_current_user),
        schedule_use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    await schedule_use_case.delete_schedule(schedule_id, current_user.id)
