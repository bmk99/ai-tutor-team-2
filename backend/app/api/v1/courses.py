from fastapi import APIRouter, Query
from app.schemas.course import CourseResponse, CourseListResponse, CourseBulkCreate
from app.services.course import course_service

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=CourseListResponse)
async def list_courses(
    category: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
):
    courses = await course_service.list_courses(category=category, difficulty=difficulty)
    return CourseListResponse(courses=[CourseResponse.model_validate(c) for c in courses])


@router.post("", response_model=CourseListResponse)
async def create_courses(payload: CourseBulkCreate):
    """Create one or many courses in a single request. Pass an array in `courses`:
    - Single: {"courses": [{...}]}
    - Bulk: {"courses": [{...}, {...}, ...]}
    Each course is embedded with Gemini (if GEMINI_API_KEY is set) before insertion."""
    courses = await course_service.create_courses_bulk(payload)
    return CourseListResponse(courses=[CourseResponse.model_validate(c) for c in courses])
