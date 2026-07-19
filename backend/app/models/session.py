"""
Session (sesion) model -- a concrete execution of a routine on a given
date.

`routine_id` is deliberately nullable with ON DELETE SET NULL rather than
NOT NULL / CASCADE: this supports ad-hoc sessions logged with no planned
routine, and it means deleting or editing an old routine can never cascade
into deleting historical session data -- that data is exactly what feeds
the progress charts (CLAUDE.md section 1), so it must outlive the routine
that originally produced it.

Open question, not solved here: this table has no direct student_id.
For a session tied to a routine, the student is derivable via
routine_id -> routine.student_id. But an ad-hoc session with no routine
currently has no link to any student at all. Revisit once ad-hoc sessions
are actually used -- possibly by adding an optional direct student_id.
"""

import uuid
from datetime import date as date_

from sqlalchemy import Date, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    routine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routine.id", ondelete="SET NULL"),
        nullable=True,
    )
    date: Mapped[date_] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    # Minutes.
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)

    routine: Mapped["Routine | None"] = relationship(
        "Routine", back_populates="sessions"
    )
    session_sets: Mapped[list["SessionSet"]] = relationship(
        "SessionSet", back_populates="session"
    )
