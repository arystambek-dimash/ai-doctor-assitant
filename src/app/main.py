from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.sessions import SessionMiddleware

from src.app.container import AppContainer
from src.domain.errors import BaseError
from src.presentation.api.admin.doctors import router as admin_doctors_router
from src.presentation.api.admin.stats import router as admin_stats_router
from src.presentation.api.admin.users import router as admin_users_router
from src.presentation.api.routers.appointments import router as appointments_router
from src.presentation.api.routers.chat import router as chat_router
from src.presentation.api.routers.doctors import router as doctors_router
from src.presentation.api.routers.medical_records import router as medical_records_router
from src.presentation.api.routers.schedules import router as schedules_router
from src.presentation.api.routers.specializations import router as specializations_router
from src.presentation.api.routers.users import router as users_router

_engine: AsyncEngine | None = None


def create_app() -> FastAPI:
    container = AppContainer()
    settings = container.settings()
    app = FastAPI(title="AI Doctor Assistant API", version="1.0.0")

    allowed_origins = [
        settings.FRONTEND_URL,
        settings.BACKEND_URL,
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server alternate
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
        expose_headers=["Content-Length", "X-Request-Id"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
    )

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "timeout": 10.0,
        },
    )

    app.state.oauth = oauth
    app.state.settings = settings

    @app.exception_handler(BaseError)
    async def bad_request_handler(_: Request, exc: BaseError):
        content = "detail" if exc.status_code < 500 else "error"
        return JSONResponse(status_code=exc.status_code, content={content: exc.message})

    @app.on_event("startup")
    async def startup():
        global _engine
        _engine = container.engine()

        try:
            password_service = container.password_service()
            admin_settings = container.settings()
            async with _engine.begin() as connection:
                await connection.execute(
                    text("""
                        INSERT INTO users (email, password_hash, full_name, is_admin, created_at, updated_at)
                        VALUES (:email, :password_hash, :full_name, TRUE, NOW(), NOW())
                        ON CONFLICT (email) DO NOTHING
                    """),
                    {
                        "email": admin_settings.SUPER_ADMIN_LOGIN,
                        "password_hash": password_service.encrypt(admin_settings.SUPER_ADMIN_PASSWORD),
                        "full_name": "Admin",
                    }
                )
        except Exception as e:
            print(f"Warning: Could not create admin user: {e}")

    @app.on_event("shutdown")
    async def shutdown():
        await container.shutdown_resources()
        global _engine
        _engine = None

    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(users_router)
    v1_router.include_router(doctors_router)
    v1_router.include_router(specializations_router)
    v1_router.include_router(schedules_router)
    v1_router.include_router(medical_records_router)
    v1_router.include_router(appointments_router)
    v1_router.include_router(chat_router)
    v1_router.include_router(admin_doctors_router)
    v1_router.include_router(admin_users_router)
    v1_router.include_router(admin_stats_router)
    app.include_router(v1_router)

    return app


app = create_app()
