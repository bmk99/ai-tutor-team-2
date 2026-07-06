from fastapi import APIRouter
from app.api.v1.skills import router as skills_router
from app.api.v1.courses import router as courses_router
from app.api.v1.roadmap import router as roadmap_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(skills_router)
api_router.include_router(courses_router)
api_router.include_router(roadmap_router)
