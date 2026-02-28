---
name: session-handoff
description: Create and restore comprehensive context handoff documents for agent session transfers. Use when context is getting full, a major task milestone is complete, work is pausing, or when resuming from a previous session. Triggers include "create handoff", "save state", "context is full", "I need to pause", "load handoff", "resume where we left off", or proactively after 5+ file edits or complex multi-step work. Do NOT use for project documentation — this is for agent-to-agent context preservation.
categories: [Core, Productivity]
tags: [handoff, context, session, resumption, continuity, memory]
---

# Session Handoff

Create comprehensive handoff documents that enable a fresh agent to seamlessly continue work with zero ambiguity. Solves the long-running agent context exhaustion problem.

---

## Mode Selection

Determine which mode applies:

**Creating a handoff?** User wants to save current state, pause work, or context is getting full.
→ Follow **CREATE Workflow** below

**Resuming from a handoff?** User wants to continue previous work or load context.
→ Follow **RESUME Workflow** below

**Proactive suggestion** — After substantial work (5+ file edits, complex debugging, major design decisions), suggest:
> "We've made significant progress. Consider creating a handoff document to preserve this context for future sessions. Say 'create handoff' when ready."

---

## CREATE Workflow

### Step 1: Generate Scaffold

Run the scaffold script to create a pre-filled handoff document:

```bash
python scripts/create_handoff.py [task-slug]
# Example: python scripts/create_handoff.py implementing-user-auth

# For continuation handoffs (linking to previous):
python scripts/create_handoff.py "auth-part-2" --continues-from 2024-01-15-143022-auth.md
```

The script will:
- Create `.agent/handoffs/` directory if needed
- Generate timestamped filename (`YYYY-MM-DD-HHMMSS-[slug].md`)
- Pre-fill: project path, git branch, recent commits, modified files
- Add chain links if continuing from a previous handoff

### Step 2: Complete the Document

Open the generated file and fill in all `[TODO: ...]` sections. Prioritize:

1. **Current State Summary** — What is happening right now
2. **Important Context** — Critical info the next agent MUST know
3. **Immediate Next Steps** — Clear, actionable first steps (numbered)
4. **Decisions Made** — Choices with rationale, not just outcomes

Use [references/handoff-template.md](references/handoff-template.md) for guidance.

### Step 3: Validate

```bash
python scripts/validate_handoff.py <handoff-file>
```

The validator checks:
- [ ] No `[TODO: ...]` placeholders remaining
- [ ] Required sections present and populated
- [ ] No potential secrets detected (API keys, tokens, passwords)
- [ ] Referenced files exist
- [ ] Quality score (0–100)

**Do not finalize a handoff with secrets detected or a score below 70.**

### Step 4: Confirm

Report to user:
- Handoff file location
- Validation score and any warnings
- Summary of captured context
- First action item for the next session

---

## RESUME Workflow

### Step 1: Find Available Handoffs

```bash
python scripts/list_handoffs.py
```

Lists all handoffs in the current project with dates, titles, and completion status.

### Step 2: Check Staleness

```bash
python scripts/check_staleness.py <handoff-file>
```

Staleness levels:
- **FRESH** — Safe to resume; minimal changes since handoff
- **SLIGHTLY_STALE** — Review changes, then resume
- **STALE** — Verify context carefully before proceeding
- **VERY_STALE** — Consider creating a fresh handoff first

The script checks: time elapsed, git commits since handoff, files changed, branch divergence, missing referenced files.

### Step 3: Load the Handoff

Read the relevant handoff document completely before taking any action. If the handoff is part of a chain (has a "Continues from" link), also read the linked previous handoff for full context.

### Step 4: Verify Context

Follow [references/resume-checklist.md](references/resume-checklist.md):

1. Verify project directory and git branch match
2. Check if blockers from the handoff have been resolved
3. Validate assumptions still hold (run a quick `git status`)
4. Review modified files for conflicts
5. Check environment state (services running, env vars set)

### Step 5: Begin Work

Start with **Immediate Next Steps** item #1 from the handoff document. Reference:
- "Critical Files" section for important file locations
- "Key Patterns Discovered" for conventions to follow
- "Potential Gotchas" to avoid known issues

### Step 6: Update or Chain

As you work:
- Mark completed items in "Pending Work"
- Add new discoveries to relevant sections
- For long sessions: create a new handoff with `--continues-from` to chain them

---

## Handoff Chaining

For long-running projects, chain handoffs together to maintain context lineage:

```
handoff-1.md (initial work)
    ↓
handoff-2.md --continues-from handoff-1.md
    ↓
handoff-3.md --continues-from handoff-2.md
```

When resuming from a chain, read the most recent handoff first, then reference predecessors as needed for deeper context.

---

## Storage Location

Handoffs are stored in: `.agent/handoffs/`

Naming convention: `YYYY-MM-DD-HHMMSS-[slug].md`

Example: `2024-01-15-143022-implementing-auth.md`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create_handoff.py [slug] [--continues-from <file>]` | Generate new handoff with smart scaffolding |
| `scripts/list_handoffs.py [path]` | List available handoffs in a project |
| `scripts/validate_handoff.py <file>` | Check completeness, quality, and security |
| `scripts/check_staleness.py <file>` | Assess if handoff context is still current |

## References

- [references/handoff-template.md](references/handoff-template.md) — Complete template structure with guidance
- [references/resume-checklist.md](references/resume-checklist.md) — Verification checklist for resuming agents
