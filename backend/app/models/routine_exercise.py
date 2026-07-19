"""
RoutineExercise (rutina_ejercicio) model -- bridge table between routine
and exercise, carrying relationship metadata (ordering, targets).

Uses a composite primary key of (routine_id, exercise_id) instead of a
surrogate id: a given exercise appears at most once per routine, so the
natural key already uniquely identifies a row, and enforcing that via the
PK itself (rather than a separate unique constraint alongside a surrogate
id) means the constraint can't accidentally be dropped or forgotten in a
future migration.
"""

import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoutineExercise(Base):
    __tablename__ = "routine_exercise"

    routine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routine.id"), primary_key=True
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise.id"), primary_key=True
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    target_sets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)

    routine: Mapped["Routine"] = relationship(
        "Routine", back_populates="routine_exercises"
    )
    exercise: Mapped["Exercise"] = relationship(
        "Exercise", back_populates="routine_exercises"
    )
