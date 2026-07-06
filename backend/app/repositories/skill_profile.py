from uuid import UUID
from typing import Optional

from app.core.supabase_client import get_async_supabase
from app.core.exceptions import DatabaseException

TABLE = "skill_profiles"


class SkillProfileRepository:
    async def get_by_user_id(self, user_id: UUID) -> Optional[dict]:
        sb = await get_async_supabase()
        try:
            result = await (
                sb.table(TABLE).select("*").eq("user_id", str(user_id)).limit(1).execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data = result.data
        return data[0] if data else None

    async def upsert(self, data: dict) -> dict:
        sb = await get_async_supabase()
        record = {**data}
        record["user_id"] = str(record["user_id"])
        record["skill_id"] = str(record["skill_id"])
        if record.get("created_at") is not None:
            record["created_at"] = record["created_at"].isoformat()
        try:
            result = await (
                sb.table(TABLE).upsert(record, on_conflict="user_id").execute()
            )
        except Exception as exc:
            raise DatabaseException() from exc
        data_out = result.data
        return data_out[0] if data_out else record
