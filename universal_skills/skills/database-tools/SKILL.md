---
name: database-tools
description: "Use this skill whenever the user wants to connect to, query, or manage databases, including PostgreSQL, MySQL, and MS SQL Server (MSSQL). Requires setting up a connections.json file with credentials. Can execute SQL queries, inspect schemas, dump data, and repair broken tables depending on dialect."
categories: [Data & Documents]
tags: [database, sql, postgresql, mysql, mssql, querying, schema, data-extraction]
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

## Best Practices
1. **Explore First**: Start by describing the database schema. Example: `SELECT table_name FROM information_schema.tables WHERE table_schema='public';`
2. **Limit Rows**: Always use `LIMIT N` or `TOP N` on initial `SELECT` queries to avoid massive outputs crashing your context window.
3. **Write Operations**: For state-changing operations, ensure you double-check conditions (e.g., proper `WHERE` clauses). The script will prompt for safety or block you based on configuration—follow the script's instructions.
