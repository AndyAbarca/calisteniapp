"""
Application entry point.

Why so little lives here: this file's job is just to assemble routers and
prove the app boots and responds, via GET /health (which also doubles as a
Docker Compose health check target once one is added). The actual route
logic lives under app/routes/, one module per entity, wired in below with
app.include_router(...).

Current state: `exercise` is the only entity with endpoints so far --
schema-done and seeded with real data (see CLAUDE.md section 4) -- and
those endpoints are read-only (GET only). student/routine/session/
session_set don't have endpoints yet, and no entity has write endpoints
(POST/PUT/PATCH/DELETE) yet, since those need an auth strategy that hasn't
been decided (see CLAUDE.md's pending items).
"""

from fastapi import FastAPI

from app.routes import exercises

app = FastAPI(title="calisteniapp")

app.include_router(exercises.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
