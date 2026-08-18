#!/usr/bin/env bash
# Daily neobank wiki scout. Wire into cron/launchd — see jobs/README.md
set -euo pipefail
cd "$(dirname "$0")/.."
echo "=== neobank scout $(date '+%Y-%m-%d %H:%M') ==="
claude -p "/neobank-scout"
