from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    user_id: UUID
    hours_per_week: int
    learning_rate: str   # beginner | intermediate | advanced


class RoadmapCourseItem(BaseModel):
    course_id: UUID
    course_name: str
    sequence_order: int
    month: Optional[int]
    status: str
    completion_percentage: int
    duration_hours: Optional[float] = None


class RoadmapResponse(BaseModel):
    roadmap_id: UUID
    user_id: UUID
    target_role: Optional[str]
    status: str
    hours_per_week: Optional[int]
    learning_rate: Optional[str]
    total_courses: int
    courses: List[RoadmapCourseItem]


class ProgressUpdateRequest(BaseModel):
    completion_percentage: int
    quiz_score: Optional[int] = None
    hours_spent: Optional[float] = None
    notes: Optional[str] = None
