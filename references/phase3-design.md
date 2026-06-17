# astra-sre Phase 3 — Automated Repair Framework Design

> Version: 1.0
> Date: 2026-06-07
> Status: Design Finalised

---

## Core Principles

No binary choice — gradual transition. First write recipes (with trigger conditions and decision-point markers), reserving space for auto-safe expansion. Once trust is established, progressively relax the manual gates on safe operations.

## Repair Levels (L1/L2/L3)

Classify by **blast radius**, not by the operation itself:

| Level | Definition | Example | Execution Strategy |
|:-----:|:-----------|:--------|:-------------------|
| **L1** Transparent Repair | User is completely unaware, no service impact | Config changes, cache clears, notification retries | ✅ Fully automatic |
| **L2** Noticeable but Safe | Brief impact or affects non-critical services | Restart non-critical service, run read-only diagnostics | ✅ Automatic + notify afterwards |
| **L3** Risky or Irreversible | Potential data loss or service interruption | Delete data, rotate tokens, rebuild service, restart critical service | 🛑 Requires your approval |

## Repair Flow

```
Incident ──→ health-scan.py parallel diagnostics
                  │
                  ▼
            Query sre_incidents ──→ Match found?
                  │                        │
                No                        Yes
                  │                        │
                  ▼                        ▼
          Collaborate on              Determine repair level
          investigation                   │
                  │              ┌────────┼────────┐
                  │              │        │        │
                  │             L1       L2       L3
                  │           Auto     Auto +   Require
                  │          Execute   Notify   Approval
                  │              │        │        │
                  │              └────────┼────────┘
                  │                       │
                  │              Verification Probe ← Critical!
                  │              │              │
                  │            Healthy        Worse
                  │              │              │
                  │             ✅         Rollback/Notify
                  │
                  ▼
          Log to sre_incidents
                  │
        Same tag appears twice? ──→ learn.py suggests sub-skill
```

## Verification Probes

Every automatic repair step must be followed immediately by verification:

- Reuse a single probe from `health-scan.py` (e.g. `--mode <service-name>`)
- Compare state before and after repair
- If post-repair state is worse than pre-repair → trigger **automatic rollback** or **emergency notification**

## Repair Locks

Prevent concurrent repairs on the same class of issue (keyed by tag).

### Lock Implementation

```
Lock file: /tmp/astra-sre-lock-<tag>.lock
Content:   PID + lock timestamp (second-granularity)
```

### Lock/Unlock Logic

```
Acquiring lock:
  1. Does the lock file exist?
     ├─ No  → Create lock (write current PID + timestamp) → Acquired ✅
     └─ Yes → Read lock content
              ├─ PID still alive → Held by another repair, queue ⏳
              └─ PID is dead    → Stale lock! Remove old lock, acquire new ✅

Releasing lock:
  Remove lock file (must execute regardless of success or failure)
```

### Key Design Decisions

- **PID liveliness check** uses `kill -0 <PID>` (sends no signal, only checks whether the process exists)
- **No hard timeout** — repair tasks may run for hours (e.g. system upgrades, full E2EE recovery). As long as the PID is alive, the lock is valid
- **Automatic stale lock cleanup** — the only criterion: if the PID is dead, the lock is stale, regardless of whether it was created 1 minute or 1 day ago
- **Lock age monitoring (optional, non-mandatory)** — log a hint when lock age exceeds 30 minutes to help debug "is it stuck?" scenarios, but do not force-unlock

## Sub-skill Template

Each repair sub-skill should contain the following fields:

```yaml
name: astra-sre-fix-<problem>
level: L1|L2|L3            # Repair level
triggers:                   # Trigger conditions (matched against health-scan.py output)
  - <probe>: <pattern>
safety:                     # Safety notes
  rollback: <how to roll back>
  risks: [<list of risks>]
steps:                      # Repair steps
  - <step> [auto|gate]      # auto = automatic, gate = requires your approval
verify: <verification probe>
```

## External Incident Intake

Repairs performed outside the SRE framework enter `sre_incidents` through the following paths:

| Scenario | Trigger | My Behaviour |
|:---------|:--------|:-------------|
| We investigate and fix together | "Done" declared by the agent | Proactively ask: "Shall I log this in sre_incidents?" |
| You fix and tell me | You say it's fixed | Ask for root cause, assess whether it's worth recording, ask if you'd like it stored |
| Colleague/third-party experience | You say "store this" or "look at this" | Extract key information and write to sre_incidents |
| Confirmed recording | Your consent ("yes"/"sure"/"ok") | Execute the write |
| Skip | You say "not needed" / "skip" | Do not record |

> No specific keywords or emoji required. The agent takes responsibility for identifying and asking — you just talk as you normally would.
