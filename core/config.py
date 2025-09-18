from functools import lru_cache
from pydantic import BaseSettings, BaseModel
from dotenv import load_dotenv
from datetime import timedelta # Import timedelta

load_dotenv()

class BaseConfig(BaseSettings):

    # App Settings
    PROJECT_NAME: str = 'theyday'
    API_V1_STR: str = '/api/v1'

    # Database Settings
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'theyday'
    USER: str = 'monstazo'
    PASSWORD: str = 'tidlsl!2'
    SQLALCHEMY_DATABASE_URI: str = f'postgresql://{USER}:{PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # JWT Settings
    SECRET_KEY: str = '404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970'
    TOKEN_LOCATION: set = {'headers'}
    CSRF_PROTECT: bool = False
    COOKIE_SECURE: bool = False  # should be True in production
    COOKIE_SAMESITE: str = 'lax'  # should be 'lax' or 'strict' in production
    ACCESS_TOKEN_EXPIRES_DAYS: int = 30 # For readability
    REFRESH_TOKEN_EXPIRES_DAYS: int = 365 # For readability

    # NAVER Cloud SMS 설정
    NAVER_CLOUD_SMS_ACCESS_KEY: str = "ncp_iam_BPAMKR32W21UAxr3DgGK"
    NAVER_CLOUD_SMS_SECRET_KEY: str = "ncp_iam_BPKMKRHyXWQxmTMjCoY1sStJXbjsKeSVmX"
    NAVER_CLOUD_SMS_SERVICE_ID: str = "ncp:sms:kr:353811575184:theyday"

    # 메일 서버 설정
    MAIL_USERNAME: str = "togg0524@gmail.com"
    MAIL_PASSWORD: str = "yhgj xelq kwaj hapq"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Redis Verification Code Expiration
    PHONE_VERIFICATION_EXPIRATION: int = 5 # minutes
    EMAIL_VERIFICATION_EXPIRATION: int = 10 # minutes

    # ADMIN Settings
    ADMIN_USERNAME: str = 'admin'
    ADMIN_EMAIL: str = 'admin@417.co.kr'
    ADMIN_PASSWORD: str = 'qwe123123'

    # REDIS settings
    REDIS_HOST: str
    REDIS_PORT: int

# --- local 프로파일 설정 ---
class LocalConfig(BaseConfig):
    SERVER_PORT: int = 8080
    SERVER_ADDRESS: str = "localhost"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    SERVER_NAME: str = "local_server"


# --- blue 프로파일 설정 ---
class BlueConfig(BaseConfig):
    SERVER_PORT: int = 8080
    SERVER_ADDRESS: str = "13.124.21.41"
    SERVER_NAME: str = "blue_server"


# --- green 프로파일 설정 ---
class GreenConfig(BaseConfig):
    SERVER_PORT: int = 8081
    SERVER_ADDRESS: str = "13.124.21.41"
    SERVER_NAME: str = "green_server"

# 환경변수 APP_ENV에 따라 설정을 로드하는 함수
@lru_cache()
def get_settings() -> BaseConfig:
    import os
    profile = os.getenv('APP_ENV', 'local').lower()
    if profile == 'local':
        return LocalConfig()
    elif profile == 'blue':
        return BlueConfig()
    elif profile == 'green':
        return GreenConfig()
    else:
        raise ValueError(f"Unknown PROFILE: {profile}")

settings = get_settings()

class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_token_location: set = settings.TOKEN_LOCATION
    authjwt_cookie_csrf_protect: bool = settings.CSRF_PROTECT
    authjwt_cookie_secure: bool = settings.COOKIE_SECURE
    authjwt_cookie_samesite: str = settings.COOKIE_SAMESITE
    authjwt_access_token_expires: timedelta = timedelta(days=settings.ACCESS_TOKEN_EXPIRES_DAYS)
    authjwt_refresh_token_expires: timedelta = timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)