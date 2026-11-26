---
name: web-design-guidelines
domain: web-development
skill_type: skill
description: >-
  Review UI code for Web Interface Guidelines compliance. Use when asked to
  "review my UI", "check accessibility", "audit design", "review UX", or "check my
  site against best practices".
license: MIT
tags: [ui, design, guidelines, accessibility, audit]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---
# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Steps

1. Fetch the current rules with WebFetch from `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md`. Verify that the returned text contains the rule list and the output format instructions.
2. Resolve the files to review with `git ls-files 'src/**/*.tsx'` (or the pattern the user gave) and ask the user when none is given. Verify that the command prints at least one path.
3. Read each file and apply every fetched rule. Verify that each finding quotes a real line, checked with `grep -n "<quoted text>" <file>`.
4. Report findings in the terse `file:line` format the guidelines specify. Verify that every reported line matches the form `path:NN` and no finding lacks a location.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| WebFetch returns an error or empty body | The raw GitHub URL is unreachable or blocked | Fetch the same URL with `curl -sSL <url>` in Bash and review against that text. |
| No files match the pattern | The glob does not fit the project layout | Run `git ls-files | head -50`, pick the right extension and directory, and rerun. |
| Findings lack line numbers | Files were read without line numbering | Re-read each file with `cat -n <file>` and cite the printed numbers. |

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
