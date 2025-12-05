from fastapi import APIRouter, Depends, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.users import UserCreateRequest, UserLoginRequest, UserUpdateRequest
from src.presentation.api.schemas.responses.users import UserResponse, LoginResponse
from src.presentation.dependencies import get_user_use_case, get_current_user
from src.use_cases.users.dto import CreateUserDTO, LoginUserDTO
from src.use_cases.users.use_case import UserUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
        request: UserCreateRequest,
        user_use_case: UserUseCase = Depends(get_user_use_case),
):
    dto = CreateUserDTO(
        email=request.email.__str__(),
        password_hash=request.password,
        full_name=request.full_name,
        phone=request.phone,
        is_admin=False,
    )
    user = await user_use_case.register(dto)
    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
)
async def login(
        request: UserLoginRequest,
        user_use_case: UserUseCase = Depends(get_user_use_case),
):
    dto = LoginUserDTO(
        email=request.email.__str__(),
        password=request.password,
    )
    result = await user_use_case.login(dto)
    return result


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
        current_user: UserEntity = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_me(
        request: UserUpdateRequest,
        current_user: UserEntity = Depends(get_current_user),
        user_use_case: UserUseCase = Depends(get_user_use_case),
):
    updated_user = await user_use_case.update_user(
        user_id=current_user.id,
        data=request.model_dump(exclude_unset=True),
    )
    return updated_user
