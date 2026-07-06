from uuid import UUID
from fastapi import APIRouter
from app.schemas.skill import SkillProfileIngestRequest, SkillProfileResponse
from app.services.skill_profile import skill_profile_service

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/ingest", response_model=SkillProfileResponse)
async def ingest_skill_profile(payload: SkillProfileIngestRequest):
    """Receives the skill-analysis JSON produced by Team 1's workflow and stores it."""
    profile = await skill_profile_service.ingest(payload)
    return SkillProfileResponse.model_validate(profile)


@router.get("/{user_id}", response_model=SkillProfileResponse)
async def get_skill_profile(user_id: UUID):
    profile = await skill_profile_service.get_by_user_id(user_id)
    return SkillProfileResponse.model_validate(profile)
