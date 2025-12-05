from urllib.request import Request

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.app.container import AppContainer
from src.domain.errors import BaseError
from src.presentation.api.routers.doctors import router as doctors_router
from src.presentation.api.routers.schedules import router as schedules_router
from src.presentation.api.routers.specializations import router as specializations_router
from src.presentation.api.routers.users import router as users_router
from src.presentation.api.routers.medical_records import router as medical_records_router
from src.presentation.api.routers.appointments import router as appointments_router
from src.presentation.api.routers.websocket_chat import router as websocket_chat_router
from src.presentation.api.routers.ai_consultations import router as ai_consultations_router


def create_app() -> FastAPI:
    container = AppContainer()
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(BaseError)
    async def bad_request_handler(_: Request, exc: BaseError):
        content = "detail" if exc.status_code < 500 else "error"
        return JSONResponse(status_code=exc.status_code, content={content: exc.message})

    @app.on_event("startup")
    async def startup():
        await container.init_resources()

    @app.on_event("shutdown")
    async def shutdown():
        await container.shutdown_resources()

    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(users_router)
    v1_router.include_router(doctors_router)
    v1_router.include_router(specializations_router)
    v1_router.include_router(schedules_router)
    v1_router.include_router(medical_records_router)
    v1_router.include_router(appointments_router)
    v1_router.include_router(websocket_chat_router)
    v1_router.include_router(ai_consultations_router)
    app.include_router(v1_router)
    return app


app = create_app()
