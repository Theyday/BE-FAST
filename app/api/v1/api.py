from fastapi import APIRouter

from .endpoints import user, category, schedule, event, task, routine

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(schedule.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(event.router, prefix="/events", tags=["events"])
api_router.include_router(task.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(routine.router, prefix="/routines", tags=["routines"])
