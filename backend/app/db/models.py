# Deprecated: these SQLAlchemy models are no longer used at runtime — the app
# talks to Supabase over its REST API via the supabase-py client (see
# app/core/supabase_client.py). Kept only as a reference for the table shapes;
# see app/db/schema.sql for the authoritative DDL to run in Supabase.
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SkillProfile(Base):
    """Mirrors the skill-analysis payload produced by Team 1."""
    __tablename__ = "skill_profiles"

    skill_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    current_role = Column(String(100), nullable=True)
    target_role = Column(String(100), nullable=True)
    skills = Column(JSONB, nullable=False, default=dict)          # {"Python": 8, "FastAPI": 7}
    skill_gaps = Column(JSONB, nullable=False, default=list)      # [{"skill": "System Design", "requiredLevel": 8}]
    role_alignment = Column(String(30), nullable=True)            # ALIGNED / MISALIGNED
    resume_path = Column(String(500), nullable=True)
    status = Column(String(30), nullable=False, default="COMPLETED")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    roadmaps = relationship("Roadmap", back_populates="skill_profile")


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=True)                 # udemy, coursera, internal
    external_course_id = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    difficulty_level = Column(String(20), nullable=True)          # beginner / intermediate / advanced
    duration_hours = Column(Numeric(6, 2), nullable=True)
    url = Column(String(500), nullable=True)
    prerequisites = Column(JSONB, nullable=False, default=list)   # ["Python", "Statistics"]
    skills_taught = Column(JSONB, nullable=False, default=list)   # ["System Design"]
    rating = Column(Numeric(3, 2), nullable=True)
    enrollment_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    roadmap_courses = relationship("RoadmapCourse", back_populates="course")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    roadmap_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    skill_profile_id = Column(UUID(as_uuid=True), ForeignKey("skill_profiles.skill_id"), nullable=True)
    target_role = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="active")   # active / completed / paused / cancelled
    hours_per_week = Column(Integer, nullable=True)
    learning_rate = Column(String(20), nullable=True)               # beginner / intermediate / advanced
    total_courses = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    skill_profile = relationship("SkillProfile", back_populates="roadmaps")
    courses = relationship("RoadmapCourse", back_populates="roadmap", order_by="RoadmapCourse.sequence_order")


class RoadmapCourse(Base):
    __tablename__ = "roadmap_courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.roadmap_id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.course_id"), nullable=False)
    sequence_order = Column(Integer, nullable=False, default=0)
    month = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="not_started")  # not_started / in_progress / completed / skipped
    completion_percentage = Column(Integer, default=0)
    quiz_score = Column(Integer, nullable=True)
    hours_spent = Column(Numeric(5, 2), default=0)
    notes = Column(Text, nullable=True)

    roadmap = relationship("Roadmap", back_populates="courses")
    course = relationship("Course", back_populates="roadmap_courses")
