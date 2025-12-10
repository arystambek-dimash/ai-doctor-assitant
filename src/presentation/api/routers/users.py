from fastapi import APIRouter, Depends, status

from src.domain.entities.users import UserEntity
from src.presentation.api.schemas.requests.users import UserCreateRequest, UserLoginRequest
from src.presentation.api.schemas.responses.users import UserResponse, LoginResponse
from src.presentation.dependencies import get_user_use_case, get_current_user
from src.use_cases.users.dto import CreateUserDTO, LoginUserDTO
from src.use_cases.users.use_case import UserUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
        request: UserCreateRequest,
        use_case: UserUseCase = Depends(get_user_use_case),
):
    return UserResponse.from_orm(await use_case.register(
        CreateUserDTO(
            email=request.email.__str__(),
            password_hash=request.password,
            full_name=request.full_name,
            phone=request.phone,
            is_admin=request.is_admin,
        )
    )
                                 )


@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
        request: UserLoginRequest,
        use_case: UserUseCase = Depends(get_user_use_case),
):
    return await use_case.login(
        LoginUserDTO(
            email=request.email.__str__(),
            password=request.password,
        )
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(
        current_user: UserEntity = Depends(get_current_user),
):
    return current_user
