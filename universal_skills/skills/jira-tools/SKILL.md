---
name: jira-tools
description: Interact with Jira using natural language. Use when the user mentions Jira issues (e.g., "PROJ-123"), asks about tickets, wants to create/view/update issues, check sprint status, or manage their Jira workflow. Triggers on keywords like "jira", "issue", "ticket", "sprint", "backlog", or issue key patterns (e.g., ABC-123). Do NOT use for GitHub PRs or issues — use github-tools instead.
categories: [Productivity, Development]
tags: [jira, tickets, sprint, backlog, atlassian, project-management]
---

# Jira Tools

Natural language interaction with Jira. Supports two backends: the `jira` CLI tool and the Atlassian MCP server.

---

## Backend Detection

Run this check first to determine which backend is available:

```
1. Check if jira CLI is installed:
   → Run: which jira
   → If found: USE CLI BACKEND

2. If no CLI, check for Atlassian MCP:
   → Look for mcp__atlassian__* tools in available tools
   → If available: USE MCP BACKEND

3. If neither:
   → GUIDE USER TO SETUP (see below)
```

| Backend | When to Use | Reference |
|---------|-------------|-----------|
| **jira CLI** | `jira` command available | CLI commands below |
| **Atlassian MCP** | `mcp__atlassian__*` tools available | MCP tools below |
| **Neither** | Guide to install CLI | Setup section |

---

## Quick Reference — CLI Backend

| Intent | Command |
|--------|---------|
| View issue | `jira issue view ISSUE-KEY` |
| List my issues | `jira issue list -a$(jira me)` |
| My in-progress | `jira issue list -a$(jira me) -s"In Progress"` |
| Create issue | `jira issue create -tType -s"Summary" -b"Description"` |
| Move/transition | `jira issue move ISSUE-KEY "State"` |
| Assign to me | `jira issue assign ISSUE-KEY $(jira me)` |
| Add comment | `jira issue comment add ISSUE-KEY -b"Comment text"` |
| Open in browser | `jira open ISSUE-KEY` |
| Current sprint | `jira sprint list --state active` |

---

## Quick Reference — MCP Backend

| Intent | MCP Tool |
|--------|----------|
| Search issues | `mcp__atlassian__searchJiraIssuesUsingJql` |
| View issue | `mcp__atlassian__getJiraIssue` |
| Create issue | `mcp__atlassian__createJiraIssue` |
| Update issue | `mcp__atlassian__editJiraIssue` |
| Get transitions | `mcp__atlassian__getTransitionsForJiraIssue` |
| Transition issue | `mcp__atlassian__transitionJiraIssue` |
| Add comment | `mcp__atlassian__addCommentToJiraIssue` |
| Lookup user ID | `mcp__atlassian__lookupJiraAccountId` |
| List projects | `mcp__atlassian__getVisibleJiraProjects` |

---

## Issue Key Detection

Issue keys follow the pattern `[A-Z]+-[0-9]+` (e.g., `PROJ-123`, `ABC-1`).

When a user mentions an issue key in conversation:
- **CLI:** `jira issue view KEY` or `jira open KEY`
- **MCP:** call `getJiraIssue` with the key

---

## Workflow Guidelines

### Creating Tickets

1. Research context (referenced code, PRs, tickets)
2. Draft ticket with summary, description, type, and priority
3. Review with user before creating
4. Create using the detected backend

### Updating Tickets

1. Fetch current issue state first
2. Show current vs proposed changes
3. Get explicit approval before modifying
4. Add a comment explaining the change

---

## Critical Safety Rules

- **NEVER transition without fetching current status first** — workflows may require intermediate states; "To Do" → "Done" may fail silently if "In Progress" is required
- **NEVER assign using display names (MCP)** — only account IDs work; always call `lookupJiraAccountId` first
- **NEVER edit description without showing original** — Jira has no undo; always show what will be replaced
- **NEVER use `--no-input` (CLI) without all required fields** — fails silently with cryptic errors
- **NEVER assume transition names are universal** — "Done", "Closed", "Complete" vary by project
- **NEVER bulk-modify without explicit approval** — each change notifies all watchers

### Safety Checklist

- Always show the command or tool call before executing
- Always get approval before modifying tickets
- Preserve original information when editing descriptions
- Verify updates after applying them
- Surface authentication issues clearly so the user can resolve them

---

## Setup (No Backend Available)

If neither CLI nor MCP is available, guide the user:

```
To interact with Jira, install one of:

1. jira CLI (recommended):
   https://github.com/ankitpokhrel/jira-cli

   Install:  brew install ankitpokhrel/jira-cli/jira-cli
   Setup:    jira init

2. Atlassian MCP Server:
   Configure in your MCP settings with Atlassian API credentials.
   See: https://github.com/sooperset/mcp-atlassian
```

---

## When to Load References

| Task | Load Reference? |
|------|-----------------|
| View/list issues | No — Quick Reference above is sufficient |
| Create with description | Yes — CLI needs temp-file pattern for multi-line content |
| Transition issue | Yes — need to fetch valid transition IDs first |
| JQL search | Yes — for complex filter queries |
| Link issues | Yes — MCP has limitations; may need a helper script |
