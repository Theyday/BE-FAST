from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session