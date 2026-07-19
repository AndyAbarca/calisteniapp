"""
Import every model module here so they register on Base.metadata as a
side effect of importing this package -- Alembic's env.py imports
app.database.Base and diffs against Base.metadata, so a model that never
gets imported anywhere is invisible to autogenerate even though the class
exists on disk.
"""

from app.models.student import Student
from app.models.exercise import Exercise
from app.models.routine import Routine
from app.models.routine_exercise import RoutineExercise
from app.models.session import Session
from app.models.session_set import SessionSet

__all__ = [
    "Student",
    "Exercise",
    "Routine",
    "RoutineExercise",
    "Session",
    "SessionSet",
]
