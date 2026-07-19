"""
Routine (rutina) model -- a named plan of exercises for a student.
"""

import uuid

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Routine(Base):
    __tablename__ = "routine"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("student.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    # Named "generation_method" rather than the original draft's
    # "created_by" (CLAUDE.md section 4): "created_by" reads like a
    # reference to a user account, but this only ever holds "manual" or
    # "auto". Keeping it distinct avoids clashing with a real
    # created_by_user_id once auth exists.
    generation_method: Mapped[str] = mapped_column(String, nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="routines")
    routine_exercises: Mapped[list["RoutineExercise"]] = relationship(
        "RoutineExercise", back_populates="routine"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="routine"
    )
