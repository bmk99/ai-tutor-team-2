from uuid import UUID
from typing import Optional

from app.core.supabase_client import get_async_supabase
from app.core.exceptions import DatabaseException

ROADMAP_TABLE = "roadmaps"


class RoadmapRepository:
    """Data access for the ``roadmaps`` table. Each row stores a full
    week-by-week learning plan as a JSONB ``plan`` document."""

    async def get_latest_by_user_id(self, user_id: UUID) -> Optional[dict]:
        """Returns the most recently created roadmap for a user, or ``None``."""
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(ROADMAP_TABLE)
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return data[0] if data else None

    async def create(self, data: dict) -> dict:
        """Inserts a new roadmap row and returns the persisted record."""
        sb = await get_async_supabase()
        try:
            result = await sb.table(ROADMAP_TABLE).insert(data).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data[0]
