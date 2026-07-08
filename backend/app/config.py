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
    cockroach_user: str = os.getenv("COCKROACH_USER", "root")
    cockroach_password: str = os.getenv("COCKROACH_PASSWORD", "")
    cockroach_database: str = os.getenv("COCKROACH_DATABASE", "crdb_calisteniaapp_db")

    @property
    def database_url(self) -> str:
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
        auth = self.cockroach_user
        if self.cockroach_password:
            auth += f":{self.cockroach_password}"
        return (
            f"cockroachdb://{auth}@{self.cockroach_host}:{self.cockroach_port}"
            f"/{self.cockroach_database}?sslmode=disable"
        )


settings = Settings()
