"""
Application entry point.

Why so little lives here: the domain model (student/exercise/routine/
session — see CLAUDE.md section 4) is still a draft pending review against
the exercise-table material, so no business routes exist yet. This file's
only job right now is to prove the FastAPI app boots and responds, via
GET /health, which also doubles as a Docker Compose health check target
once one is added. Domain routes will live under app/routes/ and get wired
in here with app.include_router(...) once the model is confirmed.
"""

from fastapi import FastAPI

app = FastAPI(title="calisteniapp")


@app.get("/health")
def health_check():
    return {"status": "ok"}
