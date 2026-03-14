from urllib.parse import urlencode

from fastapi import APIRouter, Depends, status, Query
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing_extensions import Literal

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
    user = await use_case.register(
        CreateUserDTO(
            email=str(request.email),
            password_hash=request.password,
            full_name=request.full_name,
            phone=request.phone,
            is_admin=False,
        )
    )
    return UserResponse.from_orm(user)


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
            email=str(request.email),
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


@router.get("/google")
async def auth_google(request: Request, platform: Literal["web", "mobile"] = Query(default="web")):
    settings = request.app.state.settings
    request.session["oauth_platform"] = platform

    redirect_uri = f"{settings.BACKEND_URL}/api/v1/users/google/callback"

    return await request.app.state.oauth.google.authorize_redirect(
        request,
        redirect_uri=redirect_uri,
    )


@router.get("/google/callback")
async def auth_google_callback(
        request: Request,
        controller: UserUseCase = Depends(get_user_use_case),
):
    result = await controller.google_callback(request)
    settings = request.app.state.settings
    platform = request.session.pop("oauth_platform", "web")

    if platform == "mobile":
        scheme = settings.MOBILE_REDIRECT_SCHEME
        params = urlencode({
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "user_id": result["user"]["id"],
            "email": result["user"]["email"],
        })
        return RedirectResponse(url=f"{scheme}://auth/callback?{params}")

    redirect = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard", status_code=302)

    redirect.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=60 * 15,
    )
    redirect.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )

    return redirect
