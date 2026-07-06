from datetime import datetime
from typing import List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SkillGap(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    skill: str
    required_level: int = Field(..., alias="requiredLevel")


class SkillProfileIngestRequest(BaseModel):
    """Matches the exact payload produced by Team 1's skill-analysis workflow."""
    model_config = ConfigDict(populate_by_name=True)

    skill_id: UUID = Field(..., alias="skillId")
    user_id: UUID = Field(..., alias="userId")
    username: str
    email: str
    current_role: str = Field(..., alias="currentRole")
    target_role: str = Field(..., alias="targetRole")
    skills: Dict[str, int]
    skill_gaps: List[SkillGap] = Field(default_factory=list, alias="skillGaps")
    role_alignment: str = Field(..., alias="roleAlignment")
    resume_path: str | None = Field(default=None, alias="resumePath")
    status: str
    created_at: datetime = Field(..., alias="createdAt")


class SkillProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: UUID
    user_id: UUID
    username: str
    email: str
    current_role: str | None
    target_role: str | None
    skills: Dict[str, int]
    skill_gaps: List[dict]
    role_alignment: str | None
    resume_path: str | None
    status: str
    created_at: datetime
