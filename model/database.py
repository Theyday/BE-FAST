from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")

print("--- DATABASE CONNECTION DEBUG ---")
print(f"DATABASE_URL used for engine creation: {DATABASE_URL}")
print(f"DB_HOST from settings: {settings.DB_HOST}")
print(f"DB_SSLMODE from settings: {settings.DB_SSLMODE}")
print("---------------------------------")

# DB_SSLMODE 값에 따라 asyncpg에 맞는 SSL 설정을 구성합니다.
connect_args = {}
if settings.DB_SSLMODE == 'disable':
    connect_args["ssl"] = False
elif settings.DB_SSLMODE == 'require':
    connect_args["ssl"] = True

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args  # 생성자에 connect_args 추가
)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session