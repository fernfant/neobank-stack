#!/usr/bin/env bash
# Weekly neobank wiki health check. Wire into cron/launchd — see jobs/README.md
set -euo pipefail
cd "$(dirname "$0")/.."
echo "=== neobank lint $(date '+%Y-%m-%d %H:%M') ==="
claude -p "/neobank-lint"
