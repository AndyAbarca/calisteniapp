"""
Pydantic schema(s) for the `exercise` entity -- this is the first module in
schemas/, so it's worth spelling out how this package differs from
models/ (see app/models/exercise.py's `Exercise` class):

- models/ describes the DATABASE shape: a SQLAlchemy `Mapped[...]` class
  tied 1:1 to the `exercise` table's columns, constraints, and
  relationships. Its job is talking to CockroachDB.
- schemas/ (this file) describes the API shape: what a client actually
  receives as JSON from a GET /exercises response. It's a plain Pydantic
  model with no SQLAlchemy machinery at all. Its job is validation and
  serialization at the FastAPI boundary.

Why not just return the ORM `Exercise` object directly from a route and
skip this file: FastAPI/Pydantic can't cleanly serialize a `Mapped`-style
ORM instance to JSON on its own -- and even where it technically could,
that would leak ORM-only details (relationships, lazy-loading proxies,
internal SQLAlchemy state) straight into the API contract. Today
`ExerciseRead` below mirrors `Exercise`'s plain columns 1:1 because this is
the first, read-only slice of the API -- but the two are kept as separate
classes on purpose, so that later the API's shape can evolve (rename/omit/
reshape a field for clients) without forcing a DB migration, or vice versa.

`model_config = ConfigDict(from_attributes=True)` is what actually bridges
the two: it tells Pydantic v2 to build this model by reading attributes off
an arbitrary object (like a SQLAlchemy `Exercise` instance), not just off a
dict. Without it, handing an ORM instance to `ExerciseRead` (which is what
FastAPI does under the hood via `response_model=`) would fail. This is the
Pydantic v2 spelling of what used to be `class Config: orm_mode = True` in
Pydantic v1 -- `orm_mode` no longer exists in v2.
"""

import uuid

from pydantic import BaseModel, ConfigDict


class ExerciseRead(BaseModel):
    """
    Shape returned by GET /exercises and GET /exercises/{exercise_id}.

    Field types and nullability mirror app.models.exercise.Exercise's
    plain columns 1:1 -- see the module docstring above for why that's a
    starting point for this first slice, not a permanent guarantee.
    Relationship fields (progresses_from, routine_exercises, session_sets)
    are deliberately omitted: including them would require eager-loading
    joins this first read-only slice doesn't need.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    movement_pattern: str
    progression_line: str
    level: int | None = None
    level_variant: str | None = None
    equipment: str | None = None
    progresses_from_id: uuid.UUID | None = None
    book_page: int | None = None
