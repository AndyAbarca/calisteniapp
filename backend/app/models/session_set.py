"""
SessionSet (sesion_set) model -- the most granular record, a single set of
a single exercise within a session. This is what the progress charts
(CLAUDE.md section 1) ultimately query and group by exercise_id.

Two different position columns, on purpose:
- `set_number`: position within *this exercise* in the session (e.g. "3rd
  set of pull-ups today"). Natural for a user logging straight-through
  workouts one exercise at a time.
- `set_order`: position within the *session as a whole*, across every
  exercise. `set_number` alone can't reconstruct chronological order once
  a workout is a circuit or superset (e.g. alternating pull-ups and
  push-ups) -- two sets can share the same set_number but happen at
  different times. `set_order` is what makes that ordering recoverable.
"""

import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SessionSet(Base):
    __tablename__ = "session_set"
    __table_args__ = (
        UniqueConstraint(
            "session_id", "exercise_id", "set_number", name="uq_session_set_number"
        ),
        UniqueConstraint("session_id", "set_order", name="uq_session_set_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("session.id"), nullable=False
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise.id"), nullable=False
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    set_order: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    added_weight_kg: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    rpe: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    session: Mapped["Session"] = relationship(
        "Session", back_populates="session_sets"
    )
    exercise: Mapped["Exercise"] = relationship(
        "Exercise", back_populates="session_sets"
    )
