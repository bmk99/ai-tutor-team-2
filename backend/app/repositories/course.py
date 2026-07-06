from uuid import UUID
from typing import Optional, List

from app.core.supabase_client import get_async_supabase
from app.core.exceptions import DatabaseException

TABLE = "courses"


class CourseRepository:
    async def get_by_id(self, course_id: UUID) -> Optional[dict]:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(TABLE).select("*").eq("course_id", str(course_id)).limit(1).execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return data[0] if data else None

    async def list_all(self, category: str | None = None, difficulty: str | None = None) -> List[dict]:
        sb = await get_async_supabase()
        query = sb.table(TABLE).select("*")
        if category:
            query = query.eq("category", category)
        if difficulty:
            query = query.eq("difficulty_level", difficulty)
        try:
            result = await query.execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data or []

    async def list_by_skills(self, skill_names: List[str], limit: int = 10) -> List[dict]:
        """Fallback keyword matching: returns courses whose skills_taught overlaps
        requested skills. Used only if no embedding is available (e.g. Gemini not configured)."""
        all_courses = await self.list_all()
        matched = [
            c for c in all_courses
            if any(skill in (c.get("skills_taught") or []) for skill in skill_names)
        ]
        return (matched or all_courses)[:limit]

    async def list_by_embedding(self, embedding: List[float], limit: int = 10) -> List[dict]:
        """Vector similarity search via the `match_courses` Postgres function
        (see app/db/schema.sql) — finds courses whose embedding is closest to
        the given query embedding using cosine distance (pgvector)."""
        sb = await get_async_supabase()
        try:
            result = await sb.rpc(
                "match_courses",
                {"query_embedding": embedding, "match_count": limit},
            ).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data or []

    async def create(self, data: dict) -> dict:
        sb = await get_async_supabase()
        try:
            result = await sb.table(TABLE).insert(data).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data[0]

    async def create_many(self, rows: List[dict]) -> List[dict]:
        sb = await get_async_supabase()
        try:
            result = await sb.table(TABLE).insert(rows).execute()
        except Exception as exc:
            raise DatabaseException() from exc
        return result.data or []
