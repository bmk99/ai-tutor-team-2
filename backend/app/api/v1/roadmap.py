from uuid import UUID
from fastapi import APIRouter
from app.schemas.roadmap import RecommendationRequest, RoadmapResponse, RoadmapCourseItem, ProgressUpdateRequest
from app.services.recommendation import recommendation_service

router = APIRouter(prefix="/learning", tags=["Learning"])


def _to_roadmap_response(roadmap: dict) -> RoadmapResponse:
    return RoadmapResponse(
        roadmap_id=roadmap["roadmap_id"],
        user_id=roadmap["user_id"],
        target_role=roadmap.get("target_role"),
        status=roadmap["status"],
        hours_per_week=roadmap.get("hours_per_week"),
        learning_rate=roadmap.get("learning_rate"),
        total_courses=roadmap["total_courses"],
        courses=[
            RoadmapCourseItem(
                course_id=rc["course"]["course_id"],
                course_name=rc["course"]["course_name"],
                sequence_order=rc["sequence_order"],
                month=rc.get("month"),
                status=rc["status"],
                completion_percentage=rc["completion_percentage"],
                duration_hours=float(rc["course"]["duration_hours"]) if rc["course"].get("duration_hours") else None,
            )
            for rc in roadmap["courses"]
        ],
    )


@router.post("/recommend", response_model=RoadmapResponse)
async def recommend_roadmap(payload: RecommendationRequest):
    roadmap = await recommendation_service.generate_roadmap(payload)
    return _to_roadmap_response(roadmap)


@router.get("/roadmap/{user_id}", response_model=RoadmapResponse)
async def get_roadmap(user_id: UUID):
    roadmap = await recommendation_service.get_active_roadmap(user_id)
    return _to_roadmap_response(roadmap)


@router.post("/progress/{roadmap_course_id}")
async def update_progress(roadmap_course_id: UUID, payload: ProgressUpdateRequest):
    updated = await recommendation_service.update_progress(
        roadmap_course_id,
        payload.model_dump(exclude_unset=True),
    )
    return {
        "roadmap_course_id": updated["id"],
        "status": updated["status"],
        "completion_percentage": updated["completion_percentage"],
    }
