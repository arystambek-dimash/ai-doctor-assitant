from typing import List

from fastapi import APIRouter, Depends, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.specializations import SpecializationResponse, \
    SpecializationWithCountResponse
from src.presentation.api.schemas.responses.specializations import SpecializationCreateRequest, \
    SpecializationUpdateRequest
from src.presentation.dependencies import get_current_user, get_specialization_use_case, requires_roles
from src.use_cases.specializations.dto import CreateSpecializationDTO, UpdateSpecializationDTO
from src.use_cases.specializations.use_case import SpecializationUseCase

router = APIRouter(prefix="/specializations", tags=["Specializations"])


@router.post(
    "",
    response_model=SpecializationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_specialization(
        request: SpecializationCreateRequest,
        use_case: SpecializationUseCase = Depends(get_specialization_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.create_specialization(
        CreateSpecializationDTO(
            title=request.title,
            description=request.description,
        )
    )


@router.get(
    "",
    response_model=List[SpecializationWithCountResponse]
)
async def get_all_specializations(
        use_case: SpecializationUseCase = Depends(get_specialization_use_case),
):
    return await use_case.get_all_specializations_with_count()


@router.patch(
    "/{specialization_id}",
    response_model=SpecializationResponse
)
async def update_specialization(
        specialization_id: int,
        request: SpecializationUpdateRequest,
        use_case: SpecializationUseCase = Depends(get_specialization_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.update_specialization(
        specialization_id, UpdateSpecializationDTO(
            title=request.title,
            description=request.description,
        )
    )


@router.delete(
    "/{specialization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_specialization(
        specialization_id: int,
        specialization_use_case: SpecializationUseCase = Depends(get_specialization_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    await specialization_use_case.delete_specialization(specialization_id)
