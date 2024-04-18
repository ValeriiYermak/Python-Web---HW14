import contextlib
import logging
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, \
    async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        """ Initialize the session manager. """

        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False,
            bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """ Provide a transactional scope around a series of operations. """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """ Get the database session. """
    async with sessionmanager.session() as session:
        return session
