import jwt
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.app.container import AppContainer
from src.domain.errors import BadRequestException, UnauthorizedException
from src.domain.interfaces.repositories import IUserRepository
from src.domain.interfaces.uow import IUoW
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.password_service import PasswordService
from src.use_cases.users.users import UserUseCase

http_bearer = HTTPBearer()


@inject
async def get_user_use_case(
        uow: IUoW = Depends(Provide[AppContainer.uow]),
        user_repository: IUserRepository = Depends(Provide[AppContainer.user_repository]),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
        password_service: PasswordService = Depends(Provide[AppContainer.password_service])
) -> UserUseCase:
    return UserUseCase(
        uow=uow,
        user_repository=user_repository,
        jwt_service=jwt_service,
        password_service=password_service,
    )


@inject
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        jwt_service: JWTService = Depends(Provide[AppContainer.jwt_service]),
        user_repository: IUserRepository = Depends(Provide[AppContainer.user_repository]),
):
    try:
        token = credentials.credentials
        if not token:
            raise BadRequestException("Token is required")

        decoded_token = jwt_service.decode_access_token(token)

        user_id: int | None = decoded_token.get("user_id")
        if not user_id:
            raise UnauthorizedException("Invalid token")

        return await user_repository.get_user_by_id(user_id)

    except jwt.ExpiredSignatureError:
        raise BadRequestException("Token is expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")
