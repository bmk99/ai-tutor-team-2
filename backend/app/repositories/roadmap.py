from uuid import UUID
from typing import Optional

from app.core.supabase_client import get_async_supabase
from app.core.exceptions import DatabaseException

ROADMAP_TABLE = "roadmaps"
ROADMAP_COURSE_TABLE = "roadmap_courses"
COURSE_TABLE = "courses"

# Embedded-relation select: pulls roadmap_courses rows plus their joined course row.
_ROADMAP_SELECT = f"*, {ROADMAP_COURSE_TABLE}(*, {COURSE_TABLE}(*))"


class RoadmapRepository:
    async def get_active_by_user_id(self, user_id: UUID) -> Optional[dict]:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(ROADMAP_TABLE)
                .select(_ROADMAP_SELECT)
                .eq("user_id", str(user_id))
                .eq("status", "active")
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return self._normalize(data[0]) if data else None

    async def get_by_id(self, roadmap_id: UUID) -> Optional[dict]:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(ROADMAP_TABLE)
                .select(_ROADMAP_SELECT)
                .eq("roadmap_id", str(roadmap_id))
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return self._normalize(data[0]) if data else None

    async def create(self, data: dict) -> dict:
        sb = await get_async_supabase()
        try:
            result = await sb.table(ROADMAP_TABLE).insert(data).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data[0]

    async def update(self, roadmap_id: UUID, data: dict) -> None:
        sb = await get_async_supabase()
        try:
            await sb.table(ROADMAP_TABLE).update(data).eq("roadmap_id", str(roadmap_id)).execute()
        except Exception as exc:
            raise DatabaseException() from exc

    @staticmethod
    def _normalize(row: dict) -> dict:
        """Renames the embedded roadmap_courses relation to `courses`, and each
        embedded course sub-relation to `course`, to match the shape the
        service/response layer expects."""
        row = {**row}
        rcs = row.pop(ROADMAP_COURSE_TABLE, None) or []
        row["courses"] = [
            {**rc, "course": rc.pop(COURSE_TABLE, None)} for rc in rcs
        ]
        row["courses"].sort(key=lambda rc: rc.get("sequence_order") or 0)
        return row


class RoadmapCourseRepository:
    async def get_by_id(self, roadmap_course_id: UUID) -> Optional[dict]:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(ROADMAP_COURSE_TABLE)
                .select("*")
                .eq("id", str(roadmap_course_id))
                .limit(1)
                .execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return data[0] if data else None

    async def create(self, data: dict) -> dict:
        sb = await get_async_supabase()
        try:
            result = await sb.table(ROADMAP_COURSE_TABLE).insert(data).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data[0]

    async def update(self, roadmap_course_id: UUID, data: dict) -> dict:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(ROADMAP_COURSE_TABLE)
                .update(data)
                .eq("id", str(roadmap_course_id))
                .execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data[0]
