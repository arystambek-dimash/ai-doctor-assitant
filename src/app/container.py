from typing import AsyncGenerator

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.app.settings import Settings
from src.infrastructure.database.core import create_engine, create_session_factory
from src.infrastructure.database.uow import UoW


async def get_session(
        session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
        ]
    )

    settings = Settings()

    engine = providers.Singleton(create_engine, db_url=settings.db_url, echo=False)

    session_factory = providers.Resource(
        create_session_factory, engine=engine
    )

    session = providers.Resource(get_session, session_factory)
    uow = providers.Resource(UoW, session=session)
