from urllib.request import Request

from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from src.app.container import AppContainer
from src.domain.errors import BaseError
from src.presentation.api.routers.users import router as users_router


def create_app() -> FastAPI:
    container = AppContainer()
    app = FastAPI()

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
    app.include_router(v1_router)
    return app


app = create_app()
