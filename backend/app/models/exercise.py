"""
Exercise (ejercicio) model.

Self-referencing via `progresses_from_id`: calisthenics training is
organized around progression chains (e.g. "knee push-ups -> standard
push-ups -> one-arm push-ups"), so each exercise can point back at the
prior step in its own chain rather than needing a separate table just to
express "comes before". It's nullable because the first step of a
progression line has no predecessor. `progression_line` + `level` together
identify where an exercise sits within its chain (see the unique
constraint below); `progresses_from_id` is what actually lets you walk
the chain programmatically without re-deriving order from `level` alone.

Per CLAUDE.md section 4, this entity is still a draft pending review
against the user's exercise-table ebook -- expect fields here (e.g.
difficulty_level naming, category granularity) to change.

`level_variant` exists because the source material (the ebook index)
genuinely assigns the same numeric level to two different exercises
within one progression_line more than once (e.g. two distinct Level-16
entries under "Planche") -- that's the book's own structure, not a data
error to collapse or fudge a level number to work around. The unique
constraint is therefore on (progression_line, level, level_variant), not
just (progression_line, level); level_variant is NULL for the vast
majority of rows where no such collision exists.

`level` is nullable because the book itself marks some entries "N/A" --
no single level applies (e.g. "Handstand Walking", "Asian Squat").
"""

import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Exercise(Base):
    __tablename__ = "exercise"
    __table_args__ = (
        UniqueConstraint(
            "progression_line",
            "level",
            "level_variant",
            name="uq_exercise_line_level_variant",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # Expected values (no DB-level enum yet, see CLAUDE.md "exercise is a
    # draft"): "Push", "Pull", "Legs", "Core", "Static".
    movement_pattern: Mapped[str] = mapped_column(String, nullable=False)
    # Name of the progression chain this exercise belongs to, e.g.
    # "Pull-ups", "Front Lever".
    progression_line: Mapped[str] = mapped_column(String, nullable=False)
    # Position within progression_line (1 = first step). Nullable: the
    # book marks some entries "N/A" (no single level applies).
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Disambiguates two exercises the book assigns the same level within
    # the same progression_line (see class docstring). 'a'/'b' etc.; NULL
    # when there's no collision to disambiguate.
    level_variant: Mapped[str | None] = mapped_column(String(1), nullable=True)
    # Expected values: "Bar", "Rings", "Parallel Bars", "Floor", "None".
    equipment: Mapped[str | None] = mapped_column(String, nullable=True)
    progresses_from_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exercise.id"), nullable=True
    )
    book_page: Mapped[int | None] = mapped_column(Integer, nullable=True)

    progresses_from: Mapped["Exercise | None"] = relationship(
        "Exercise", remote_side=[id], back_populates="progresses_to"
    )
    progresses_to: Mapped[list["Exercise"]] = relationship(
        "Exercise", back_populates="progresses_from"
    )
    routine_exercises: Mapped[list["RoutineExercise"]] = relationship(
        "RoutineExercise", back_populates="exercise"
    )
    session_sets: Mapped[list["SessionSet"]] = relationship(
        "SessionSet", back_populates="exercise"
    )
