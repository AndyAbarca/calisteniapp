"""
Read-only REST endpoints for the `exercise` entity.

This is the layer where app.models.Exercise (the DB shape, queried via
SQLAlchemy) and app.schemas.ExerciseRead (the API shape, returned as JSON)
meet: each endpoint below queries the DB using the ORM model, then declares
response_model=ExerciseRead so FastAPI converts the resulting ORM
instance(s) into the API schema (via the from_attributes config on
ExerciseRead) before serializing the response. See app/schemas/exercise.py
for why those two shapes are kept separate instead of returning the ORM
object straight to the client.

Deliberately read-only for now: write endpoints (POST/PUT/PATCH/DELETE)
need an auth strategy that doesn't exist yet (see CLAUDE.md's pending
items), so this first slice only covers GET /exercises and
GET /exercises/{exercise_id}.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseRead

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    progression_line: str | None = None,
    movement_pattern: str | None = None,
    db: Session = Depends(get_db),
):
    """
    List exercises, optionally filtered by progression_line and/or
    movement_pattern. Both filters are optional and independent: no query
    params returns every row, and supplying both ANDs them together
    (chained .where() calls already AND, no explicit and_() needed).
    """
    stmt = select(Exercise)
    if progression_line is not None:
        stmt = stmt.where(Exercise.progression_line == progression_line)
    if movement_pattern is not None:
        stmt = stmt.where(Exercise.movement_pattern == movement_pattern)

    return db.execute(stmt).scalars().all()


@router.get("/{exercise_id}", response_model=ExerciseRead)
def get_exercise(exercise_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Fetch a single exercise by id, or 404 if it doesn't exist.

    exercise_id is typed as uuid.UUID (not str) so FastAPI validates the
    path segment is a well-formed UUID and returns a 422 automatically for
    malformed input, before this function body ever runs.
    """
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
