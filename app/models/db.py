from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.database import Base

DATABASE_URL = "postgresql+asyncpg://aiops:aiops@localhost:5432/aiops"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """Crée les tables si elles n'existent pas encore (suffisant pour le dev / démo)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session