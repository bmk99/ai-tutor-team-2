import math
import uuid
from uuid import UUID
from app.repositories.skill_profile import SkillProfileRepository
from app.repositories.course import CourseRepository
from app.repositories.roadmap import RoadmapRepository, RoadmapCourseRepository
from app.schemas.roadmap import RecommendationRequest
from app.core.exceptions import SkillProfileNotFoundException, RoadmapNotFoundException, ConfigurationException, LLMException
from app.core.logging import get_logger
from app.core.config import get_settings
from app.core import gemini_client

logger = get_logger(__name__)

DEFAULT_HOURS_PER_COURSE = 10  # fallback if a course has no duration set


class RecommendationService:
    @staticmethod
    async def _find_candidate_courses(
        course_repo: CourseRepository, skill_gaps: list[dict], gap_skill_names: list[str]
    ) -> list[dict]:
        """Finds the most relevant courses for a user's skill gaps using Gemini embeddings
        + pgvector similarity search. Requires GEMINI_API_KEY to be set."""
        if not get_settings().GEMINI_API_KEY:
            raise ConfigurationException("GEMINI_API_KEY is not configured. Course recommendations require LLM embeddings.")

        if not skill_gaps:
            logger.warning("No skill gaps found, returning empty course list")
            return []

        gap_text = "Skills to learn: " + ", ".join(
            f"{gap.get('skill')} (target level {gap.get('requiredLevel') or gap.get('required_level')})"
            for gap in skill_gaps
        )

        try:
            query_embedding = await gemini_client.embed_text(gap_text, task_type="retrieval_query")
        except Exception as exc:
            logger.error("Failed to generate embedding for skill gaps", exc_info=exc)
            raise LLMException("Failed to generate embedding for skill gaps. Check GEMINI_API_KEY and network connectivity.") from exc

        courses = await course_repo.list_by_embedding(query_embedding, limit=10)
        if not courses:
            logger.warning("No courses found via vector search for skill gaps", gap_text=gap_text)
        return courses

    async def generate_roadmap(self, request: RecommendationRequest) -> dict:
        skill_repo = SkillProfileRepository()
        profile = await skill_repo.get_by_user_id(request.user_id)
        if not profile:
            raise SkillProfileNotFoundException(str(request.user_id))

        skill_gaps = profile.get("skill_gaps") or []
        gap_skill_names = [gap.get("skill") for gap in skill_gaps]

        course_repo = CourseRepository()
        candidate_courses = await self._find_candidate_courses(course_repo, skill_gaps, gap_skill_names)

        # Deactivate any existing active roadmap for this user (MVP: single active roadmap per user)
        roadmap_repo = RoadmapRepository()
        existing = await roadmap_repo.get_active_by_user_id(request.user_id)
        if existing:
            await roadmap_repo.update(existing["roadmap_id"], {"status": "cancelled"})

        roadmap_id = uuid.uuid4()
        roadmap = await roadmap_repo.create({
            "roadmap_id": str(roadmap_id),
            "user_id": str(request.user_id),
            "skill_profile_id": profile["skill_id"],
            "target_role": profile.get("target_role"),
            "status": "active",
            "hours_per_week": request.hours_per_week,
            "learning_rate": request.learning_rate,
            "total_courses": len(candidate_courses),
        })

        roadmap_course_repo = RoadmapCourseRepository()
        cumulative_hours = 0.0
        for index, course in enumerate(candidate_courses, start=1):
            duration = float(course.get("duration_hours") or DEFAULT_HOURS_PER_COURSE)
            cumulative_hours += duration
            month = max(1, math.ceil(cumulative_hours / max(request.hours_per_week, 1) / 4))

            await roadmap_course_repo.create({
                "id": str(uuid.uuid4()),
                "roadmap_id": str(roadmap_id),
                "course_id": course["course_id"],
                "sequence_order": index,
                "month": month,
                "status": "not_started",
                "completion_percentage": 0,
            })

        logger.info("Roadmap generated", user_id=str(request.user_id), roadmap_id=str(roadmap_id))

        refreshed = await roadmap_repo.get_by_id(roadmap_id)
        return refreshed

    async def get_active_roadmap(self, user_id: UUID) -> dict:
        roadmap_repo = RoadmapRepository()
        roadmap = await roadmap_repo.get_active_by_user_id(user_id)
        if not roadmap:
            raise RoadmapNotFoundException(str(user_id))
        return roadmap

    async def update_progress(self, roadmap_course_id: UUID, update: dict) -> dict:
        rc_repo = RoadmapCourseRepository()
        roadmap_course = await rc_repo.get_by_id(roadmap_course_id)
        if not roadmap_course:
            raise RoadmapNotFoundException(str(roadmap_course_id))

        patch = {k: v for k, v in update.items() if v is not None}
        completion = patch.get("completion_percentage", roadmap_course.get("completion_percentage", 0))
        if completion >= 100:
            patch["status"] = "completed"
        elif completion > 0:
            patch["status"] = "in_progress"

        updated = await rc_repo.update(roadmap_course_id, patch)
        return updated


recommendation_service = RecommendationService()
