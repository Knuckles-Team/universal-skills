---
name: database-tools
domain: infrastructure
skill_type: skill
description: >-
  Use this skill whenever the user wants to connect to, query, or manage
  databases, including PostgreSQL, MySQL, and MS SQL Server (MSSQL). Requires
  setting up a connections.json file with credentials. Can execute SQL queries,
  inspect schemas, dump data, and repair broken tables depending on dialect.
license: MIT
tags: [database, sql, postgresql, mysql, mssql, querying, schema, data-extraction]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
---
# Database Tools

## Overview
This skill combines tools for PostgreSQL, MySQL, and Microsoft SQL Server (MSSQL).

## Capabilities/Tools

You have three specialized query scripts located in `scripts/`:
- **PostgreSQL**: `scripts/postgres_query.py`
- **MySQL**: `scripts/mysql_query.py`
- **MSSQL**: `scripts/mssql_query.py`

These scripts allow you to securely connect to a database using predefined alias configurations, execute read/write queries, explain plans, and format output. DO NOT attempt to write your own `psycopg2` or `pymysql` wrappers; always use these scripts unless explicitly told otherwise.

## Permissions & Safety
The query scripts analyze every SQL statement before execution. Read-only queries (`SELECT`, `SHOW`, `EXPLAIN`) will execute directly. Write queries (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.) will NOT execute implicitly.

## Setup
1. Check if `connections.json` exists in the skill root or your working directory. If it doesn't exist, create it from `connections.example.json`.
2. Add the user's database credentials securely to `connections.json`. The user must either provide these or tell you where to find them. Do NOT guess passwords.
3. Identify the connection by its top-level alias (e.g., `prod_db`, `local_test`).

## Usage

### PostgreSQL (`postgres_query.py`)
```bash
python scripts/postgres_query.py <connection_name> "<sql_query>" [--json] [--explain]
```

### MySQL (`mysql_query.py`)
```bash
python scripts/mysql_query.py <connection_name> "<sql_query>" [--json] [--explain]
```

### MSSQL (`mssql_query.py`)
```bash
python scripts/mssql_query.py <connection_name> "<sql_query>" [--json] [--explain]
```

## Steps

1. Locate or create `connections.json`.
   Run `ls connections.json` and copy `connections.example.json` if missing. Verify that the needed alias exists and that credentials came from the user, not guesses.
2. List configured databases for the dialect.
   Run `python scripts/postgres_query.py --list` (or `mysql_query.py` / `mssql_query.py`). Verify that the target alias appears in the output.
3. Explore the schema before querying.
   Run `python scripts/postgres_query.py --db <alias> --tables`. Verify that the expected tables are listed.
4. Run a bounded read query.
   Run `python scripts/postgres_query.py --db <alias> --query "SELECT * FROM <table>" --limit 20`. Verify that rows return and the count respects the limit.
5. Gate any write query.
   Use the same script with `--query "UPDATE ... WHERE ..."` only after confirming the `WHERE` clause. Verify that a follow-up `SELECT` shows only the intended rows changed.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| `Database '<alias>' not found` | Alias missing from `connections.json` | Run `--list`, then fix the alias or add the entry from `connections.example.json` |
| Write query is blocked | Safety analysis blocks state-changing SQL without approval | Follow the script's prompt, confirm with the user, and narrow the `WHERE` clause |
| Connection refused or authentication failed | Wrong host, port, or credentials | Ask the user to confirm the credentials, test with `--list`, and never guess passwords |

## Best Practices
1. **Explore First**: Start by describing the database schema. Example: `SELECT table_name FROM information_schema.tables WHERE table_schema='public';`
2. **Limit Rows**: Always use `LIMIT N` or `TOP N` on initial `SELECT` queries to avoid massive outputs crashing your context window.
3. **Write Operations**: For state-changing operations, ensure you double-check conditions (e.g., proper `WHERE` clauses). The script will prompt for safety or block you based on configuration—follow the script's instructions.
