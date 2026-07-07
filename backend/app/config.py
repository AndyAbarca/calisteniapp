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
    cockroach_database: str = os.getenv("COCKROACH_DATABASE", "calisteniapp")

    @property
    def database_url(self) -> str:
        # CockroachDB speaks the PostgreSQL wire protocol, so a standard
        # "postgresql" SQLAlchemy URL works with the psycopg2 driver.
        # sslmode=disable matches the --insecure single-node setup used for
        # local development (see docker-compose.yml); a real deployment
        # would use TLS certificates instead and drop this.
        auth = self.cockroach_user
        if self.cockroach_password:
            auth += f":{self.cockroach_password}"
        return (
            f"postgresql://{auth}@{self.cockroach_host}:{self.cockroach_port}"
            f"/{self.cockroach_database}?sslmode=disable"
        )


settings = Settings()
