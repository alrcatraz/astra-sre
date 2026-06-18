# astra-sre

<div align="center">

> Unified SRE coordination layer for multi-node infrastructure — health scanning, diagnostics, auto-repair, and learning.
>
> Part of [Astra AI Agent Infrastructure](https://github.com/alrcatraz/astra-aiagent-infra)
>
> [![License: MIT](https://badgen.net/github/license/alrcatraz/astra-sre)](LICENSE)
> [![GitHub stars](https://badgen.net/github/stars/alrcatraz/astra-sre)](https://github.com/alrcatraz/astra-sre)
> [![GitHub last commit](https://badgen.net/github/last-commit/alrcatraz/astra-sre)](https://github.com/alrcatraz/astra-sre/commits)

</div>

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
- SSH key access to target devices (see `config/devices.yaml.example`)
- Hermes Agent (recommended for cron scheduling)

## Setup

```bash
git clone https://github.com/alrcatraz/astra-sre.git
cd astra-sre
```

No separate pip install required. Dependencies are managed via uv:

```bash
pip install uv  # if not already installed
uv sync
```

## Configuration

Target devices are configured by copying the example file:

```bash
cp config/devices.yaml.example config/devices.yaml
# then edit config/devices.yaml
```

The example (`config/devices.yaml.example`) contains a complete reference with all supported fields:

## Usage

### Daily Health Scan

```bash
python3 scripts/health-scan.py          # Markdown report
python3 scripts/health-scan.py --json   # Machine-readable
```

### Investigate an Incident

```bash
python3 scripts/triage.py "service X is failing"   # Search past incidents
python3 scripts/triage.py --list                    # List all recorded incidents
```

Combined with health scan for current system state:

### Auto-Suggest New Skills

```bash
python3 scripts/learn.py
python3 scripts/learn.py --cron          # Silent mode (output only when new suggestions)
```

### Fix Framework (sub-skills)

Repair sub-skills implement the recipes defined in the phase3 design.
Each is deployed as a Hermes Agent skill (`astra-sre-fix-<problem>`):

| Skill | Level | Description |
|:------|:-----:|:------------|
| `astra-sre-fix-restart-service` | L2/L3 | Service restarts (non-critical / critical) |
| `astra-sre-fix-mcp` | L2 | MCP process audit & cleanup |

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

## Dependencies

| Repository | Resource | Required | Purpose |
|:-----------|:---------|:--------:|:--------|
| [astra-knowledge-base-mcp](https://github.com/alcatrz/astra-knowledge-base-mcp) | Shared SQLite database via `ASTRA_KB_PATH` | Recommended | Incident data layer — `health-scan.py`, `triage.py`, and `learn.py` share the same DB schema |

### Knowledge Base: `sre_incidents`

Stores incident records (root cause analysis, diagnostics, fixes, prevention tips). Currently 2 example records covering:

- MCP process accumulation (redundant service memory leak)
- Health check false positive (external dependency cascading failure)

See `scripts/triage.py` for searching past incidents.

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
|
## Related

- [astra-knowledge-base-mcp](https://github.com/alrcatraz/astra-knowledge-base-mcp) — incident knowledge storage
- [astra-aiagent-infra](https://github.com/alrcatraz/astra-aiagent-infra) — ecosystem portal

## License

MIT — see [LICENSE](LICENSE).

> CI/CD: coming soon — see [astra-aiagent-infra](https://github.com/alrcatraz/astra-aiagent-infra) for ecosystem-wide pipeline plans.

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=alrcatraz/astra-sre&type=date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=alrcatraz/astra-sre&type=date" />
    <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=alrcatraz/astra-sre&type=date" width="600" />
  </picture>
</div>

---

## 中文版

### 概述

Astra SRE 为自建服务器和服务集群（8 台设备，覆盖 VPS、NAS、笔记本、路由器）提供统一运维层。采用分层架构：

1. **Plan（计划）** — 每日全设备健康扫描
2. **Diagnose（诊断）** — 基于症状的事故搜索 + 五路并行诊断
3. **Fix（修复）** — 带升级策略（L1–L3）的自动修复框架
4. **Learn（学习）** — 两次触发模式检测 → 自动建议新 skill

### 依赖关系

| 仓库 | 资源 | 必须 | 用途 |
|:-----|:-----|:----:|:-----|
| [astra-knowledge-base-mcp](https://github.com/alrcatraz/astra-knowledge-base-mcp) | 通过 `ASTRA_KB_PATH` 共享 SQLite 数据库 | 推荐 | 事故数据层 — `health-scan.py`、`triage.py`、`learn.py` 共用同一 DB |

---

<br>
