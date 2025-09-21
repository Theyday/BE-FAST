from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.config import settings
import ssl

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")

# DB_SSLMODE 값에 따라 asyncpg에 맞는 SSL 설정을 구성합니다.
connect_args = {}
if settings.DB_SSLMODE == 'disable':
    connect_args["ssl"] = False
elif settings.DB_SSLMODE == 'require':
    # SSLContext를 직접 만들어 서버 인증서 검증을 건너뛰도록 설정
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

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