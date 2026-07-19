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

## 4. Domain model (IMPLEMENTED — schema migrated, `exercise` seeded with real data)

> **IMPORTANT:** the schema below is implemented in `backend/app/models/` and applied
> to CockroachDB via Alembic migrations (see section 7). The `exercise` table is now
> seeded with 222 real rows derived from the user's ebook, Steven Low's "Overcoming
> Gravity" 2nd Edition (chapters 24-27), via `backend/scripts/seed_exercises.py`. The
> one deliberately unfinished piece is `progresses_from_id` (see the exercise entity
> below) — left NULL on all 222 rows on purpose, not a gap to fill automatically.

### Entities

- **student** (alumno) — `backend/app/models/student.py`
  `id (UUID, PK), name, date_of_birth, notes`
  Represents the person training. Multi-user from day 1 (see section 1).

- **exercise** (ejercicio) — `backend/app/models/exercise.py` [SCHEMA DONE, SEEDED WITH 222 REAL ROWS]
  `id (UUID, PK), name (unique), movement_pattern, progression_line, level,
  level_variant, equipment, progresses_from_id, book_page`
  `movement_pattern` is a free-text field for now (e.g. Push/Pull/Legs/Core/Static, no
  DB-level enum yet). `progression_line` + `level` together locate an exercise within a
  named progression chain (e.g. "Pull-ups", "Front Lever"). `level` is nullable, since
  the book itself marks some entries "N/A" (no single level applies). `level_variant`
  (nullable, single char) exists because the book's own index genuinely assigns the
  same level to two different exercises within one progression_line, twice (Planche
  level 16; Muscle-ups and Inverted Muscle-ups level 8) — a real authorial collision,
  not a derivation error to fudge away, so the unique constraint is
  `(progression_line, level, level_variant)` rather than just the pair. `progresses_from_id`
  self-references `exercise.id` to point at the prior step in that chain (nullable —
  the first step of a line has no predecessor), e.g. "knee push-ups → standard
  push-ups → one-arm push-ups" — **NULL on all 222 rows for now, deliberately**: the
  user is reading the book himself to work out the real progression chains, and this
  is explicitly not to be inferred or automated by Claude Code. `book_page` links back
  to the ebook page an exercise was sourced from, to ease cross-checking that data.

- **routine** (rutina) — `backend/app/models/routine.py`
  `id (UUID, PK), student_id, name, description, generation_method` (values: `manual` |
  `auto`)
  Named `generation_method` rather than the originally drafted `created_by`, to avoid
  colliding with a future auth `created_by_user_id` field — see section 6.

- **routine_exercise** (rutina_ejercicio) — `backend/app/models/routine_exercise.py` —
  bridge table routine↔exercise, with relationship metadata
  `routine_id, exercise_id, order, target_sets, target_reps`
  Composite primary key `(routine_id, exercise_id)`, no separate `id` column — an
  exercise appears at most once per routine, so the natural key already uniquely
  identifies a row.

- **session** (sesion) — `backend/app/models/session.py`
  `id (UUID, PK), routine_id, date, notes, duration`
  A concrete execution of a routine, on a given date. `routine_id` is **nullable, with
  `ON DELETE SET NULL`** — deliberately, to support ad-hoc sessions logged with no
  planned routine, and so deleting an old routine never cascades into deleting the
  historical session data that feeds the progress charts. **Open question, not yet
  solved:** there is no direct `student_id` on this table. For a session tied to a
  routine, the student is derivable via `routine_id -> routine.student_id`, but an
  ad-hoc session with no routine currently has no link to any student at all — revisit
  once ad-hoc sessions are actually used.

- **session_set** (sesion_set) — `backend/app/models/session_set.py`
  `id (UUID, PK), session_id, exercise_id, set_number, set_order, actual_reps,
  added_weight_kg, rpe, time_seconds`
  The most granular level of detail: a single set within a session. This is the table
  that feeds the progress charts (e.g., "added-weight progression on pull-ups over
  time" is a query grouped by `exercise_id`, ordered by the date of the associated
  `session`). Two distinct position columns: `set_number` is the position within *that
  exercise* in the session (e.g. "3rd set of pull-ups today"); `set_order` is the
  position within the *session as a whole*, across every exercise, which is what makes
  it possible to reconstruct the actual chronological order of a circuit/superset
  workout (`set_number` alone can't — two sets can share a `set_number` but happen at
  different times). Unique constraints on both `(session_id, exercise_id, set_number)`
  and `(session_id, set_order)`.

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
- **UUID primary keys, not serial/int**: every domain table (section 4) uses a
  UUID primary key instead of an auto-incrementing integer. Sequential integer PKs
  cause write hotspotting in CockroachDB, since consecutive inserts land on the same
  key range and therefore the same range leaseholder/node — UUIDs spread writes
  across the keyspace instead.
- **UUID PKs need a `server_default`, not just an ORM-side default**: not every
  insert goes through the SQLAlchemy ORM — e.g. bulk-loading the ebook's exercise
  data is expected to happen via raw SQL — so PK generation has to work at the
  database level too, not just in Python. Every UUID PK column therefore has
  `server_default=text("gen_random_uuid()")` in addition to the ORM-side
  `default=uuid.uuid4`.
- **DB access is split into two identities, not one shared `root`**: `app_user`
  is least-privilege (`SELECT`/`INSERT`/`UPDATE`/`DELETE` only, no DDL) and is
  what the backend's runtime connection actually uses (`database_url` in
  `app/config.py`); `root` is used only by Alembic (`alembic/env.py`) and
  one-off scripts that need DDL (`admin_database_url`), e.g.
  `seed_exercises.py`. Neither user has a password — CockroachDB's `--insecure`
  mode doesn't just skip checking passwords, it refuses to let a user have one
  at all. So this split buys **privilege isolation**, not authentication:
  `app_user` structurally can't run DDL or touch other databases, but anything
  that can reach the cluster can still connect as either user. Real
  authentication would require enabling TLS certs, out of scope for local LAN
  dev (see section 2, "Hosting").
- **Two CockroachDB gotchas hit while building the split above, worth
  remembering**:
  - `CREATE USER ... WITH PASSWORD` fails outright under `--insecure` — not a
    silent no-op, an actual error.
  - Every user is implicitly a member of the built-in `public` role, which
    grants `CREATE` on a database's public schema by default. Without an
    explicit `REVOKE CREATE ON SCHEMA public FROM public`, a "least-privilege"
    user can still create tables regardless of what it was or wasn't
    explicitly granted.

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
- Alembic has 3 migrations applied against CockroachDB: the domain model baseline
  (`7ebeb2df8200`, creates the 6 tables from section 4), a follow-up fix adding
  server-side UUID defaults (`b9f6688550b9`), and `df3166695497` (adds
  `exercise.level_variant`, makes `exercise.level` nullable, and widens the unique
  constraint to `(progression_line, level, level_variant)`). `alembic/env.py` now has
  `compare_server_default=True` enabled so autogenerate reliably detects
  `server_default` changes going forward — this wasn't the case initially, which
  caused a silently empty migration the first time a `server_default` was added.
- `backend/scripts/seed_exercises.py` loaded 222 real `exercise` rows, derived from
  the "Overcoming Gravity" ebook index, into `crdb_calisteniaapp_db` via raw SQL
  (not the ORM) — see section 4.
- `db-init` (in `docker-compose.yml`) now also creates the least-privilege
  `app_user` and its grants on every `docker compose up` — `GRANT ... ON ALL
  TABLES`, `ALTER DEFAULT PRIVILEGES FOR ROLE root` (so future tables Alembic
  creates are automatically covered too), and `REVOKE CREATE ON SCHEMA public
  FROM public` (see section 6's gotchas). Verified end-to-end from a genuinely
  fresh volume (`docker compose down -v` → `up` → `alembic upgrade head` →
  `seed_exercises.py`), including confirming `app_user` can `SELECT` but
  cannot `CREATE TABLE`.

## 8. Explicit pending items (nothing left implicitly "done")

- [x] Decide public vs. private for the GitHub repo. -> Public
- [x] Create the remote repo and connect it (`git remote add origin ...`).
- [x] Scaffold the infra (backend/frontend/docker-compose) and commit it.
- [x] Implement the 6 domain models (student, exercise, routine, routine_exercise,
  session, session_set) with their Alembic migrations.
- [x] Review and update the `exercise` model with the ebook material (schema +
  initial data load — 222 rows landed).
- [x] Split DB access into least-privilege `app_user` (runtime) and admin
  `root` (migrations/scripts) — not originally tracked as a pending item, but
  done; see sections 6 and 7 for the reasoning and the CockroachDB gotchas
  hit along the way.
- [ ] Fill in `progresses_from_id` for all 222 exercise rows based on the book's
  actual progression logic. Manual, user-driven — not to be automated by Claude Code.
- [ ] Define the final folder structure for the scaffold (backend/frontend/infra).
- [ ] Decide user authentication strategy (even if single-user initially).
- [ ] Set up the GitHub MCP server once the PM Agent phase is reached.
