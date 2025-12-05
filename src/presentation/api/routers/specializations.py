from fastapi import APIRouter, Depends, status

from src.domain.entities.users import UserEntity
from src.domain.errors import ForbiddenException
from src.presentation.api.schemas.requests.specializations import SpecializationResponse, \
    SpecializationWithCountResponse
from src.presentation.api.schemas.responses.specializations import SpecializationCreateRequest, \
    SpecializationUpdateRequest
from src.presentation.dependencies import get_current_user, get_specialization_use_case
from src.use_cases.specializations.dto import CreateSpecializationDTO, UpdateSpecializationDTO
from src.use_cases.specializations.use_case import SpecializationUseCase

router = APIRouter(prefix="/specializations", tags=["Specializations"])


@router.post(
    "",
    response_model=SpecializationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new specialization (admin only)",
)
async def create_specialization(
        request: SpecializationCreateRequest,
        current_user: UserEntity = Depends(get_current_user),
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    if not current_user.is_admin:
        raise ForbiddenException("Only admins can create specializations")

    dto = CreateSpecializationDTO(
        title=request.title,
        description=request.description,
    )
    return await specialization_use_case.create_specialization(dto)


@router.get(
    "",
    response_model=list[SpecializationWithCountResponse],
    summary="Get all specializations with doctor count",
)
async def get_all_specializations(
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    return await specialization_use_case.get_all_specializations_with_count()


@router.get(
    "/{specialization_id}",
    response_model=SpecializationResponse,
    summary="Get specialization by ID",
)
async def get_specialization(
        specialization_id: int,
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    return await specialization_use_case.get_specialization_by_id(specialization_id)


@router.patch(
    "/{specialization_id}",
    response_model=SpecializationResponse,
    summary="Update specialization (admin only)",
)
async def update_specialization(
        specialization_id: int,
        request: SpecializationUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    if not current_user.is_admin:
        raise ForbiddenException("Only admins can update specializations")

    dto = UpdateSpecializationDTO(
        title=request.title,
        description=request.description,
    )
    return await specialization_use_case.update_specialization(specialization_id, dto)


@router.delete(
    "/{specialization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete specialization (admin only)",
)
async def delete_specialization(
        specialization_id: int,
        current_user: UserEntity = Depends(get_current_user),
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    if not current_user.is_admin:
        raise ForbiddenException("Only admins can delete specializations")

    await specialization_use_case.delete_specialization(specialization_id)
