"""
Applies manually-curated exercise.progresses_from_id links from
progression_chains.csv.

Workflow (see also the header comment in progression_chains.csv): as you
work through the book, add rows to progression_chains.csv (exercise_name,
progresses_from_name), committing the CSV incrementally in small batches --
many separate commits over time, not one big edit. Whenever you want to
push a new batch of decisions into the database, run this script:

    python backend/scripts/apply_progression_chains.py            # dry run
    python backend/scripts/apply_progression_chains.py --apply    # for real

This script deliberately does NOT infer or guess any progression
relationship itself -- it only applies the pairs you've already decided on
and written into the CSV.

Connects as settings.cockroach_user (app_user), not the admin identity --
unlike seed_exercises.py's bulk INSERT (which needs root), this is a plain
UPDATE against an existing table, and app_user already has UPDATE
privileges for it (see CLAUDE.md section 6's app_user/root split). Uses
the same psycopg2-with-individual-params connection style as
seed_exercises.py, rather than settings.database_url directly, since that
URL uses the "cockroachdb://" SQLAlchemy dialect scheme that psycopg2
itself doesn't understand.
"""

import argparse
import csv
import sys
from pathlib import Path

# Allow running as `python backend/scripts/apply_progression_chains.py`
# from the repo root without installing the app package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg2

from app.config import settings

CSV_PATH = Path(__file__).resolve().parent / "progression_chains.csv"

SELECT_NAMES_SQL = "SELECT id, name FROM exercise WHERE name = ANY(%s)"

UPDATE_SQL = "UPDATE exercise SET progresses_from_id = %s WHERE id = %s"

RECHECK_NULLS_SQL = """
    SELECT name FROM exercise
    WHERE name = ANY(%s) AND progresses_from_id IS NULL
"""


def load_rows() -> list[dict]:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def connect():
    return psycopg2.connect(
        host=settings.cockroach_host,
        port=settings.cockroach_port,
        user=settings.cockroach_user,
        password=settings.cockroach_password,
        dbname=settings.cockroach_database,
        sslmode="disable",
    )


def validate(rows: list[dict], name_to_id: dict[str, str]) -> list[str]:
    errors = []
    for i, row in enumerate(rows, start=2):  # start=2: header is line 1
        exercise_name = row["exercise_name"].strip()
        progresses_from_name = row["progresses_from_name"].strip()

        if exercise_name == progresses_from_name:
            errors.append(
                f"Line {i}: self-reference -- exercise_name and "
                f"progresses_from_name are both {exercise_name!r}"
            )
        if exercise_name not in name_to_id:
            errors.append(
                f"Line {i}: exercise_name {exercise_name!r} not found in "
                f"exercise.name"
            )
        if progresses_from_name not in name_to_id:
            errors.append(
                f"Line {i}: progresses_from_name {progresses_from_name!r} "
                f"not found in exercise.name"
            )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually run the UPDATEs. Without this flag, only prints "
        "what would be done.",
    )
    args = parser.parse_args()

    rows = load_rows()
    if not rows:
        print("progression_chains.csv has no data rows yet -- nothing to do.")
        return

    all_names = sorted(
        {row["exercise_name"].strip() for row in rows}
        | {row["progresses_from_name"].strip() for row in rows}
    )

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(SELECT_NAMES_SQL, (all_names,))
            name_to_id = {name: str(id_) for id_, name in cur.fetchall()}

        errors = validate(rows, name_to_id)
        if errors:
            print(f"Found {len(errors)} error(s) in progression_chains.csv -- "
                  f"no changes applied:\n")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)

        print(f"Validated {len(rows)} row(s) from progression_chains.csv, "
              f"all names matched.\n")

        if not args.apply:
            print("DRY RUN -- no changes made. Would run:\n")
            for row in rows:
                exercise_name = row["exercise_name"].strip()
                progresses_from_name = row["progresses_from_name"].strip()
                print(f"  {exercise_name!r} -> progresses_from {progresses_from_name!r}")
            print(f"\n{len(rows)} row(s) would be updated. "
                  f"Re-run with --apply to actually update the database.")
            return

        updated_names = [row["exercise_name"].strip() for row in rows]
        with conn:
            with conn.cursor() as cur:
                for row in rows:
                    exercise_name = row["exercise_name"].strip()
                    progresses_from_name = row["progresses_from_name"].strip()
                    cur.execute(
                        UPDATE_SQL,
                        (name_to_id[progresses_from_name], name_to_id[exercise_name]),
                    )
        print(f"Applied {len(rows)} update(s) to exercise.progresses_from_id.")

        with conn.cursor() as cur:
            cur.execute(RECHECK_NULLS_SQL, (updated_names,))
            still_null = [name for (name,) in cur.fetchall()]
        if still_null:
            print(f"\nWARNING: {len(still_null)} row(s) still have a NULL "
                  f"progresses_from_id after the update:")
            for name in still_null:
                print(f"  - {name}")
        else:
            print("Confirmed: no NULLs remain among the updated rows.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
