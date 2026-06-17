# astra-sre — Agent Guide

For AI agents consuming this component. Humans can skip to [README](README.md).

## Entry Points

| Action | Command |
|:-------|:--------|
| Run health scan | `python3 scripts/health-scan.py` |
| Run health scan (JSON) | `python3 scripts/health-scan.py --json` |
| Search SRE incidents | `python3 scripts/triage.py "<symptom>"` |
| List all incidents | `python3 scripts/triage.py --list` |
| Learn from patterns | `python3 scripts/learn.py` |

## Dependencies

- Python 3.11+
- SSH key access to target devices (as configured in `config/devices.yaml.example`)
- Data layer: SQLite via `scripts/kb_access.py` (reads `$ASTRA_KB_PATH`, default `~/.astra/knowledge-base.db`)

## Agent Workflows

### Use Case: Daily Health Scan

```
astra-sre/scripts/health-scan.py
  → reads config/devices.yaml.example
  → SSH into each device
  → checks load, disk, memory, uptime
  → prints markdown summary
```

### Use Case: Investigate an Incident

```
1. scripts/triage.py "<symptom>"      # Search past incidents in KB
2. scripts/health-scan.py --json      # Collect current system state
3. scripts/learn.py                    # Learn from patterns
```

### Use Case: Cron Job Integration

See [Maintenance](README.md#maintenance) section in README. Schedule via Hermes `cronjob()` with `workdir` set to the repo path.
