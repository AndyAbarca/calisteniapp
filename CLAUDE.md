# calisteniapp — Project context for Claude Code

## 1. Description

Progress-tracking app for calisthenics training. Allows creating training routines
(manual or auto-generated), logging repeated training sessions over time, and
visualizing performance evolution per exercise (reps, added weight/load, time under
tension, etc.) through charts and dashboards.

Supports multiple "students" (alumnos) from the initial design, even though short-term
usage is expected to be single-user (the developer himself). This decoupling is
intentional: modeling multi-user support from the start avoids a painful schema
migration later if the project grows (e.g., for use with real students of a
calisthenics coach).

## 2. Tech stack and rationale

| Component      | Choice                     | Reason |
|----------------|----------------------------|--------|
| Backend        | Python + FastAPI           | Typing via Pydantic, automatic OpenAPI/Swagger generation, good fit for a dev with a DBA background learning backend development |
| Database       | CockroachDB (via Docker)   | The user already administers it professionally (2 years as DBA); reduces the learning curve on the data layer so effort can focus on DevOps/infra |
| Frontend       | React (Vite) + Recharts    | Simple SPA, Recharts covers progress charts well without needing a heavier visualization library |
| Orchestration  | Docker Compose             | The whole stack (backend, DB, frontend) spins up with a single command, reproducible across machines |
| Hosting        | Local network (LAN)        | No need to expose to the internet; accessible from phone/laptop within the same home network |

## 3. Development environment

- Editor: VS Code on Windows 11, connected via **Remote-SSH** to a Linux Mint machine
  (which provides the real infrastructure: Docker, CockroachDB, etc.)
- The code and containers live **entirely on the Linux Mint machine**, not on Windows.
  VS Code's integrated terminal, being in Remote-SSH mode, executes commands on Mint.
- Project path on the Mint filesystem: `/home/andy_dell/DevOps/calisteniapp`
- Version control: Git + GitHub
  - Remote repo: https://github.com/AndyAbarca/calisteniapp (public)

## 4. Domain model (DRAFT — subject to revision)

> **IMPORTANT:** this model is a working draft. The user has an ebook with calisthenics
> exercise tables (categories, progressions, difficulty levels) that hasn't been
> incorporated into this document yet. **Do not build complex business logic on top
> of the `exercise` entity until this section is confirmed or updated.**
> It is safe to proceed with: infrastructure setup, authentication, base FastAPI
> structure, CockroachDB connection — anything that doesn't depend on the fine-grained
> detail of what fields an exercise has.

### Entities

- **student** (alumno)
  `id, name, date_of_birth, notes`
  Represents the person training. Multi-user from day 1 (see section 1).

- **exercise** (ejercicio) [PENDING REVIEW WITH EBOOK MATERIAL]
  `id, name, category, metric_unit`
  `metric_unit` indicates how performance is measured for that exercise: repetitions,
  time (seconds), or repetitions + added weight.
  Candidates to add once the ebook is reviewed: `difficulty_level`,
  `progresses_from` (reference to another exercise, to model progression chains,
  e.g. "knee push-ups → standard push-ups → one-arm push-ups").

- **routine** (rutina)
  `id, student_id, name, description, created_by` (values: `manual` | `auto`)

- **routine_exercise** (rutina_ejercicio) — bridge table routine↔exercise, with
  relationship metadata
  `routine_id, exercise_id, order, target_sets, target_reps`

- **session** (sesion)
  `id, routine_id, student_id, date, notes, duration`
  A concrete execution of a routine, on a given date.

- **session_set** (sesion_set)
  `id, session_id, exercise_id, set_number, actual_reps, added_weight_kg, rpe,
  time_seconds`
  The most granular level of detail: a single set within a session.
  This is the table that feeds the progress charts (e.g., "added-weight progression
  on pull-ups over time" is a query grouped by `exercise_id`, ordered by the date of
  the associated `session`).

## 5. Roadmap (phases)

1. **MVP** — CRUD for routines/exercises/sessions via REST API. No agents yet.
   Goal: have something functional to log sessions manually.
2. **Dashboard** — Progress charts per exercise (Recharts), filterable by student
   and date range.
3. **Automatic routine generation** — Simple progression rules based on history
   (e.g., "if the same weight/reps has held for N weeks, suggest an increase").
   Possible future incorporation of an LLM for smarter suggestions, not confirmed yet.
4. **Agents** (in this order):
   - **Dev Agent**: Claude Code assisting with development, tests, refactors.
   - **Infra Agent**: automated health checks on containers/DB, backups.
   - **PM/Roadmap Agent**: reads/writes to GitHub (Issues, Projects, Milestones)
     via the GitHub MCP server.

## 6. Working conventions

- **Commits**: descriptive messages, in English (see language convention below).
  Small, atomic commits — avoid mixing infra changes with business logic changes
  in the same commit.
- **Tests**: to be introduced from the MVP phase, not as an afterthought. Use
  `pytest` for the backend.
- **Language convention**: all project documentation, code comments, data models,
  and files such as this one are written in **English**, regardless of the language
  used in conversation with the user (the user converses in Spanish but wants all
  project artifacts in English).
- **Inline documentation**: since this project also serves as a DevOps learning
  vehicle for the user (ex-Oracle/CockroachDB DBA transitioning into DevOps),
  prioritize comments that explain the *why* behind technical decisions, not just
  the *what* the code does. Don't assume prior knowledge of Docker, CI/CD, or
  backend architecture patterns.
- **Learning context**: the user prefers to understand the reasoning behind each
  decision before accepting it. When ambiguity arises on an architecturally
  relevant decision (library choice, design pattern, etc.), briefly explain the
  trade-off instead of silently applying a default.

## 7. Current environment state (as of this document's creation)

- Git 2.43.0 installed and configured (`user.name`, `user.email`) on the Mint machine.
- Claude Code 2.1.201 installed and authenticated with a Claude Pro account.
- Local Git repository initialized at `/home/andy_dell/DevOps/calisteniapp`
  (default branch: `main`).
- Remote GitHub repository: created and connected.
  `origin` -> `git@github.com:AndyAbarca/calisteniapp.git` (public), branch `main`
  tracked via `git push -u origin main`.
- Infra scaffold created, verified, and committed: FastAPI backend
  (`backend/app/main.py` with `GET /health`), SQLAlchemy + CockroachDB connection
  setup (env-based, no hardcoded credentials), minimal Vite+React frontend, and
  `docker-compose.yml` wiring `cockroachdb` + `backend` + `frontend`, all bound to
  `0.0.0.0` for LAN access. Verified via `docker compose up --build`. The `models/`,
  `schemas/`, and `routes/` packages exist but are intentionally empty, pending the
  domain model (see section 4).

## 8. Explicit pending items (nothing left implicitly "done")

- [x] Decide public vs. private for the GitHub repo. -> Public
- [x] Create the remote repo and connect it (`git remote add origin ...`).
- [x] Scaffold the infra (backend/frontend/docker-compose) and commit it.
- [ ] Review and update the `exercise` model with the ebook material.
- [ ] Define the final folder structure for the scaffold (backend/frontend/infra).
- [ ] Decide user authentication strategy (even if single-user initially).
- [ ] Set up the GitHub MCP server once the PM Agent phase is reached.
