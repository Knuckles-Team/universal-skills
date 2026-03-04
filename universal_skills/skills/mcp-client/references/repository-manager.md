# Repository Manager MCP Reference

**Project:** `repository-manager`
**Entrypoint:** `repository-manager-mcp`

## Available Tool Tags (4)

| Env Variable | Default |
|-------------|----------|
| `FILE_OPERATIONSTOOL` | `True` |
| `GIT_OPERATIONSTOOL` | `True` |
| `MISCTOOL` | `True` |
| `SYSTEM_OPERATIONSTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "repository-manager": {
      "command": "repository-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "FILE_OPERATIONSTOOL": "True",
        "GIT_OPERATIONSTOOL": "True",
        "MISCTOOL": "True",
        "SYSTEM_OPERATIONSTOOL": "True"
      }
    }
  }
}
```

## HTTP Connection

Connects to a running MCP server over HTTP:

```json
{
  "mcpServers": {
    "repository-manager": {
      "url": "http://repository-manager-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `FILE_OPERATIONSTOOL` and disable all others:

```json
{
  "mcpServers": {
    "repository-manager": {
      "command": "repository-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "FILE_OPERATIONSTOOL": "True",
        "GIT_OPERATIONSTOOL": "False",
        "MISCTOOL": "False",
        "SYSTEM_OPERATIONSTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/repository-manager.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command repository-manager-mcp \
    --enable-tag FILE_OPERATIONSTOOL \
    --all-tags "FILE_OPERATIONSTOOL,GIT_OPERATIONSTOOL,MISCTOOL,SYSTEM_OPERATIONSTOOL"
```

## Tailored Skills Reference

### test-skill

**Description:** A test skill.

## test-skill Skill

### When to use
For testing.

### How to use
Call it.

### Examples
- Example 1: ...

### file-operations

**Description:** Advanced skill for file navigation, reading, editing, and search within the codebase.

## File Operations

This skill provides powerful tools for exploring and modifying the codebase. It includes capabilities for searching, reading, editing content, and managing directories.

### Tools

#### Search and Navigation
- **`search_codebase`**: Search for code patterns using regex (ripgrep).
    - `query` (str): Regex pattern.
    - `path` (str, optional): Directory to search (absolute or relative).
    - `glob_pattern` (str, optional): Filter files (e.g., "*.py").
    - `case_sensitive` (bool): Case sensitivity flag.
- **`find_files`**: Find files by name pattern.
    - `name_pattern` (str): Glob pattern for filename (e.g., "*.md").
    - `path` (str, optional): Directory to search.
- **`get_project_readme`**: content of the README.md file.
    - `path` (str, optional): Path to project or directory.

#### File Content
- **`read_file`**: Read file content.
    - `path` (str): Path to file.
    - `start_line` (int, optional): Start line number (1-indexed).
    - `end_line` (int, optional): End line number (1-indexed).

#### Editing
- **`text_editor`**: Versatile file system editor tool.
    - `command` (str): Command to execute (view, create, str_replace, insert, undo_edit).
    - `path` (str): Path to file.
    - `file_text` (str, optional): Content for create command.
    - `view_range` (List[int], optional): Range of lines for view command.
    - `old_str` (str, optional): String to replace.
    - `new_str` (str, optional): Replacement string.
    - `insert_line` (int, optional): Line to insert at.
- **`replace_in_file`**: Replace a block of text.
    - `path` (str): Path to file.
    - `target_content` (str): Exact text to replace (must be unique).
    - `replacement_content` (str): New text.
- **`create_directory`**: Create a new directory.
    - `path` (str): Path where directory should be created.
- **`delete_directory`**: Recursively delete a directory.
    - `path` (str): Path of directory to delete.
- **`rename_directory`**: Rename or move a directory or file.
    - `old_path` (str): Current path.
    - `new_path` (str): New path.

### Usage Examples

#### Searching for Code
```python
## specific query in a specific path
await search_codebase(query="class Git", path="/workspace/repo")
## case-insensitive search
await search_codebase(query="error", case_sensitive=False)
```

#### Reading a File Segment
```python
await read_file(path="/workspace/repo/README.md", start_line=1, end_line=10)
```

#### Replacing Text
```python
await replace_in_file(
    path="/workspace/repo/config.py",
    target_content="DEBUG = True",
    replacement_content="DEBUG = False"
)
```

#### Using Text Editor
```python
## Create a new file
await text_editor(command="create", path="/workspace/repo/new_script.py", file_text="print('Hello')")

## Insert text at line 5
await text_editor(command="insert", path="/workspace/repo/script.py", insert_line=5, new_str="    # New comment\n")
```

### git-operations

**Description:** Comprehensive skill for managing Git repositories, including cloning, pulling, branching, and versioning.

## Git Operations

This skill provides a complete set of tools for managing Git repositories. It covers cloning, pulling, committing (via git_action), and version management.

### Tools

#### Core Git Actions
- **`git_action`**: Execute any arbitrary Git command. Use this tool for any git operation not covered by specialized tools.
    - `command` (str): The git command (e.g., "git status", "git commit -m 'msg'").
    - `path` (str, optional): Path to execute the command in. Defaults to workspace.
    - `threads` (int, optional): Number of threads for parallel processing.
    - `set_to_default_branch` (bool, optional): Whether to checkout default branch.

#### Project Management
- **`create_project`**: Create a new project directory and initialize it as a git repository.
    - `path` (str): Path for the new project.
- **`clone_project`**: Clone a single repository.
    - `url` (str): URL of the repo.
    - `path` (str, optional): Path to clone into.
- **`clone_projects`**: Clone multiple repositories in parallel.
    - `projects` (List[str], optional): List of URLs.
    - `projects_file` (str, optional): File containing list of URLs.
    - `path` (str, optional): Path to clone into.
- **`pull_project`**: Pull updates for a single repository.
    - `path` (str): Path of the project to pull.
- **`pull_projects`**: Pull updates for multiple repositories in parallel.
    - `path` (str, optional): Workspace path containing projects.
- **`list_projects`**: List all projects in the workspace.
    - `projects_file` (str, optional): File containing list of URLs.
    - `path` (str, optional): Workspace path.

#### Maintenance
- **`run_pre_commit`**: Run pre-commit hooks.
    - `run` (bool): Run hooks (default True).
    - `autoupdate` (bool): Update hooks (default False).
    - `path` (str, optional): Path to run in.
- **`bump_version`**: Bump project version using bump2version.
    - `part` (str): Part to bump (major, minor, patch).
    - `path` (str, optional): Path to project.

### Usage Examples

#### Cloning a Repository
```python
await clone_project(url="https://github.com/user/repo.git", path="/workspace/repo")
```

#### Checking Status
```python
await git_action(command="git status", path="/workspace/repo")
```

#### Committing Changes
```python
await git_action(command="git add .", path="/workspace/repo")
await git_action(command="git commit -m 'feat: new feature'", path="/workspace/repo")
```

#### Common Git Actions

##### Configuration
```python
## Set user name globally
await git_action(command="git config --global user.name 'John Doe'")
## Set project as safe directory
await git_action(command="git config --global --add safe.directory '/workspace/repositories-list'")
```

##### Log & History
```python
## View recent logs
await git_action(command="git log -n 10", path="/workspace/repo")
## Check diff
await git_action(command="git diff HEAD~1", path="/workspace/repo")
## Blame file
await git_action(command="git blame README.md", path="/workspace/repo")
```

##### Remote Operations
```python
## Push changes
await git_action(command="git push origin main", path="/workspace/repo")
## Add remote
await git_action(command="git remote add origin https://github.com/user/repo.git", path="/workspace/repo")
```

##### Stashing
```python
## Stash changes
await git_action(command="git stash push -m 'temp work'", path="/workspace/repo")
## Pop stash
await git_action(command="git stash pop", path="/workspace/repo")
## List stashes
await git_action(command="git stash list", path="/workspace/repo")
```

##### Status & Reset
```python
## Check status
await git_action(command="git status", path="/workspace/repo")
## Hard reset (use with caution)
await git_action(command="git reset --hard HEAD", path="/workspace/repo")
## Clean untracked files
await git_action(command="git clean -fd", path="/workspace/repo")
```

##### Tagging
```python
## Create tag
await git_action(command="git tag -a v1.0 -m 'Version 1'", path="/workspace/repo")
## Push tags
await git_action(command="git push origin --tags", path="/workspace/repo")
```

#### Creating a New Project
```python
await create_project(path="/workspace/new-project")
```

### system-operations

**Description:** Specialized skill for executing system-level commands and scripts.

## System Operations

This skill provides the ability to execute arbitrary shell commands on the underlying system. This is a powerful capability that allows for extensive automation and integration not covered by other specific tools.

### Tools

#### Command Execution
- **`run_command`**: Execute a shell command.
    - `command` (str): The command to run (e.g., "ls -la", "python3 script.py").
    - `ctx` (Context, optional): Context for progress reporting (implicitly handled by MCP).

### Usage Examples

#### Listing Files
`run_command` command tool with `command` = `"ls -la /workspace"`

#### Running a Python Script

`run_command` command tool with `command` = `"python3 scripts/setup.py"`

#### Checking System Status
`run_command` command tool with `command` = `"uptime"`

### validation-scripting

**Description:** Create small Python scripts to validate library usage, troubleshoot issues, or verify functionality.

## Validation Scripting

This skill involves writing and executing small, targeted Python scripts to validate assumptions about libraries, test specific functionality, or troubleshoot complex issues by isolating them.

### Purpose

- **Validate Library Usage**: Verify how a specific function or class behaves before integrating it into the main codebase.
- **Troubleshoot Issues**: Isolate a bug by reproducing it in a minimal script.
- **Verify Fixes**: quick confirmation that a change works as expected.
- **Inspect Objects**: Print attributes and methods of objects at runtime to understand their structure.

### Process

1.  **Draft Script**: Create a file (e.g., `validate_feature.py`) using `text_editor` or `create_project` (if a full repo structure is needed).
2.  **Write Code**: Implement the minimal code necessary to test the feature or reproduce the issue.
3.  **Execute**: Run the script using `run_command`.
4.  **Analyze Output**: Review stdout/stderr to confirm behavior.
5.  **Refine**: Modify the script and re-run as needed.
6.  **Cleanup**: Delete the script once validation is complete.

### Toolkit

- **`text_editor`**: To create and edit the script file.
- **`run_command`**: To execute the script (`python3 script.py`).
- **`read_file`**: To check the script content if needed.
- **`delete_directory` / `run_command`**: To remove the script after use.

### Example Scenario

#### Validating a Library Function

```python
## Create the validation script
script_content = """
import os
from agent_utilities.base_utilities import to_boolean

print(f"True -> {to_boolean('True')}")
print(f"false -> {to_boolean('false')}")
print(f"None -> {to_boolean(None)}")
"""

await text_editor(command="create", path="validate_bool.py", file_text=script_content)

## Run the script
result = await run_command(command="python3 validate_bool.py")
print(result["output"])

## Cleanup
await run_command(command="rm validate_bool.py")
```

#### Troubleshooting an Import Error

```python
## Create a script to check sys.path and imports
script_content = """
import sys
print(sys.path)
try:
    import some_module
    print("Module imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
"""

await text_editor(command="create", path="debug_import.py", file_text=script_content)
await run_command(command="python3 debug_import.py")
await run_command(command="rm debug_import.py")
```
