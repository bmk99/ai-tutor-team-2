"""Recommendation (learning-roadmap) API.

All endpoints are scoped to an employee via the ``employee_id`` path parameter
(the employee's user UUID). The flow is:

* ``POST /employees/{employee_id}/recommendations`` - build a week-by-week
  roadmap from Team 1's skill-analysis JSON, store it, and return it.
* ``GET  /employees/{employee_id}/recommendations`` - fetch the saved roadmap.
"""

from uuid import UUID

from fastapi import APIRouter

from app.schemas.recommendation import RoadmapPlan, RoadmapResponse, SkillAnalysis
from app.services.recommendation import recommendation_service

router = APIRouter(prefix="/employees", tags=["Recommendations"])


def _to_roadmap_response(roadmap: dict) -> RoadmapResponse:
    """Maps a persisted ``roadmaps`` row into the API response schema."""
    return RoadmapResponse(
        roadmap_id=roadmap["roadmap_id"],
        user_id=roadmap["user_id"],
        target_role=roadmap.get("target_role"),
        status=roadmap["status"],
        plan=RoadmapPlan.model_validate(roadmap.get("plan") or {}),
        created_at=roadmap.get("created_at"),
    )


@router.post("/{employee_id}/recommendations", response_model=RoadmapResponse)
async def create_recommendation(employee_id: UUID, analysis: SkillAnalysis) -> RoadmapResponse:
    """Generates and stores a week-by-week roadmap from an employee's skill gaps.

    Accepts Team 1's skill-analysis JSON in the request body, runs a vector
    search over the course catalogue, prompts Gemini to produce the plan, saves
    it, and returns the persisted roadmap.
    """
    roadmap = await recommendation_service.generate(employee_id, analysis)
    return _to_roadmap_response(roadmap)


@router.get("/{employee_id}/recommendations", response_model=RoadmapResponse)
async def get_recommendation(employee_id: UUID) -> RoadmapResponse:
    """Fetches the most recently saved roadmap for an employee."""
    roadmap = await recommendation_service.get_roadmap(employee_id)
    return _to_roadmap_response(roadmap)
