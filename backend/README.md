# Backend

FastAPI + SQLAlchemy service, backed by CockroachDB. See `/CLAUDE.md` at the
repo root for the full project context and domain model.

## Running Alembic migrations

Alembic runs **inside the `backend` container**, not on the host — that way
it always uses the same Python/dependency versions the app itself runs
with, and the same `COCKROACH_*` environment variables docker-compose
injects into that container (see `docker-compose.yml`).

```bash
# Bring the stack up first (cockroachdb -> db-init -> backend)
docker compose up -d

# Apply all migrations (currently an empty baseline, zero migrations)
docker compose exec backend alembic upgrade head

# Once real models exist under app/models/, generate a migration from them
docker compose exec backend alembic revision --autogenerate -m "add student, routine, session tables"

# Check current migration state
docker compose exec backend alembic current
```

There is no supported host-side workflow (running `alembic` directly on
the Mint machine) unless you separately install the backend's
`requirements.txt` into a local virtualenv — not necessary for normal
development.
