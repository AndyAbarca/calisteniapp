"""
Student (alumno) model -- the person training.

Deliberately just a training-profile entity, not a login account. Multi-
user from day 1 (see CLAUDE.md section 1): the app is expected to be
single-user short-term, but modeling "student" separately from any future
"User"/auth concept now avoids a painful migration later if a coach ends
up managing several real students. When auth is introduced, the
relationship should be User (one) -> Student (many), not fields bolted
onto this table.
"""

import uuid
from datetime import date

from sqlalchemy import Date, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "student"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    routines: Mapped[list["Routine"]] = relationship(
        "Routine", back_populates="student"
    )
