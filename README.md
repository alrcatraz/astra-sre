# astra-sre

> Unified SRE coordination layer for multi-node infrastructure — health scanning, diagnostics, auto-repair, and learning.
>
> Part of [Astra AI Agent Infrastructure](https://github.com/alrcatraz/astra-aiagent-infra)
>
> [![License: MIT](https://badgen.net/github/license/alrcatraz/astra-sre)](LICENSE)
> [![GitHub stars](https://badgen.net/github/stars/alrcatraz/astra-sre)](https://github.com/alrcatraz/astra-sre)
> [![GitHub last commit](https://badgen.net/github/last-commit/alrcatraz/astra-sre)](https://github.com/alrcatraz/astra-sre/commits)

## Overview

Astra SRE provides a unified operational layer for a fleet of self-hosted servers and services (8 devices across VPS, NAS, laptops, router). It follows a layered architecture:

1. **Plan** — Daily health scans across all devices
2. **Diagnose** — Symptom-based incident search + 5-way parallel diagnosis
3. **Fix** — Automated repair framework with escalation levels (L1–L3)
4. **Learn** — Two-strike pattern detection → auto-suggest new skills

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   astra-sre                          │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Assets   │  │  Data    │  │  Diagnosis       │  │
│  │  device  │  │  service │  │  triage + diagnose│  │
│  │  inventory│  │  inventory│  │                   │  │
│  └──────────┘  └──────────┘  └────────┬─────────┘  │
│                                       │             │
│  ┌────────────────────────────────────┘             │
│  │                                                   │
│  ▼                                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │       Fix Layer (sub-skills)                  │    │
│  │  fix-e2ee · restart-service · fix-gfw        │    │
│  │  fix-mcp · fix-vps-recovery                  │    │
│  └──────────────────────────────────────────────┘    │
│                          │                           │
│  ┌───────────────────────┘                          │
│  ▼                                                   │
│  ┌──────────────────────────────────────────────┐    │
│  │       Learn Layer (learn.py)                  │    │
│  │  Two-strike pattern → auto-suggest new skill │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- SSH key access to target devices (see `config/devices.yaml`)
- Hermes Agent (recommended for cron scheduling)

## Setup

```bash
git clone https://github.com/alrcatraz/astra-sre.git
cd astra-sre
```

No pip install required — scripts use Python stdlib only.

## Configuration

Configure target devices in `config/devices.yaml`:

```yaml
vps-hk:
  host: 10.20.4.10
  user: root
  port: 2222
```

Copy from `config/devices.yaml.example` and edit.

## Usage

### Daily Health Scan

```bash
python3 scripts/health-scan.py          # Markdown report
python3 scripts/health-scan.py --json   # Machine-readable
```

### Diagnose an Incident

```bash
bash scripts/diagnose.sh                                    # 5-way parallel
bash scripts/diagnose.sh --mode network,gateway --symptom "sync error"
```

### Search Historical Incidents

```bash
python3 scripts/triage.py "E2EE cannot decrypt"
python3 scripts/triage.py --list          # List all recorded incidents
```

### Auto-Suggest New Skills

```bash
python3 scripts/learn.py
python3 scripts/learn.py --cron          # Silent mode (output only when new suggestions)
```

### Fix Framework (sub-skills)

Repair skills are loaded via Hermes Agent:

| Skill | Level | Description |
|:------|:-----:|:------------|
| `astra-sre-fix-e2ee` | L2/L3 | E2EE daily repair & full recovery |
| `astra-sre-restart-service` | L2/L3 | Service restarts (non-critical / critical) |
| `astra-sre-fix-gfw` | L2 | GFW interference diagnosis & degradation |
| `astra-sre-fix-mcp` | L2 | MCP process audit & cleanup |
| `astra-sre-fix-vps-recovery` | L2/L3 | VPS upgrade / rebuild recovery |

### Fix Level Definitions

| Level | Strategy |
|:-----:|:---------|
| **L1** 🔵 | Fully automatic, zero user awareness |
| **L2** 🟡 | Automatic + post-action notification |
| **L3** 🔴 | Requires user approval |
| **L3** 🧑 | Requires manual user operation |

### Lock Mechanism

Repair locks use PID files at `/tmp/astra-sre-lock-<tag>.lock`:

- PID alive → lock valid
- PID dead → stale lock, auto-cleaned
- No hard timeout (repairs may run for hours)

## Data Layer

Scripts use a shared SQLite access layer (`scripts/kb_access.py`) that connects to the same database as [astra-knowledge-base-mcp](https://github.com/alcatrz/astra-knowledge-base-mcp). Set via `$ASTRA_KB_PATH` (default: `~/.astra/knowledge-base.db`).

### Knowledge Base: `sre_incidents`

Stores incident records (root cause analysis, diagnostics, fixes, prevention tips). Currently 15 records covering:

- E2EE stale OTK repair
- VPS upgrade & data recovery
- WAN outage diagnosis (GFW interference)
- Service restart patterns

## Maintenance

| Task | Frequency | Method |
|:-----|:---------:|:-------|
| Full device scan | Daily 08:00 | `health-scan.py` → Home thread |
| Hermes version + learn check | Monthly 1st 09:00 | `astra-sre-refresh.sh` → silent |
| Incident records | After each incident | Manual via `kb_add` |

## References

| File | Description |
|:-----|:------------|
| `references/phase3-design.md` | Fix framework design (locks, probes, escalation) |
| `references/format-convention.md` | Project format conventions |

## Related

- [astra-knowledge-base-mcp](https://github.com/alcatrz/astra-knowledge-base-mcp) — incident knowledge storage
- [astra-aiagent-infra](https://github.com/alcatrz/astra-aiagent-infra) — ecosystem portal

## License

MIT — see [LICENSE](LICENSE).

> CI/CD: coming soon — see [astra-aiagent-infra](https://github.com/alcatrz/astra-aiagent-infra) for ecosystem-wide pipeline plans.

---

<p align="center">
  <a href="https://star-history.com/#alcatrz/astra-sre&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=alcatrz/astra-sre&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=alcatrz/astra-sre&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=alcatrz/astra-sre&type=Date" width="600" />
    </picture>
  </a>
</p>
