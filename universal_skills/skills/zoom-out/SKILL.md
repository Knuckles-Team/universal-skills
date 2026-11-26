---
name: zoom-out
domain: system
skill_type: skill
description: >-
  Tell the agent to zoom out and give broader context or a higher-level
  perspective. Use when you're unfamiliar with a section of code or need to
  understand how it fits into the bigger picture.
license: MIT
tags: [zoom out, meta, overview, context]
metadata:
  version: '1.6.2'
  author: Knuckles-Team
---

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary.

## Steps

1. Identify the area in question with `grep -rn "<symbol or file name>" .`. Verify that the output lists the definition and its call sites.
2. List the modules around it with `ls <directory of the area>`. Verify that the neighbouring modules are named in your map.
3. Find the callers one layer up with `grep -rn "import <module>" .` (or the language's equivalent). Verify that each caller you report appears in the output.
4. Write the map using the project's domain glossary vocabulary, checking terms with `grep -rn -i "<term>" CONTEXT.md docs/`. Verify that every term used exists in the glossary or is flagged as missing.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| No call sites found | The symbol is used through a re-export or dynamic dispatch | Search for the re-exporting module name and for string references with `grep -rn "<name>" --include=*.py --include=*.ts .`. |
| No domain glossary exists | The project has no `CONTEXT.md` or glossary file | Say so in the map and use the names found in the code, rather than inventing vocabulary. |
| Map is too detailed | The agent stayed at the file level | Go up one more layer: group modules by responsibility and drop internal helpers from the map. |
