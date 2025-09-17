from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from core.config import settings, AuthJWTSettings
from app.api.v1.api import api_router

app = FastAPI(title=settings.PROJECT_NAME,
              openapi_url=f"{settings.API_V1_STR}/openapi.json")

@AuthJWT.load_config
def get_auth_jwt_config() -> AuthJWTSettings:
    return AuthJWTSettings()

@app.exception_handler(AuthJWTException)
def auth_jwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# # CORS
# # this section is for allowing the frontend to access the backend during development
# # this section must be removed in production
# # origins = [
# #     'http://localhost:3000',
# #     'http://localhost:8000',
# # ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['http://localhost:3000'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )
# # End CORS

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get('/')
def root():
    return {'message': 'Hello World'}
