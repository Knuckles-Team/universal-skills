---
name: session-handoff
description: >-
  Create and restore comprehensive context handoff documents for agent session
  transfers. Use when context is getting full, a major task milestone is complete,
  work is pausing, or when resuming from a previous session. Triggers include
  "create handoff", "save state", "context is full", "I need to pause", "load
  handoff", "resume where we left off", or proactively after 5+ file edits or
  complex multi-step work. Do NOT use for project documentation — this is for
  agent-to-agent context preservation.
license: MIT
tags: [handoff, context, session, resumption, continuity, memory]
metadata:
  author: Genius
  version: '0.45.0'
---
# Session Handoff

Create comprehensive handoff documents that enable a fresh agent to seamlessly continue work with zero ambiguity. Solves the long-running agent context exhaustion problem.

---

# Session Handoff

Create comprehensive handoff documents that enable a fresh agent to seamlessly continue work with zero ambiguity. Solves the long-running agent context exhaustion problem.

---

## Capabilities

1.  **Scaffold Generation** — Auto-scaffolds handoff documents with system, git, and file context.
2.  **Handoff Validation** — Performs secret-scanning, placeholder checks, and quality scoring.
3.  **Staleness Scoring** — Calculates divergency metrics based on git timeline and files.
4.  **Episodic Memory Integration** — Double-writes handoffs as markdown and Graph-OS knowledge nodes.

---

## Steps

### Step 1: mode_selection
Determine which mode applies to the current session:
- **Creating a handoff?** User wants to save current state, pause work, or context is getting full.
  - Follow branch: `generate_scaffold` -> `complete_and_validate` -> `memory_persistence`.
- **Resuming from a handoff?** User wants to continue previous work or load context.
  - Follow branch: `locate_handoffs` -> `verify_staleness_context` -> `begin_execution`.
- **Proactive suggestion** — After substantial work (5+ file edits, complex debugging, major design decisions), suggest:
  > "We've made significant progress. Consider creating a handoff document to preserve this context for future sessions. Say 'create handoff' when ready."

### Step 2: generate_scaffold [depends_on: mode_selection]
Run the scaffold script to create a pre-filled handoff document if in CREATE mode:
- Requires: primary script `scripts/create_handoff.py [task-slug]`
  - Example: `python scripts/create_handoff.py implementing-user-auth`
  - For continuation handoffs (linking to previous): `python scripts/create_handoff.py "auth-part-2" --continues-from 2024-01-15-143022-auth.md`
- The script will:
  - Create `.agent/handoffs/` directory if needed
  - Generate timestamped filename (`YYYY-MM-DD-HHMMSS-[slug].md`)
  - Pre-fill: project path, git branch, recent commits, modified files
  - Add chain links if continuing from a previous handoff

### Step 3: locate_handoffs [depends_on: mode_selection]
Find available handoffs if in RESUME mode using either local filesystem or the Knowledge Graph:
- **Local Filesystem**:
  ```bash
  python scripts/list_handoffs.py
  ```
- **Knowledge Graph (Recommended)**: Use the `kg_memory_recall` MCP tool with `memory_type` set to `episodic` to semantically search for previous handoff states related to your current task. This is particularly useful if the local `.agent/handoffs/` directory was lost or if you need to find a handoff by context rather than filename.

### Step 4: complete_and_validate [depends_on: generate_scaffold]
Open the generated file, fill in all sections, and run the validation script to verify completeness and security:
- Open the generated file and fill in all `[TODO: ...]` sections. Prioritize:
  1. **Current State Summary** — What is happening right now
  2. **Important Context** — Critical info the next agent MUST know
  3. **Immediate Next Steps** — Clear, actionable first steps (numbered)
  4. **Decisions Made** — Choices with rationale, not just outcomes
  Use `references/handoff-template.md` for guidance.
- Execute validation:
  ```bash
  python scripts/validate_handoff.py <handoff-file>
  ```
  - The validator checks: No `[TODO: ...]` placeholders remaining, required sections present and populated, no potential secrets detected (API keys, tokens, passwords), referenced files exist, and a quality score (0–100).
- **Do not finalize a handoff with secrets detected or a score below 70.**
- Report to user: Handoff file location, validation score and any warnings, summary of captured context, and first action item for the next session.

### Step 5: verify_staleness_context [depends_on: locate_handoffs]
Assess if handoff context is still current and analyze divergence:
- Requires: primary script `scripts/check_staleness.py <handoff-file>`
- The script checks: time elapsed, git commits since handoff, files changed, branch divergence, missing referenced files.
- Staleness levels:
  - **FRESH** — Safe to resume; minimal changes since handoff
  - **SLIGHTLY_STALE** — Review changes, then resume
  - **STALE** — Verify context carefully before proceeding
  - **VERY_STALE** — Consider creating a fresh handoff first

### Step 6: memory_persistence [depends_on: complete_and_validate]
Persist the validated handoff to both local markdown and Graph-OS:
- Markdown local fallback: file is stored in `.agent/handoffs/` following the naming convention `YYYY-MM-DD-HHMMSS-[slug].md`.
- Knowledge Graph global memory store:
  - Invoke `kg_memory_store` MCP tool with `memory_type` set to `episodic`.
  - Pass the full content of the handoff document, and include tags like `handoff`, `session`, and the `[slug]`.
  - This ensures the dual-write strategy: the Markdown file acts as a local fallback, while the KG serves as the global memory store.
- For long-running projects, chain handoffs together to maintain context lineage:
  `handoff-1.md` (initial work) -> `handoff-2.md --continues-from handoff-1.md` -> `handoff-3.md --continues-from handoff-2.md`.

### Step 7: begin_execution [depends_on: verify_staleness_context]
Load the verified context and begin working on the immediate next steps list:
- Follow `references/resume-checklist.md`:
  1. Verify project directory and git branch match
  2. Check if blockers from the handoff have been resolved
  3. Validate assumptions still hold (run a quick `git status`)
  4. Review modified files for conflicts
  5. Check environment state (services running, env vars set)
- Start with **Immediate Next Steps** item #1 from the handoff document. Reference:
  - "Critical Files" section for important file locations
  - "Key Patterns Discovered" for conventions to follow
  - "Potential Gotchas" to avoid known issues
- As you work: mark completed items in "Pending Work", add new discoveries to relevant sections, and for long sessions create a new handoff with `--continues-from` to chain them.

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

- `references/handoff-template.md` — Complete template structure with guidance
- `references/resume-checklist.md` — Verification checklist for resuming agents
