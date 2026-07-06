"""Business logic for the learning-recommendation flow.

The heavy lifting is now performed by the LangGraph roadmap workflow (see
``app/workflows/agents/roadmap``). This service is a thin orchestration layer:

1. Converts the incoming ``SkillAnalysis`` into a workflow input dict.
2. Resolves and executes the roadmap workflow via the registry.
3. Stores the workflow's ``final_plan`` as a JSONB document in ``roadmaps``.
4. Returns the persisted record.
"""

import uuid
from uuid import UUID

from app.repositories.roadmap import RoadmapRepository
from app.schemas.recommendation import SkillAnalysis
from app.core.exceptions import (
    ConfigurationException,
    RoadmapNotFoundException,
)
from app.core.logging import get_logger
from app.workflows.registry import workflow_registry
from app.workflows.loader import ROADMAP_WORKFLOW_ID

logger = get_logger(__name__)


class RecommendationService:
    """Generates, saves and fetches employee learning roadmaps."""

    async def generate(self, employee_id: UUID, analysis: SkillAnalysis) -> dict:
        """Generates a week-by-week roadmap for an employee, stores it, and
        returns the persisted record."""
        workflow = workflow_registry.get(ROADMAP_WORKFLOW_ID)
        if not workflow:
            raise ConfigurationException("Roadmap workflow is not registered.")

        workflow_input = {
            "employee_id": str(employee_id),
            "current_role": analysis.current_role,
            "target_role": analysis.target_role,
            "skills": analysis.skills or {},
            "skill_gaps": [gap.model_dump() for gap in analysis.skill_gaps],
        }

        result = await workflow.run(workflow_input)
        final_plan = result["final_plan"]

        roadmap_repo = RoadmapRepository()
        roadmap = await roadmap_repo.create(
            {
                "roadmap_id": str(uuid.uuid4()),
                "user_id": str(employee_id),
                "target_role": analysis.target_role,
                "status": "active",
                "plan": final_plan,
            }
        )
        logger.info(
            "Roadmap generated and saved",
            employee_id=str(employee_id),
            roadmap_id=roadmap["roadmap_id"],
            total_weeks=final_plan.get("total_weeks"),
        )
        return roadmap

    async def get_roadmap(self, employee_id: UUID) -> dict:
        """Fetches the most recently saved roadmap for an employee."""
        roadmap_repo = RoadmapRepository()
        roadmap = await roadmap_repo.get_latest_by_user_id(employee_id)
        if not roadmap:
            raise RoadmapNotFoundException(str(employee_id))
        return roadmap


recommendation_service = RecommendationService()
