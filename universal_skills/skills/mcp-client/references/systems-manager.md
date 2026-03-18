# Systems Manager MCP Reference

**Project:** `systems-manager`

## Available Tool Tags (17)

| Env Variable | Default |
|-------------|----------|
| `CRONTOOL` | `True` |
| `DISKTOOL` | `True` |
| `FILESYSTEMTOOL` | `True` |
| `FIREWALL_MANAGEMENTTOOL` | `True` |
| `LOGTOOL` | `True` |
| `MISCTOOL` | `True` |
| `NETWORKTOOL` | `True` |
| `NODEJSTOOL` | `True` |
| `PROCESSTOOL` | `True` |
| `PYTHONTOOL` | `True` |
| `SERVICETOOL` | `True` |
| `SHELLTOOL` | `True` |
| `SSH_MANAGEMENTTOOL` | `True` |
| `SYSTEMTOOL` | `True` |
| `SYSTEM_MANAGEMENTTOOL` | `True` |
| `TEXT_EDITORTOOL` | `True` |
| `USERTOOL` | `True` |

## Stdio Connection (Default)

Spawns the MCP server locally as a subprocess:

```json
{
  "mcpServers": {
    "systems-manager": {
      "command": "systems-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "CRONTOOL": "True",
        "DISKTOOL": "True",
        "FILESYSTEMTOOL": "True",
        "FIREWALL_MANAGEMENTTOOL": "True",
        "LOGTOOL": "True",
        "MISCTOOL": "True",
        "NETWORKTOOL": "True",
        "NODEJSTOOL": "True",
        "PROCESSTOOL": "True",
        "PYTHONTOOL": "True",
        "SERVICETOOL": "True",
        "SHELLTOOL": "True",
        "SSH_MANAGEMENTTOOL": "True",
        "SYSTEMTOOL": "True",
        "SYSTEM_MANAGEMENTTOOL": "True",
        "TEXT_EDITORTOOL": "True",
        "USERTOOL": "True"
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
    "systems-manager": {
      "url": "http://systems-manager-mcp:8787/mcp",
      "timeout": 200000
    }
  }
}
```

## Single-Tag Config Example

Enable only `CRONTOOL` and disable all others:

```json
{
  "mcpServers": {
    "systems-manager": {
      "command": "systems-manager-mcp",
      "args": [
        "--transport",
        "stdio"
      ],
      "env": {
        "CRONTOOL": "True",
        "DISKTOOL": "False",
        "FILESYSTEMTOOL": "False",
        "FIREWALL_MANAGEMENTTOOL": "False",
        "LOGTOOL": "False",
        "MISCTOOL": "False",
        "NETWORKTOOL": "False",
        "NODEJSTOOL": "False",
        "PROCESSTOOL": "False",
        "PYTHONTOOL": "False",
        "SERVICETOOL": "False",
        "SHELLTOOL": "False",
        "SSH_MANAGEMENTTOOL": "False",
        "SYSTEMTOOL": "False",
        "SYSTEM_MANAGEMENTTOOL": "False",
        "TEXT_EDITORTOOL": "False",
        "USERTOOL": "False"
      }
    }
  }
}
```

## CLI Usage

```bash
# List tools (all tags enabled)
python scripts/mcp_client.py --config references/systems-manager.json --action list-tools

# Generate a single-tag config
python scripts/mcp_client.py --action generate-config \
    --mcp-command systems-manager-mcp \
    --enable-tag CRONTOOL \
    --all-tags "CRONTOOL,DISKTOOL,FILESYSTEMTOOL,FIREWALL_MANAGEMENTTOOL,LOGTOOL,MISCTOOL,NETWORKTOOL,NODEJSTOOL,PROCESSTOOL,PYTHONTOOL,SERVICETOOL,SHELLTOOL,SSH_MANAGEMENTTOOL,SYSTEMTOOL,SYSTEM_MANAGEMENTTOOL,TEXT_EDITORTOOL,USERTOOL"
```

## Tailored Skills Reference

### git-cli-docs

**Description:** High-level reference for the Git command-line interface.

## Git Cli Docs Documentation

High-level reference for the Git command-line interface.

**Original Source**: [https://git-scm.com/docs/git](https://git-scm.com/docs/git)

**Contains**: 284 markdown files with full folder structure.
*Last updated: February 27, 2026*

### 📚 Table of Contents

- [About Git](reference/about.md)
- [About Trademark](reference/about_trademark.md)
- [Api Index](reference/api-index.md)
- [Api Trace2](reference/api-trace2.md)
- [Book](reference/book.md)
- [Git Cheat Sheet](reference/cheat-sheet.md)
- [Community](reference/community.md)
- [Git credential helpers](reference/doc_credential-helpers.md)
- [External Links](reference/doc_ext.md)
- [Reference](reference/docs.md)
- [Git Add](reference/git-add.md)
- [Git Am](reference/git-am.md)
- [Git Annotate](reference/git-annotate.md)
- [Git Apply](reference/git-apply.md)
- [Git Archimport](reference/git-archimport.md)
- [Git Archive](reference/git-archive.md)
- [Git Backfill](reference/git-backfill.md)
- [Git Bisect](reference/git-bisect.md)
- [Git Blame](reference/git-blame.md)
- [Git Branch](reference/git-branch.md)
- [Git Bugreport](reference/git-bugreport.md)
- [Git Bundle](reference/git-bundle.md)
- [Git Cat File](reference/git-cat-file.md)
- [Git Check Attr](reference/git-check-attr.md)
- [Git Check Ignore](reference/git-check-ignore.md)
- [Git Check Mailmap](reference/git-check-mailmap.md)
- [Git Check Ref Format](reference/git-check-ref-format.md)
- [Git Checkout Index](reference/git-checkout-index.md)
- [Git Checkout](reference/git-checkout.md)
- [Git Cherry Pick](reference/git-cherry-pick.md)
- [Git Cherry](reference/git-cherry.md)
- [Git Citool](reference/git-citool.md)
- [Git Clean](reference/git-clean.md)
- [Git Clone](reference/git-clone.md)
- [Git Column](reference/git-column.md)
- [Git Commit Graph](reference/git-commit-graph.md)
- [Git Commit Tree](reference/git-commit-tree.md)
- [Git Commit](reference/git-commit.md)
- [Git Config](reference/git-config.md)
- [Git Count Objects](reference/git-count-objects.md)
- [Git Credential Cache](reference/git-credential-cache.md)
- [Git Credential Store](reference/git-credential-store.md)
- [Git Credential](reference/git-credential.md)
- [Git Cvsexportcommit](reference/git-cvsexportcommit.md)
- [Git Cvsimport](reference/git-cvsimport.md)
- [Git Cvsserver](reference/git-cvsserver.md)
- [Git Daemon](reference/git-daemon.md)
- [Git Describe](reference/git-describe.md)
- [Git Diagnose](reference/git-diagnose.md)
- [Git Diff Files](reference/git-diff-files.md)
- [Git Diff Index](reference/git-diff-index.md)
- [Git Diff Pairs](reference/git-diff-pairs.md)
- [Git Diff Tree](reference/git-diff-tree.md)
- [Git Diff](reference/git-diff.md)
- [Git Difftool](reference/git-difftool.md)
- [Git Fast Export](reference/git-fast-export.md)
- [Git Fast Import](reference/git-fast-import.md)
- [Git Fetch Pack](reference/git-fetch-pack.md)
- [Git Fetch](reference/git-fetch.md)
- [Git Filter Branch](reference/git-filter-branch.md)
- [Git Fmt Merge Msg](reference/git-fmt-merge-msg.md)
- [Git For Each Ref](reference/git-for-each-ref.md)
- [Git For Each Repo](reference/git-for-each-repo.md)
- [Git Format Patch](reference/git-format-patch.md)
- [Git Fsck](reference/git-fsck.md)
- [Git Gc](reference/git-gc.md)
- [Git Get Tar Commit Id](reference/git-get-tar-commit-id.md)
- [Git Grep](reference/git-grep.md)
- [Git Gui](reference/git-gui.md)
- [Git Hash Object](reference/git-hash-object.md)
- [Git Help](reference/git-help.md)
- [Git Hook](reference/git-hook.md)
- [Git Http Backend](reference/git-http-backend.md)
- [Git Http Fetch](reference/git-http-fetch.md)
- [Git Http Push](reference/git-http-push.md)
- [Git Imap Send](reference/git-imap-send.md)
- [Git Index Pack](reference/git-index-pack.md)
- [Git Init](reference/git-init.md)
- [Git Instaweb](reference/git-instaweb.md)
- [Git Interpret Trailers](reference/git-interpret-trailers.md)
- [Git Last Modified](reference/git-last-modified.md)
- [Git Log](reference/git-log.md)
- [Git Ls Files](reference/git-ls-files.md)
- [Git Ls Remote](reference/git-ls-remote.md)
- [Git Ls Tree](reference/git-ls-tree.md)
- [Git Mailinfo](reference/git-mailinfo.md)
- [Git Mailsplit](reference/git-mailsplit.md)
- [Git Maintenance](reference/git-maintenance.md)
- [Git Merge Base](reference/git-merge-base.md)
- [Git Merge File](reference/git-merge-file.md)
- [Git Merge Index](reference/git-merge-index.md)
- [Git Merge One File](reference/git-merge-one-file.md)
- [Git Merge Tree](reference/git-merge-tree.md)
- [Git Merge](reference/git-merge.md)
- [Git Mergetool](reference/git-mergetool.md)
- [Git Mktag](reference/git-mktag.md)
- [Git Mktree](reference/git-mktree.md)
- [Git Multi Pack Index](reference/git-multi-pack-index.md)
- [Git Mv](reference/git-mv.md)
- [Git Name Rev](reference/git-name-rev.md)
- [Git Notes](reference/git-notes.md)
- [Git P4](reference/git-p4.md)
- [Git Pack Objects](reference/git-pack-objects.md)
- [Git Pack Redundant](reference/git-pack-redundant.md)
- [Git Pack Refs](reference/git-pack-refs.md)
- [Git Patch Id](reference/git-patch-id.md)
- [Git Prune Packed](reference/git-prune-packed.md)
- [Git Prune](reference/git-prune.md)
- [Git Pull](reference/git-pull.md)
- [Git Push](reference/git-push.md)
- [Git Quiltimport](reference/git-quiltimport.md)
- [Git Range Diff](reference/git-range-diff.md)
- [Git Read Tree](reference/git-read-tree.md)
- [Git Rebase](reference/git-rebase.md)
- [Git Receive Pack](reference/git-receive-pack.md)
- [Git Reflog](reference/git-reflog.md)
- [Git Refs](reference/git-refs.md)
- [Git Remote](reference/git-remote.md)
- [Git Repack](reference/git-repack.md)
- [Git Replace](reference/git-replace.md)
- [Git Replay](reference/git-replay.md)
- [Git Repo](reference/git-repo.md)
- [Git Request Pull](reference/git-request-pull.md)
- [Git Rerere](reference/git-rerere.md)
- [Git Reset](reference/git-reset.md)
- [Git Restore](reference/git-restore.md)
- [Git Rev List](reference/git-rev-list.md)
- [Git Rev Parse](reference/git-rev-parse.md)
- [Git Revert](reference/git-revert.md)
- [Git Rm](reference/git-rm.md)
- [Git Send Email](reference/git-send-email.md)
- [Git Send Pack](reference/git-send-pack.md)
- [Git Sh I18N](reference/git-sh-i18n.md)
- [Git Sh Setup](reference/git-sh-setup.md)
- [Git Shell](reference/git-shell.md)
- [Git Shortlog](reference/git-shortlog.md)
- [Git Show Branch](reference/git-show-branch.md)
- [Git Show Index](reference/git-show-index.md)
- [Git Show Ref](reference/git-show-ref.md)
- [Git Show](reference/git-show.md)
- [Git Sparse Checkout](reference/git-sparse-checkout.md)
- [Git Stash](reference/git-stash.md)
- [Git Status](reference/git-status.md)
- [Git Stripspace](reference/git-stripspace.md)
- [Git Submodule](reference/git-submodule.md)
- [Git Svn](reference/git-svn.md)
- [Git Switch](reference/git-switch.md)
- [Git Symbolic Ref](reference/git-symbolic-ref.md)
- [Git Tag](reference/git-tag.md)
- [Git Unpack File](reference/git-unpack-file.md)
- [Git Unpack Objects](reference/git-unpack-objects.md)
- [Git Update Index](reference/git-update-index.md)
- [Git Update Ref](reference/git-update-ref.md)
- [Git Update Server Info](reference/git-update-server-info.md)
- [Git Upload Archive](reference/git-upload-archive.md)
- [Git Upload Pack](reference/git-upload-pack.md)
- [Git Var](reference/git-var.md)
- [Git Verify Commit](reference/git-verify-commit.md)
- [Git Verify Pack](reference/git-verify-pack.md)
- [Git Verify Tag](reference/git-verify-tag.md)
- [Git Version](reference/git-version.md)
- [Git Whatchanged](reference/git-whatchanged.md)
- [Git Worktree](reference/git-worktree.md)
- [Git Write Tree](reference/git-write-tree.md)
- [Git](reference/git.md)
- [Git 2.0.5](reference/git_2.0.5.md)
- [Git 2.1.4](reference/git_2.1.4.md)
- [Git 2.10.5](reference/git_2.10.5.md)
- [Git 2.11.4](reference/git_2.11.4.md)
- [Git 2.12.5](reference/git_2.12.5.md)
- [Git 2.14.6](reference/git_2.14.6.md)
- [Git 2.15.4](reference/git_2.15.4.md)
- [Git 2.16.6](reference/git_2.16.6.md)
- [Git 2.17.0](reference/git_2.17.0.md)
- [Git 2.18.0](reference/git_2.18.0.md)
- [Git 2.19.0](reference/git_2.19.0.md)
- [Git 2.19.2](reference/git_2.19.2.md)
- [Git 2.2.3](reference/git_2.2.3.md)
- [Git 2.20.0](reference/git_2.20.0.md)
- [Git 2.22.0](reference/git_2.22.0.md)
- [Git 2.22.1](reference/git_2.22.1.md)
- [Git 2.23.0](reference/git_2.23.0.md)
- [Git 2.25.0](reference/git_2.25.0.md)
- [Git 2.25.1](reference/git_2.25.1.md)
- [Git 2.26.0](reference/git_2.26.0.md)
- [Git 2.27.0](reference/git_2.27.0.md)
- [Git 2.28.0](reference/git_2.28.0.md)
- [Git 2.29.0](reference/git_2.29.0.md)
- [Git 2.3.10](reference/git_2.3.10.md)
- [Git 2.30.0](reference/git_2.30.0.md)
- [Git 2.31.0](reference/git_2.31.0.md)
- [Git 2.32.0](reference/git_2.32.0.md)
- [Git 2.33.1](reference/git_2.33.1.md)
- [Git 2.33.2](reference/git_2.33.2.md)
- [Git 2.34.0](reference/git_2.34.0.md)
- [Git 2.35.0](reference/git_2.35.0.md)
- [Git 2.36.0](reference/git_2.36.0.md)
- [Git 2.37.0](reference/git_2.37.0.md)
- [Git 2.37.2](reference/git_2.37.2.md)
- [Git 2.38.0](reference/git_2.38.0.md)
- [Git 2.38.2](reference/git_2.38.2.md)
- [Git 2.39.0](reference/git_2.39.0.md)
- [Git 2.39.4](reference/git_2.39.4.md)
- [Git 2.4.12](reference/git_2.4.12.md)
- [Git 2.40.2](reference/git_2.40.2.md)
- [Git 2.41.0](reference/git_2.41.0.md)
- [Git 2.41.1](reference/git_2.41.1.md)
- [Git 2.42.0](reference/git_2.42.0.md)
- [Git 2.42.1](reference/git_2.42.1.md)
- [Git 2.42.2](reference/git_2.42.2.md)
- [Git 2.43.0](reference/git_2.43.0.md)
- [Git 2.43.1](reference/git_2.43.1.md)
- [Git 2.43.4](reference/git_2.43.4.md)
- [Git 2.44.0](reference/git_2.44.0.md)
- [Git 2.44.1](reference/git_2.44.1.md)
- [Git 2.45.0](reference/git_2.45.0.md)
- [Git 2.45.1](reference/git_2.45.1.md)
- [Git 2.46.0](reference/git_2.46.0.md)
- [Git 2.47.0](reference/git_2.47.0.md)
- [Git 2.48.0](reference/git_2.48.0.md)
- [Git 2.49.0](reference/git_2.49.0.md)
- [Git 2.5.6](reference/git_2.5.6.md)
- [Git 2.50.0](reference/git_2.50.0.md)
- [Git 2.51.1](reference/git_2.51.1.md)
- [Git 2.52.0](reference/git_2.52.0.md)
- [Git 2.53.0](reference/git_2.53.0.md)
- [Git 2.6.7](reference/git_2.6.7.md)
- [Git 2.7.6](reference/git_2.7.6.md)
- [Git 2.8.6](reference/git_2.8.6.md)
- [Git 2.9.5](reference/git_2.9.5.md)
- [Git De](reference/git_de.md)
- [Git Es](reference/git_es.md)
- [Git Fr](reference/git_fr.md)
- [Git Pt Br](reference/git_pt_BR.md)
- [Git Sv](reference/git_sv.md)
- [Git Uk](reference/git_uk.md)
- [Git Zh Hans Cn](reference/git_zh_HANS-CN.md)
- [Gitattributes](reference/gitattributes.md)
- [Gitcli](reference/gitcli.md)
- [Gitcore Tutorial](reference/gitcore-tutorial.md)
- [Gitcredentials](reference/gitcredentials.md)
- [Gitcvs Migration](reference/gitcvs-migration.md)
- [Gitdiffcore](reference/gitdiffcore.md)
- [Giteveryday](reference/giteveryday.md)
- [Gitfaq](reference/gitfaq.md)
- [Gitformat Bundle](reference/gitformat-bundle.md)
- [Gitformat Chunk](reference/gitformat-chunk.md)
- [Gitformat Commit Graph](reference/gitformat-commit-graph.md)
- [Gitformat Index](reference/gitformat-index.md)
- [Gitformat Pack](reference/gitformat-pack.md)
- [Gitformat Signature](reference/gitformat-signature.md)
- [Gitglossary](reference/gitglossary.md)
- [Githooks](reference/githooks.md)
- [Gitignore](reference/gitignore.md)
- [Gitk](reference/gitk.md)
- [Gitmailmap](reference/gitmailmap.md)
- [Gitmodules](reference/gitmodules.md)
- [Gitnamespaces](reference/gitnamespaces.md)
- [Gitprotocol Capabilities](reference/gitprotocol-capabilities.md)
- [Gitprotocol Common](reference/gitprotocol-common.md)
- [Gitprotocol Http](reference/gitprotocol-http.md)
- [Gitprotocol Pack](reference/gitprotocol-pack.md)
- [Gitprotocol V2](reference/gitprotocol-v2.md)
- [Gitremote Helpers](reference/gitremote-helpers.md)
- [Gitrepository Layout](reference/gitrepository-layout.md)
- [Gitrevisions](reference/gitrevisions.md)
- [Gitsubmodules](reference/gitsubmodules.md)
- [Gittutorial 2](reference/gittutorial-2.md)
- [Gittutorial](reference/gittutorial.md)
- [Gitweb](reference/gitweb.md)
- [Gitworkflows](reference/gitworkflows.md)
- [Howto Index](reference/howto-index.md)
- [Index](reference/index.md)
- [Install](reference/install_linux.md)
- [Learn](reference/learn.md)
- [Scalar](reference/scalar.md)
- [Git and Software Freedom Conservancy](reference/sfc.md)
- [About git-scm.com](reference/site.md)
- [Tools](reference/tools.md)
- [Command Line Tools](reference/tools_command-line.md)
- [GUI Clients](reference/tools_guis.md)
- [Git Hosting](reference/tools_hosting.md)
- [User Manual](reference/user-manual.md)
- [Videos](reference/videos.md)

### 🤖 Agent Usage Guide

- When the user asks anything about **Git Cli Docs**, consult the reference files.
- Prefer exact quotes and direct links to the relevant file/section.
- The hierarchical TOC above makes navigation fast and intuitive.
- All images and assets are preserved so links work perfectly.

### systems-manager-cron-management

**Description:** A skill for managing scheduled tasks using cron on Linux systems.

## Cron Job Management Skill

This skill allows the agent to schedule, list, and remove cron jobs on Linux systems.

### Tools

#### `list_cron_jobs`
Lists all cron jobs for the current user (or a specified user if running as root).

**Usage:**
```python
## List current user's cron jobs
list_cron_jobs()

## List specific user's cron jobs (requires root)
list_cron_jobs(user="username")
```

#### `add_cron_job`
Adds a new cron job.

**Parameters:**
- `schedule`: The cron schedule expression (e.g., `* * * * *`).
- `command`: The command to execute.
- `user`: (Optional) The user to add the cron job for.

**Best Practices:**
- Always include a comment in the command to make it easier to identify and remove later.
- Use absolute paths for commands and files.

**Example:**
```python
## Run a backup every day at 3 AM
add_cron_job(schedule="0 3 * * *", command="/usr/local/bin/backup.sh # daily-backup")
```

#### `remove_cron_job`
Removes cron jobs matching a specific pattern.

**Parameters:**
- `pattern`: A string to match against the cron job line. AND this pattern will be used to remove the job.
- `user`: (Optional) The user to remove the cron job for.

**Example:**
```python
## Remove the daily backup job
remove_cron_job(pattern="daily-backup")
```

### Common Schedules
- `* * * * *` - Every minute
- `0 * * * *` - Every hour
- `0 0 * * *` - Every day at midnight
- `0 0 * * 0` - Every Sunday at midnight
- `*/5 * * * *` - Every 5 minutes

### Heartbeat Example
To create a heartbeat that logs a message every minute:
```python
add_cron_job(schedule="* * * * *", command="echo 'Heartbeat' >> /tmp/heartbeat.log # agent-heartbeat")
```

### systems-manager-disk-management

**Description:** Systems Manager Disk Management capabilities for A2A Agent.

#### Overview
This skill provides access to disk and filesystem management operations.

#### Capabilities
- **list_disks**: Lists all disk partitions with mount points and usage statistics.
- **get_disk_usage**: Gets disk usage statistics for a specific path.
- **get_disk_space_report**: Gets a report of the largest directories under a path.

#### Common Tools
- `list_disks`: Lists all disk partitions with mount points and usage statistics.
- `get_disk_usage`: Gets disk usage statistics for a specific path.
- `get_disk_space_report`: Gets a report of the largest directories under a path.

#### Common Prompts
- "List all disk management information"
- "Lists all disk partitions with mount points and usage statistics"
- "Gets disk usage statistics for a specific path"
- "Gets a report of the largest directories under a path"

#### MCP Tags
- `disk_management`

### systems-manager-filesystem

**Description:** Systems Manager Filesystem capabilities for A2A Agent.

#### Overview
This skill provides access to filesystem operations.

#### Capabilities
- **list_files**: Lists files and directories in a path.
- **search_files**: Searches for files matching a pattern.
- **grep_files**: Searches for text content inside files (like grep).
- **manage_file**: Creates, updates, deletes, or reads a file.

### systems-manager-firewall-management

**Description:** Systems Manager Firewall Management capabilities for A2A Agent.

#### Overview
This skill provides access to firewall management operations (ufw/firewalld/iptables on Linux, netsh on Windows).

#### Capabilities
- **get_firewall_status**: Gets the current firewall status.
- **list_firewall_rules**: Lists all firewall rules.
- **add_firewall_rule**: Adds a firewall rule using the detected firewall tool.
- **remove_firewall_rule**: Removes a firewall rule using the detected firewall tool.

#### Common Tools
- `get_firewall_status`: Gets the current firewall status.
- `list_firewall_rules`: Lists all firewall rules.
- `add_firewall_rule`: Adds a firewall rule using the detected firewall tool.
- `remove_firewall_rule`: Removes a firewall rule using the detected firewall tool.

#### Common Prompts
- "List all firewall management information"
- "Gets the current firewall status"
- "Lists all firewall rules"
- "Adds a firewall rule using the detected firewall tool"
- "Removes a firewall rule using the detected firewall tool"

#### MCP Tags
- `firewall_management`

### systems-manager-linux

**Description:** Systems Manager Linux capabilities for A2A Agent.

#### Overview
This skill provides access to linux operations.

#### Capabilities
- **add_repository**: Adds an upstream repository to the package manager repository list (Linux only).
- **install_local_package**: Installs a local Linux package file using the appropriate tool (dpkg/rpm/dnf/zypper/pacman). (Linux only)
- **run_command**: Runs a command on the host. Can run elevated for administrator or root privileges.

#### Common Tools
- `add_repository`: Adds an upstream repository to the package manager repository list (Linux only).
- `install_local_package`: Installs a local Linux package file using the appropriate tool (dpkg/rpm/dnf/zypper/pacman). (Linux only)
- `run_command`: Runs a command on the host. Can run elevated for administrator or root privileges.

#### Usage Rules
- Use these tools when the user requests actions related to **linux**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please add repository"
- "Please install local package"
- "Please run command"

### systems-manager-log-management

**Description:** Systems Manager Log Management capabilities for A2A Agent.

#### Overview
This skill provides access to system log viewing operations.

#### Capabilities
- **get_system_logs**: Gets system logs from journalctl (Linux) or Event Log (Windows).
- **tail_log_file**: Reads the last N lines of a log file.

#### Common Tools
- `get_system_logs`: Gets system logs from journalctl (Linux) or Event Log (Windows).
- `tail_log_file`: Reads the last N lines of a log file.

#### Common Prompts
- "List all log management information"
- "Gets system logs from journalctl (Linux) or Event Log (Windows)"
- "Reads the last N lines of a log file"

#### MCP Tags
- `log_management`

### systems-manager-network-management

**Description:** Systems Manager Network Management capabilities for A2A Agent.

#### Overview
This skill provides access to network diagnostic operations.

#### Capabilities
- **list_network_interfaces**: Lists all network interfaces with IP addresses, speed, and MTU.
- **list_open_ports**: Lists all open/listening network ports with associated PIDs.
- **ping_host**: Pings a host and returns the results.
- **dns_lookup**: Performs a DNS lookup for a hostname and returns resolved IP addresses.

#### Common Tools
- `list_network_interfaces`: Lists all network interfaces with IP addresses, speed, and MTU.
- `list_open_ports`: Lists all open/listening network ports with associated PIDs.
- `ping_host`: Pings a host and returns the results.
- `dns_lookup`: Performs a DNS lookup for a hostname and returns resolved IP addresses.

#### Common Prompts
- "List all network management information"
- "Lists all network interfaces with IP addresses, speed, and MTU"
- "Lists all open/listening network ports with associated PIDs"
- "Pings a host and returns the results"
- "Performs a DNS lookup for a hostname and returns resolved IP addresses"

#### MCP Tags
- `network_management`

### systems-manager-node-management

**Description:** Systems Manager Node Management capabilities for A2A Agent.

#### Overview
This skill provides access to Node.js environment management.

#### Capabilities
- **install_nvm**: Installs NVM (Node Version Manager).
- **install_node**: Installs a Node.js version using NVM.
- **use_node**: Switches the active Node.js version using NVM.

### systems-manager-process-management

**Description:** Systems Manager Process Management capabilities for A2A Agent.

#### Overview
This skill provides access to process management operations for monitoring and controlling processes.

#### Capabilities
- **list_processes**: Lists all running processes with PID, name, CPU%, memory%, and status.
- **get_process_info**: Gets detailed information about a specific process by PID.
- **kill_process**: Kills a process by PID. Default signal is SIGTERM (15), use 9 for SIGKILL.

#### Common Tools
- `list_processes`: Lists all running processes with PID, name, CPU%, memory%, and status.
- `get_process_info`: Gets detailed information about a specific process by PID.
- `kill_process`: Kills a process by PID. Default signal is SIGTERM (15), use 9 for SIGKILL.

#### Common Prompts
- "List all process management information"
- "Lists all running processes with PID, name, CPU%, memory%, and status"
- "Gets detailed information about a specific process by PID"
- "Kills a process by PID. Default signal is SIGTERM (15), use 9 for SIGKILL"

#### MCP Tags
- `process_management`

### systems-manager-python-management

**Description:** Systems Manager Python Management capabilities for A2A Agent.

#### Overview
This skill provides access to Python environment management using uv.

#### Capabilities
- **install_uv**: Installs uv (Python package manager).
- **create_python_venv**: Creates a Python virtual environment using uv.
- **install_python_package_uv**: Installs a Python package using uv pip.

### systems-manager-service-management

**Description:** Systems Manager Service Management capabilities for A2A Agent.

#### Overview
This skill provides access to service management operations for controlling system services.

#### Capabilities
- **list_services**: Lists all system services with their current status.
- **get_service_status**: Gets the status of a specific system service.
- **start_service**: Starts a system service.
- **stop_service**: Stops a system service.
- **restart_service**: Restarts a system service.
- **enable_service**: Enables a system service to start at boot.
- **disable_service**: Disables a system service from starting at boot.

#### Common Tools
- `list_services`: Lists all system services with their current status.
- `get_service_status`: Gets the status of a specific system service.
- `start_service`: Starts a system service.
- `stop_service`: Stops a system service.
- `restart_service`: Restarts a system service.
- `enable_service`: Enables a system service to start at boot.
- `disable_service`: Disables a system service from starting at boot.

#### Common Prompts
- "List all service management information"
- "Lists all system services with their current status"
- "Gets the status of a specific system service"
- "Starts a system service"
- "Stops a system service"
- "Restarts a system service"
- "Enables a system service to start at boot"
- "Disables a system service from starting at boot"

#### MCP Tags
- `service_management`

### systems-manager-shell-management

**Description:** Systems Manager Shell Management capabilities for A2A Agent.

#### Overview
This skill provides access to shell profile management.

#### Capabilities
- **add_shell_alias**: Adds an alias to the user's shell profile.

### systems-manager-ssh-management

**Description:** Systems Manager SSH Key Management capabilities for A2A Agent.

#### Overview
This skill provides access to SSH key management operations.

#### Capabilities
- **list_ssh_keys**: Lists all SSH keys in the user's ~/.ssh directory.
- **generate_ssh_key**: Generates a new SSH key pair.
- **add_authorized_key**: Adds a public key to the authorized_keys file.

#### Common Tools
- `list_ssh_keys`: Lists all SSH keys in the user's ~/.ssh directory.
- `generate_ssh_key`: Generates a new SSH key pair.
- `add_authorized_key`: Adds a public key to the authorized_keys file.

#### Common Prompts
- "List all ssh management information"
- "Lists all SSH keys in the user's ~/.ssh directory"
- "Generates a new SSH key pair"
- "Adds a public key to the authorized_keys file"

#### MCP Tags
- `ssh_management`

### systems-manager-system-management

**Description:** Systems Manager System Management capabilities for A2A Agent.

#### Overview
This skill provides access to system_management operations.

#### Capabilities
- **install_applications**: Installs applications using the native package manager with Snap fallback.
- **update**: Updates the system and applications.
- **clean**: Cleans system resources (e.g., trash/recycle bin).
- **optimize**: Optimizes system resources (e.g., autoremove, defrag).
- **install_python_modules**: Installs Python modules using pip.
- **get_os_statistics**: Gets OS information (platform, version, architecture).
- **get_hardware_statistics**: Gets hardware statistics (CPU, memory, disk, network).
- **search_package**: Searches for packages in the system package manager repositories.
- **get_package_info**: Gets detailed information about a specific package.
- **list_installed_packages**: Lists all installed packages on the system.
- **list_upgradable_packages**: Lists all packages that have updates available.
- **system_health_check**: Performs a comprehensive system health check including CPU, memory, disk, swap, and top processes.
- **get_uptime**: Gets system uptime and boot time.
- **list_env_vars**: Lists all environment variables on the system.
- **get_env_var**: Gets the value of a specific environment variable.
- **clean_temp_files**: Cleans temporary files from system temp directories.
- **clean_package_cache**: Cleans the package manager cache to free disk space.

#### Common Tools
- `install_applications`: Installs applications using the native package manager with Snap fallback.
- `update`: Updates the system and applications.
- `clean`: Cleans system resources (e.g., trash/recycle bin).
- `optimize`: Optimizes system resources (e.g., autoremove, defrag).
- `install_python_modules`: Installs Python modules using pip.
- `get_os_statistics`: Gets OS information (platform, version, architecture).
- `get_hardware_statistics`: Gets hardware statistics (CPU, memory, disk, network).
- `search_package`: Searches for packages in the system package manager repositories.
- `get_package_info`: Gets detailed information about a specific package.
- `list_installed_packages`: Lists all installed packages on the system.
- `list_upgradable_packages`: Lists all packages that have updates available.
- `system_health_check`: Performs a comprehensive system health check.
- `get_uptime`: Gets system uptime and boot time.
- `list_env_vars`: Lists all environment variables.
- `get_env_var`: Gets a specific environment variable.
- `clean_temp_files`: Cleans temporary files from system temp directories.
- `clean_package_cache`: Cleans the package manager cache.

#### Common Prompts
- "Install these applications: vim, git, curl"
- "Update all system packages"
- "Clean up system resources"
- "Optimize the system"
- "Install python modules: requests, flask"
- "What operating system is this?"
- "Show hardware statistics"
- "Search for package nginx"
- "Show info for package git"
- "List all installed packages"
- "What packages need updating?"
- "Run a system health check"
- "How long has the system been running?"
- "Show all environment variables"
- "What is the value of PATH?"
- "Clean temporary files"
- "Clean the package cache"

#### MCP Tags
- `system_management`

### systems-manager-user-management

**Description:** Systems Manager User Management capabilities for A2A Agent.

#### Overview
This skill provides access to user and group management operations.

#### Capabilities
- **list_users**: Lists all system users with UID, GID, home directory, and shell.
- **list_groups**: Lists all system groups with GID and members.

#### Common Tools
- `list_users`: Lists all system users with UID, GID, home directory, and shell.
- `list_groups`: Lists all system groups with GID and members.

#### Common Prompts
- "List all user management information"
- "Lists all system users with UID, GID, home directory, and shell"
- "Lists all system groups with GID and members"

#### MCP Tags
- `user_management`

### systems-manager-windows

**Description:** Systems Manager Windows capabilities for A2A Agent.

#### Overview
This skill provides access to windows operations.

#### Capabilities
- **list_windows_features**: Lists all Windows features and their status (Windows only).
- **enable_windows_features**: Enables specified Windows features (Windows only).
- **disable_windows_features**: Disables specified Windows features (Windows only).

#### Common Tools
- `list_windows_features`: Lists all Windows features and their status (Windows only).
- `enable_windows_features`: Enables specified Windows features (Windows only).
- `disable_windows_features`: Disables specified Windows features (Windows only).

#### Usage Rules
- Use these tools when the user requests actions related to **windows**.
- Always interpret the output of these tools to provide a concise summary to the user.

#### Example Prompts
- "Please disable windows features"
- "Please enable windows features"
- "Please list windows features"
