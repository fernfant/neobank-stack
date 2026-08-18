# Scheduled jobs

Two jobs keep the wiki current. Both are just prompts that invoke a skill — the intelligence
lives in `.claude/skills/`, not here.

| Job | Schedule | Skill | What it does |
| --- | --- | --- | --- |
| `neobank-daily-scout` | Daily, 07:12 local | `neobank-scout` | Sweeps the watchlist, answers open questions, ingests material finds, generates new questions |
| `neobank-weekly-lint` | Mondays, 07:38 local | `neobank-lint` | Contradictions, stale claims, orphans, gaps |

Times are deliberately off the hour. Everyone schedules `0 9 * * *`; landing on `12 7 * * *`
avoids the crowd.

## Three ways to run them

### 1. Claude Code scheduled tasks (registered)

Registered via the scheduled-tasks integration. They run while the app is open; if it is closed
when one is due, it runs on next launch.

```bash
claude -p "list my scheduled tasks"
```

### 2. Manually, any time

```bash
claude -p "/neobank-scout"
```

```bash
claude -p "/neobank-lint"
```

### 3. System cron / launchd (headless, survives the app being closed)

Scripts in `scripts/` are the headless entrypoints. To install:

```bash
crontab -e
```

Then add (adjust the path):

```
12 7 * * * /Users/fernando/neobank-stack/scripts/daily-scout.sh >> /tmp/neobank-scout.log 2>&1
38 7 * * 1 /Users/fernando/neobank-stack/scripts/weekly-lint.sh >> /tmp/neobank-lint.log 2>&1
```

On macOS, `launchd` is the better-behaved option for anything that must survive sleep — see
`man launchd.plist`. Note that `claude -p` needs a logged-in session and network access.

## Design notes

**Why daily and not hourly.** This domain moves in weeks, not hours. A daily pass with a real
time budget produces better work than twelve shallow ones. The scout is explicitly told that a
quiet day reported honestly is a good outcome.

**Why the scout generates questions.** Ingesting news alone makes the wiki a feed. The
compounding comes from the question backlog: each pass answers some and raises more, so the

**Why lint is separate and weekly.** Different job. The scout adds; the lint makes what is
already there trustworthy. Running it daily would generate noise, since most weeks only a
handful of pages change.

**Why diagrams are not regenerated daily.** A reference diagram that changes every day is not a
reference. The scout only triggers `neobank-architect` when a layer actually moved.
