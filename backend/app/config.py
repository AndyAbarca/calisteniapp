"""
Configuration module.

Why environment variables instead of hardcoded values or a config file
checked into git: connection details (host, credentials) differ between
environments (local Docker Compose, a future staging/prod deployment) and
must never be committed to version control. python-dotenv lets us keep an
untracked `.env` file for local development (see `.env.example` for the
expected keys) while falling back to real environment variables in any
other context, such as the values injected by docker-compose.yml for the
"backend" service.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    cockroach_host: str = os.getenv("COCKROACH_HOST", "localhost")
    cockroach_port: str = os.getenv("COCKROACH_PORT", "26257")
    # Runtime identity for the FastAPI app itself (main.py, database.py,
    # and any future routes/) -- deliberately least-privilege: `app_user`
    # only has SELECT/INSERT/UPDATE/DELETE, no DDL (see the `app_user`
    # GRANT in docker-compose.yml's db-init service). The app should never
    # be able to create/alter/drop tables through its normal request path.
    cockroach_user: str = os.getenv("COCKROACH_USER", "app_user")
    cockroach_password: str = os.getenv("COCKROACH_PASSWORD", "")
    cockroach_database: str = os.getenv("COCKROACH_DATABASE", "crdb_calisteniaapp_db")

    # Separate admin identity, used ONLY by Alembic (alembic/env.py) and
    # one-off scripts that need DDL/full-table privileges app_user doesn't
    # have (e.g. backend/scripts/seed_exercises.py) -- never by the app's
    # own runtime code. Kept as its own credential pair, rather than just
    # reusing cockroach_user/_password, so the app's normal connection can
    # never accidentally end up with admin rights just because something
    # read the wrong env var.
    #
    # Note on what this split actually buys you: the local cluster runs
    # with `--insecure` (see docker-compose.yml), which doesn't just skip
    # checking passwords -- it refuses to let a user have one at all
    # ("setting or updating a password is not supported in insecure mode").
    # Both cockroach_password and cockroach_admin_password are therefore
    # always empty locally; any client that can reach the cluster can
    # connect as any existing user regardless. So this split is
    # privilege-based isolation (app_user structurally lacks DDL rights
    # and can't touch other databases), not authentication-based security.
    # Real authentication would require enabling TLS certs, which is out
    # of scope for local LAN development (see CLAUDE.md section 2,
    # "Hosting").
    cockroach_admin_user: str = os.getenv("COCKROACH_ADMIN_USER", "root")
    cockroach_admin_password: str = os.getenv("COCKROACH_ADMIN_PASSWORD", "")

    def _build_url(self, user: str, password: str) -> str:
        # CockroachDB speaks the PostgreSQL wire protocol, so a plain
        # "postgresql" SQLAlchemy URL *connects* fine with psycopg2 -- but
        # SQLAlchemy 2.x's postgresql dialect parses the server version
        # string to decide which SQL features to use, and it can't parse
        # CockroachDB's version banner ("CockroachDB CCL v23.1.21 ..."),
        # raising AssertionError on first connection. The "cockroachdb"
        # dialect scheme below comes from Cockroach Labs' own
        # sqlalchemy-cockroachdb package, which overrides just that
        # version-parsing logic and otherwise defers to the standard
        # psycopg2 driver -- so this is the officially recommended fix,
        # not a workaround. sslmode=disable matches the --insecure
        # single-node setup used for local development (see
        # docker-compose.yml); a real deployment would use TLS
        # certificates instead and drop this.
        auth = user
        if password:
            auth += f":{password}"
        return (
            f"cockroachdb://{auth}@{self.cockroach_host}:{self.cockroach_port}"
            f"/{self.cockroach_database}?sslmode=disable"
        )

    @property
    def database_url(self) -> str:
        # The app's own runtime connection -- app_user, least-privilege.
        return self._build_url(self.cockroach_user, self.cockroach_password)

    @property
    def admin_database_url(self) -> str:
        # For Alembic and one-off DDL/bulk-load scripts only -- see the
        # cockroach_admin_user/_password comment above.
        return self._build_url(self.cockroach_admin_user, self.cockroach_admin_password)


settings = Settings()
