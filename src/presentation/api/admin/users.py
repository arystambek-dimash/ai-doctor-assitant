from typing import List

from fastapi import APIRouter, status, Depends, Query

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.users import UserCreateRequest, UserUpdateRequest
from src.presentation.api.schemas.responses.users import UserResponse
from src.presentation.dependencies import get_user_use_case, requires_roles
from src.use_cases.users.dto import CreateUserDTO, UpdateUserDTO
from src.use_cases.users.use_case import UserUseCase

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get(
    "",
    response_model=List[UserResponse]
)
async def get_all_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """Get all users (admin only)"""
    return await use_case.get_all_users(skip=skip, limit=limit)


@router.get(
    "/patients",
    response_model=List[UserResponse]
)
async def get_all_patients(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """Get all patients (admin only)"""
    return await use_case.get_all_patients(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse
)
async def get_user_by_id(
        user_id: int,
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """Get user by ID (admin only)"""
    return await use_case.get_user_by_id(user_id)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        request: UserCreateRequest,
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    return await use_case.register(
        CreateUserDTO(
            email=request.email.__str__(),
            password_hash=request.password,
            full_name=request.full_name,
            phone=request.phone,
            is_admin=request.is_admin,
        )
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
async def update_user(
        user_id: int,
        request: UserUpdateRequest,
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """Update user (admin only)"""
    return await use_case.update_user(
        user_id,
        UpdateUserDTO(
            full_name=request.full_name,
            phone=request.phone,
            is_admin=request.is_admin,
        )
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
        user_id: int,
        use_case: UserUseCase = Depends(get_user_use_case),
        current_user: UserEntity = Depends(requires_roles(is_admin=True)),
):
    """Delete user (admin only)"""
    await use_case.delete_user(user_id)
