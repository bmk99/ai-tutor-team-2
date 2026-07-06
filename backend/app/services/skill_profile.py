from uuid import UUID
from app.repositories.skill_profile import SkillProfileRepository
from app.schemas.skill import SkillProfileIngestRequest
from app.core.exceptions import SkillProfileNotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)


class SkillProfileService:
    async def ingest(self, payload: SkillProfileIngestRequest):
        repo = SkillProfileRepository()
        data = {
            "skill_id": payload.skill_id,
            "user_id": payload.user_id,
            "username": payload.username,
            "email": payload.email,
            "current_role": payload.current_role,
            "target_role": payload.target_role,
            "skills": payload.skills,
            "skill_gaps": [gap.model_dump(by_alias=True) for gap in payload.skill_gaps],
            "role_alignment": payload.role_alignment,
            "resume_path": payload.resume_path,
            "status": payload.status,
            "created_at": payload.created_at,
        }
        profile = await repo.upsert(data)
        logger.info("Skill profile ingested", user_id=str(payload.user_id))
        return profile

    async def get_by_user_id(self, user_id: UUID):
        repo = SkillProfileRepository()
        profile = await repo.get_by_user_id(user_id)
        if not profile:
            raise SkillProfileNotFoundException(str(user_id))
        return profile


skill_profile_service = SkillProfileService()
