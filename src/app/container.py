from dependency_injector import containers, providers

from src.app.settings import Settings
from src.infrastructure.database.core import create_engine, create_session_factory
from src.infrastructure.services.jwt_service import JWTService
from src.infrastructure.services.openai_service import OpenAIService
from src.infrastructure.services.password_service import PasswordService


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.presentation.dependencies"
        ]
    )

    settings = providers.Singleton(Settings)

    engine = providers.Singleton(
        create_engine,
        db_url=settings.provided.db_url,
        echo=False
    )

    session_factory = providers.Singleton(
        create_session_factory,
        engine=engine
    )

    jwt_service = providers.Singleton(
        JWTService,
        jwt_access_secret_key=settings.provided.JWT_ACCESS_TOKEN_SECRET_KEY,
        jwt_refresh_secret_key=settings.provided.JWT_REFRESH_TOKEN_SECRET_KEY,
    )

    password_service = providers.Singleton(PasswordService)

    openai_service = providers.Factory(
        OpenAIService,
        api_key=settings.provided.OPENAI_API_KEY
    )
