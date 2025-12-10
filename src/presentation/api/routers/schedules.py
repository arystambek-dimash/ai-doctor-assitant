from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status

from src.domain.entities.users import UserEntity, UserEntityWithDetails
from src.presentation.api.schemas.requests.schedules import ScheduleCreateRequest, ScheduleUpdateRequest
from src.presentation.api.schemas.responses.schedules import ScheduleResponse, TimeSlotResponse
from src.presentation.dependencies import get_current_user, get_schedule_use_case, requires_roles
from src.use_cases.schedules.dto import CreateScheduleDTO, UpdateScheduleDTO
from src.use_cases.schedules.use_case import ScheduleUseCase

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post(
    "",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
        request: ScheduleCreateRequest,
        current_user: UserEntityWithDetails = Depends(requires_roles(is_doctor=True)),
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await use_case.create_schedule(
        CreateScheduleDTO(
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            slot_duration_minutes=request.slot_duration_minutes,
            is_active=request.is_active,
            doctor_id=current_user.doctor_id,
        )
    )


@router.get(
    "/me",
    response_model=List[ScheduleResponse],
)
async def get_my_schedules(
        current_user: UserEntity = Depends(get_current_user),
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await use_case.get_my_schedules(current_user.id)


@router.get(
    "/doctor/{doctor_id}",
    response_model=List[ScheduleResponse],
)
async def get_doctor_schedules(
        doctor_id: int,
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await use_case.get_schedules_by_doctor_id(doctor_id)


@router.get(
    "/doctor/{doctor_id}/slots",
    response_model=List[TimeSlotResponse],
)
async def get_available_slots(
        doctor_id: int,
        slot_date: date = Query(..., description="Date to check availability"),
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await use_case.get_available_slots(doctor_id, slot_date)


@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
async def get_schedule(
        schedule_id: int,
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
):
    return await use_case.get_schedule_by_id(schedule_id)


@router.patch(
    "/{schedule_id}",
    response_model=ScheduleResponse,
)
async def update_schedule(
        schedule_id: int,
        request: ScheduleUpdateRequest,
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
        current_user: UserEntity = Depends(requires_roles(is_doctor=True)),
):
    return await use_case.update_schedule(
        schedule_id,
        UpdateScheduleDTO(
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            slot_duration_minutes=request.slot_duration_minutes,
            is_active=request.is_active,
        ),
        doctor_id=current_user.id,
    )


@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_schedule(
        schedule_id: int,
        use_case: ScheduleUseCase = Depends(get_schedule_use_case),
        current_user: UserEntity = Depends(requires_roles(is_doctor=True))
):
    await use_case.delete_schedule(schedule_id, current_user.id)
