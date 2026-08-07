#!/usr/bin/env bash
set -euo pipefail

# Manual backup for the CockroachDB dev cluster, using CockroachDB's
# native BACKUP statement. Confirmed manually (2026-08-06) that BACKUP
# runs without any license error on this v23.1.21 single-node --insecure
# cluster -- Cockroach Labs' CCL license gate on BACKUP/RESTORE doesn't
# trigger here, so no enterprise license or workaround is needed.
#
# What this protects against: losing the HOST MACHINE -- which already
# happened once (this project moved from bare metal to a Hyper-V VM after
# that). It is NOT a production-grade HA strategy: this is a single-node
# cluster, so there's no replication and no point-in-time recovery beyond
# "a copy of the data exists somewhere else". Good enough for a solo dev
# project, not a template for a real multi-node deployment.
#
# Where backups land: `nodelocal://1/backups/<timestamp>` resolves to
# <cockroach-data-dir>/extern/backups/<timestamp> *inside* the
# `cockroachdb` container. docker-compose.yml bind-mounts that
# `extern/backups` directory to /data/calisteniapp-backups on the HOST --
# deliberately on the second disk (140GB, mounted at /data), separate
# from both the OS disk (100GB, sda) and the `cockroach-data` named
# volume that holds the live DB files. So an OS-disk failure doesn't take
# the backups down with it, and this path is outside the git repo
# entirely (never committed).
#
# Run as root (the admin identity -- see CLAUDE.md section 6): app_user
# is deliberately least-privilege (SELECT/INSERT/UPDATE/DELETE only) and
# lacks the privileges BACKUP needs. `cockroach sql --insecure` with no
# --user flag defaults to root under --insecure mode, same as db-init in
# docker-compose.yml.

DB_NAME="crdb_calisteniaapp_db"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_URI="nodelocal://1/backups/${TIMESTAMP}"

echo "Backing up ${DB_NAME} to ${BACKUP_URI} ..."

docker compose exec -T cockroachdb cockroach sql --insecure -e \
  "BACKUP DATABASE ${DB_NAME} INTO '${BACKUP_URI}';"

echo "Backup complete."
echo "  Container path: /cockroach/cockroach-data/extern/backups/${TIMESTAMP}"
echo "  Host path:      /data/calisteniapp-backups/${TIMESTAMP}"

# --- Restoring from a backup -------------------------------------------
#
# Each run of this script creates its own backup collection at
# nodelocal://1/backups/<timestamp> (one BACKUP per collection), so
# restoring means pointing RESTORE at the specific timestamp you want.
#
# 1. Find the timestamp of the backup you want -- list them directly on
#    the host, since /data/calisteniapp-backups is the bind-mounted view
#    of the same directory:
#      ls /data/calisteniapp-backups/
#
# 2. (Optional) Inspect what's inside a given backup before restoring:
#      docker compose exec cockroachdb cockroach sql --insecure -e \
#        "SHOW BACKUPS IN 'nodelocal://1/backups/<timestamp>';"
#
# 3. Restore it. The target database must NOT already exist under this
#    name -- if you're testing a restore against a live dev cluster,
#    DROP or rename the existing database first:
#      docker compose exec cockroachdb cockroach sql --insecure -e \
#        "RESTORE DATABASE crdb_calisteniaapp_db FROM LATEST IN 'nodelocal://1/backups/<timestamp>';"
#
#    ("FROM LATEST IN" picks the most recent backup within that one
#    collection -- since each script run makes a fresh collection with a
#    single backup in it, this just means "the backup taken at
#    <timestamp>".)
