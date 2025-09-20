from fastapi import FastAPI

from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME,
              openapi_url=f"{settings.API_V1_STR}/openapi.json")

# # CORS
# # this section is for allowing the frontend to access the backend during development
# # this section must be removed in production
# # origins = [
# #     'http://localhost:3000',
# #     'http://localhost:8000',
# # ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['http://localhost:3000'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )
# # End CORS

@app.get('/')
def root():
    return {'message': 'Hello World'}