from typing import Any, Callable


def _script_name(deps: Any) -> str:
    try:
        return deps.Path(deps.__file__).name
    except Exception:
        return "main.py"


def _session_label(agent_id: str) -> str:
    return "main" if str(agent_id).strip().lower() == "main" else f"agent-{agent_id}"


def cmd_start(args, *, deps: Any):
    """Start an agent in tmux session."""
    check_tmux = deps.check_tmux
    resolve_agent = deps.resolve_agent
    list_all_agents = deps.list_all_agents
    get_agent_id = deps.get_agent_id
    session_exists = deps.session_exists
    get_session_info = deps.get_session_info
    normalize_path = deps._normalize_path
    get_repo_root = deps.get_repo_root
    resolve_launcher_command = deps.resolve_launcher_command
    get_provider_key = deps.get_provider_key
    snapshot_provider_sessions = deps._snapshot_provider_sessions
    get_session_restore_mode = deps.get_session_restore_mode
    get_session_restore_flag = deps.get_session_restore_flag
    load_provider_session_id = deps._load_provider_session_id
    provider_session_exists = deps._provider_session_exists
    apply_session_restore_args = deps._apply_session_restore_args
    build_system_prompt = deps.build_system_prompt
    get_system_prompt_mode = deps.get_system_prompt_mode
    get_system_prompt_flag = deps.get_system_prompt_flag
    get_system_prompt_key = deps.get_system_prompt_key
    get_agents_md_mode = deps.get_agents_md_mode
    get_mcp_config_mode = deps.get_mcp_config_mode
    get_mcp_config_flag = deps.get_mcp_config_flag
    build_mcp_config_json = deps.build_mcp_config_json
    build_start_command = deps.build_start_command
    write_system_prompt_file = deps.write_system_prompt_file
    start_session_with_layout = deps.start_session_with_layout
    start_session = deps.start_session
    wait_for_prompt = deps.wait_for_prompt
    inject_system_prompt = deps.inject_system_prompt
    wait_for_agent_ready = deps.wait_for_agent_ready
    save_provider_session_id = deps._save_provider_session_id
    find_new_provider_session_id_with_retry = (
        deps._find_new_provider_session_id_with_retry
    )
    Path = deps.Path
    shlex = deps.shlex
    json = deps.json

    if not check_tmux():
        print("❌ tmux is not installed. Install with: apt install tmux")
        return 1

    agent_config = resolve_agent(args.agent)
    if not agent_config:
        print(f"❌ Agent not found: {args.agent}")
        print("   Available agents:")
        all_agents = list_all_agents()
        for file_id, config in sorted(all_agents.items(), key=lambda item: item[0]):
            name = config.get("name") or file_id
            agent_id = get_agent_id(config)
            print(f"   - {file_id} ({name}) ({_session_label(agent_id)})")
        return 1

    agent_name = agent_config["name"]
    agent_id = get_agent_id(agent_config)
    agent_file_id = agent_config.get("file_id", args.agent)

    if not agent_config.get("enabled", True):
        agent_file_path = agent_config.get("_file_path", f"agents/{agent_file_id}.md")
        print(f"⚠️  Agent '{agent_name}' is disabled")
        print(f"   Config: {agent_file_path}")
        print("   To enable: Set 'enabled: true' in the agent config")
        return 1

    if session_exists(agent_id):
        session_info = get_session_info(agent_id) or {}
        session_name = session_info.get("session", _session_label(agent_id))
        if getattr(args, "restore", True):
            print(f"✅ Restored existing session for '{agent_name}'")
            print(f"   Session: {session_name}({agent_name})")
            if getattr(args, "working_dir", None):
                print("   Note: --working-dir is ignored when restoring")
            print()
            if session_info.get("mode") == "windows":
                group = session_name.split(":", 1)[0]
                print(f"Attach with: tmux attach -t {group}")
            else:
                print(f"Attach with: tmux attach -t {session_name}")
            print(f"Monitor with: python3 {_script_name(deps)} monitor {agent_file_id}")
            return 0

        print(f"⚠️  Agent '{agent_name}' is already running")
        print(f"   Session: {session_name}({agent_name})")
        print()
        print(f"   To stop first: python3 {_script_name(deps)} stop {agent_file_id}")
        if session_info.get("mode") == "windows":
            group = session_name.split(":", 1)[0]
            print(f"   Or attach directly: tmux attach -t {group}")
        else:
            print(f"   Or attach directly: tmux attach -t {session_name}")
        print(
            f"   Or restore (reuse existing): python3 {_script_name(deps)} start {agent_file_id} --restore"
        )
        return 1

    working_dir = args.working_dir or agent_config.get("working_directory")
    if not working_dir:
        print("❌ No working directory specified")
        return 1

    working_dir = normalize_path(working_dir)

    repo_root = get_repo_root()
    skills_dir = repo_root / ".agent" / "skills"

    launcher = resolve_launcher_command(agent_config.get("launcher", ""))
    launcher_args = list(agent_config.get("launcher_args", []) or [])

    provider_key = get_provider_key(launcher)
    did_provider_restore = False
    provider_before_sessions: set[str] = set()

    track_provider_session = provider_key in {
        "droid",
        "agent",
        "agent-cli",
        "codex",
        "opencode",
    }
    if provider_key == "droid" and "exec" in launcher_args:
        track_provider_session = False

    if track_provider_session:
        provider_before_sessions = snapshot_provider_sessions(provider_key, working_dir)

    if getattr(args, "restore", True) and track_provider_session:
        restore_mode = get_session_restore_mode(launcher)
        restore_flag = get_session_restore_flag(launcher)
        if restore_mode == "cli_optional_arg" and restore_flag:
            stored_session_id = load_provider_session_id(
                repo_root, provider_key, agent_id
            )
            if stored_session_id and provider_session_exists(
                provider_key, working_dir, stored_session_id
            ):
                launcher_args = apply_session_restore_args(
                    provider_key,
                    launcher,
                    launcher_args,
                    restore_flag,
                    stored_session_id,
                )
                did_provider_restore = True
            elif stored_session_id:
                print(
                    f"⚠️  Stored {provider_key} sessionId not found for cwd; starting fresh"
                )

    system_prompt = build_system_prompt(
        agent_config, repo_root=repo_root, skills_dir=skills_dir
    )
    system_prompt_mode = get_system_prompt_mode(launcher)
    system_prompt_flag = get_system_prompt_flag(launcher)
    system_prompt_key = get_system_prompt_key(launcher)

    if (
        system_prompt
        and not did_provider_restore
        and get_agents_md_mode(launcher) == "cwd"
    ):
        if (Path(working_dir) / "AGENTS.md").exists():
            print(
                "ℹ️  AGENTS.md found in working directory; skipping system prompt injection"
            )
            system_prompt = ""

    mcp_config_mode = get_mcp_config_mode(launcher)
    mcp_config_flag = get_mcp_config_flag(launcher)
    try:
        mcp_config_json = build_mcp_config_json(agent_config)
    except ValueError as e:
        print(f"❌ {e}")
        return 1

    use_cli_system_prompt = bool(
        system_prompt
        and not did_provider_restore
        and system_prompt_mode in {"cli_append", "cli_config_kv"}
        and system_prompt_flag
        and (system_prompt_mode != "cli_config_kv" or system_prompt_key)
    )
    command = build_start_command(working_dir, launcher, launcher_args)

    if use_cli_system_prompt:
        prompt_file = write_system_prompt_file(repo_root, agent_id, system_prompt)

        if system_prompt_mode == "cli_append":
            command = f'{command} {shlex.quote(system_prompt_flag)} "$(cat {shlex.quote(str(prompt_file))})"'
        elif system_prompt_mode == "cli_config_kv":
            toml_path = json.dumps(str(prompt_file))
            kv = f"{system_prompt_key}={toml_path}"
            command = f"{command} {shlex.quote(system_prompt_flag)} {shlex.quote(kv)}"

    if mcp_config_json and not did_provider_restore:
        if mcp_config_mode == "cli_json" and mcp_config_flag:
            command = f"{command} {shlex.quote(mcp_config_flag)} {shlex.quote(mcp_config_json)}"
        else:
            print(
                f"⚠️  MCP config present but not supported for launcher '{launcher}' - ignoring"
            )
    elif mcp_config_json and did_provider_restore:
        print("ℹ️  Provider session restored; skipping MCP config injection")

    tmux_config = agent_config.get("tmux") or {}
    if tmux_config and not isinstance(tmux_config, dict):
        print("❌ Invalid 'tmux' in agent config (expected a mapping)")
        return 1

    tmux_layout_spec = tmux_config.get("layout") if tmux_config else None
    tmux_target_path = tmux_config.get("target_pane") if tmux_config else None

    if tmux_layout_spec is None and tmux_target_path is not None:
        print("❌ tmux.target_pane requires tmux.layout")
        return 1

    if tmux_layout_spec is not None:
        try:
            start_session_with_layout(
                agent_id,
                command,
                layout_spec=tmux_layout_spec,
                target_path=tmux_target_path,
                session_layout=getattr(args, "tmux_layout", "sessions"),
            )
        except ValueError as e:
            print(f"❌ {e}")
            return 1
    else:
        if not start_session(
            agent_id, command, layout=getattr(args, "tmux_layout", "sessions")
        ):
            print(f"❌ Failed to start agent '{agent_name}'")
            return 1

    session_info = get_session_info(agent_id) or {}
    session_name = session_info.get("session", _session_label(agent_id))
    print(f"✅ Agent '{agent_name}' started")
    print(f"   Session: {session_name}({agent_name})")
    print(f"   Working Dir: {working_dir}")
    print()

    launcher = resolve_launcher_command(agent_config.get("launcher", ""))

    print("⏳ Waiting for CLI to be ready...")
    if not wait_for_prompt(agent_id, launcher, timeout=30):
        print("⚠️  Timeout waiting for CLI prompt")
        if not session_exists(agent_id):
            print("❌ Agent session exited during startup")
            return 1
        if use_cli_system_prompt:
            print(
                f"   Continuing: system prompt injected via {system_prompt_flag}; CLI may still be starting..."
            )
        else:
            if system_prompt:
                print("   System prompt not injected. Agent may still be starting...")
            return 1

    if system_prompt and not did_provider_restore:
        if use_cli_system_prompt:
            print(f"✅ CLI ready (system prompt injected via {system_prompt_flag})")
        else:
            if get_provider_key(launcher) == "codex":
                print(
                    "❌ Codex system prompt injection is configured as CLI-only (no tmux_paste fallback)"
                )
                return 1

            print("✅ CLI ready, injecting system prompt via tmux...")

            if not inject_system_prompt(agent_id, system_prompt):
                print("❌ Failed to inject system prompt")
                return 1

            skills = agent_config.get("skills", [])
            if skills:
                print(
                    f"   System prompt injected ({len(system_prompt)} chars, {len(skills)} skills)"
                )
            else:
                print(f"   System prompt injected ({len(system_prompt)} chars)")
    elif system_prompt and did_provider_restore:
        print("ℹ️  Provider session restored; skipping system prompt injection")
    else:
        print("ℹ️  No system prompt configured for this agent")

    if track_provider_session:
        if did_provider_restore:
            session_id = load_provider_session_id(repo_root, provider_key, agent_id)
            if session_id:
                save_provider_session_id(
                    repo_root,
                    provider_key,
                    agent_id,
                    session_id=session_id,
                    cwd=working_dir,
                )
        else:
            new_session_id = find_new_provider_session_id_with_retry(
                provider_key,
                working_dir,
                before_paths=provider_before_sessions,
                timeout_s=2.0,
            )
            if new_session_id:
                save_provider_session_id(
                    repo_root,
                    provider_key,
                    agent_id,
                    session_id=new_session_id,
                    cwd=working_dir,
                )

    print("⏳ Waiting for agent to be ready...")
    if wait_for_agent_ready(agent_id, launcher, timeout=45):
        print("✅ Agent is ready!")
    else:
        print("⚠️  Agent readiness timeout, but may still be processing...")

    if not session_exists(agent_id):
        print("❌ Agent session exited during startup")
        return 1

    print()
    print(f"Attach with: tmux attach -t {session_name}")
    print(f"Monitor with: python3 {_script_name(deps)} monitor {agent_file_id}")

    return 0


def cmd_stop(args, *, deps: Any):
    """Stop a running agent."""
    check_tmux = deps.check_tmux
    resolve_agent = deps.resolve_agent
    get_agent_id = deps.get_agent_id
    session_exists = deps.session_exists
    stop_session = deps.stop_session

    if not check_tmux():
        print("❌ tmux is not installed")
        return 1

    agent_config = resolve_agent(args.agent)
    if not agent_config:
        print(f"❌ Agent not found: {args.agent}")
        return 1

    agent_name = agent_config["name"]
    agent_id = get_agent_id(agent_config)

    if not session_exists(agent_id):
        print(f"⚠️  Agent '{agent_name}' is not running")
        return 1

    if not stop_session(agent_id):
        print(f"❌ Failed to stop agent '{agent_name}'")
        return 1

    session_name = _session_label(agent_id)
    print(f"✅ Agent '{agent_name}' stopped")
    print(f"   Session {session_name}({agent_name}) terminated")
    return 0


def cmd_monitor(args, *, deps: Any):
    """Monitor agent output."""
    check_tmux = deps.check_tmux
    resolve_agent = deps.resolve_agent
    get_agent_id = deps.get_agent_id
    capture_output = deps.capture_output
    time = deps.time

    if not check_tmux():
        print("❌ tmux is not installed")
        return 1

    agent_config = resolve_agent(args.agent)
    if not agent_config:
        print(f"❌ Agent not found: {args.agent}")
        return 1

    agent_name = agent_config["name"]
    agent_id = get_agent_id(agent_config)

    if args.follow:
        session_name = _session_label(agent_id)
        print(
            f"📺 Following output for {session_name}({agent_name}) (Ctrl+C to stop)..."
        )
        print()

        last_output = ""
        try:
            while True:
                output = capture_output(agent_id, args.lines)
                if output is None:
                    print(f"⚠️  Agent '{agent_name}' is not running")
                    return 1

                if output != last_output:
                    if last_output:
                        new_lines = output[len(last_output) :]
                        print(new_lines, end="")
                    else:
                        print(output, end="")
                    last_output = output

                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n⏹  Monitoring stopped")
    else:
        output = capture_output(agent_id, args.lines)
        if output is None:
            print(f"⚠️  Agent '{agent_name}' is not running")
            return 1

        session_name = _session_label(agent_id)
        print(f"📺 Last {args.lines} lines from {session_name}({agent_name}):")
        print("=" * 60)
        print(output)
        print("=" * 60)

    return 0


def cmd_send(args, *, deps: Any):
    """Send message to agent."""
    check_tmux = deps.check_tmux
    resolve_agent = deps.resolve_agent
    get_agent_id = deps.get_agent_id
    session_exists = deps.session_exists
    Path = deps.Path
    resolve_launcher_command = deps.resolve_launcher_command
    should_use_codex_file_pointer = deps._should_use_codex_file_pointer
    get_repo_root = deps.get_repo_root
    write_codex_message_file = deps.write_codex_message_file
    send_keys = deps.send_keys

    if not check_tmux():
        print("❌ tmux is not installed")
        return 1

    agent_config = resolve_agent(args.agent)
    if not agent_config:
        print(f"❌ Agent not found: {args.agent}")
        return 1

    agent_name = agent_config["name"]
    agent_id = get_agent_id(agent_config)

    if not session_exists(agent_id):
        print(f"⚠️  Agent '{agent_name}' is not running")
        print(
            f"   Start with: python3 {Path(deps.__file__).name} start {agent_config.get('file_id', agent_name)}"
        )
        return 1

    launcher = resolve_launcher_command(agent_config.get("launcher", ""))
    is_codex = "codex" in launcher.lower()

    outgoing_message = args.message
    if is_codex and should_use_codex_file_pointer(outgoing_message):
        repo_root = get_repo_root()
        message_file = write_codex_message_file(
            repo_root, agent_id, "send", outgoing_message
        )
        outgoing_message = (
            f"Read and execute the message from file: {message_file}\n"
            "After completing it, summarize key results."
        )
        print(f"ℹ️  Codex long message detected; using file pointer: {message_file}")

    if not send_keys(
        agent_id,
        outgoing_message,
        send_enter=args.send_enter,
        clear_input=is_codex,
        escape_first=is_codex,
        enter_via_key=is_codex,
    ):
        print(f"❌ Failed to send message to {agent_name}")
        return 1

    print(f"✅ Message sent to {agent_name}")
    if outgoing_message == args.message:
        print(f"   Message: {args.message}")
    else:
        print(f"   Original message length: {len(args.message)} chars")
    print()
    print(f"Monitor response: python3 {Path(deps.__file__).name} monitor {agent_name}")
    return 0


def cmd_assign(args, *, deps: Any, start_handler: Callable | None = None):
    """Assign task to agent."""
    check_tmux = deps.check_tmux
    resolve_agent = deps.resolve_agent
    get_agent_id = deps.get_agent_id
    session_exists = deps.session_exists
    argparse = deps.argparse
    time = deps.time
    resolve_launcher_command = deps.resolve_launcher_command
    should_use_codex_file_pointer = deps._should_use_codex_file_pointer
    get_repo_root = deps.get_repo_root
    write_codex_message_file = deps.write_codex_message_file
    send_keys = deps.send_keys
    Path = deps.Path
    sys = deps.sys

    if start_handler is None:
        start_handler = deps.cmd_start

    if not check_tmux():
        print("❌ tmux is not installed")
        return 1

    agent_config = resolve_agent(args.agent)
    if not agent_config:
        print(f"❌ Agent not found: {args.agent}")
        return 1

    agent_name = agent_config["name"]
    agent_id = get_agent_id(agent_config)

    if args.task_file:
        try:
            with open(args.task_file, "r") as f:
                task = f.read()
        except FileNotFoundError:
            print(f"❌ Task file not found: {args.task_file}")
            return 1
    else:
        task = sys.stdin.read()

    if not task.strip():
        print("❌ Task cannot be empty")
        print("   Provide task via stdin or --task-file")
        return 1

    if not session_exists(agent_id):
        print(f"⚠️  Agent {agent_name} is not running. Starting...")

        start_args = argparse.Namespace(
            agent=args.agent,
            working_dir=None,
        )

        if start_handler(start_args) != 0:
            return 1

        print()
        time.sleep(3)

    launcher = resolve_launcher_command(agent_config.get("launcher", ""))
    is_codex = "codex" in launcher.lower()

    task_message = f"# Task Assignment\n\n{task}"
    if is_codex and should_use_codex_file_pointer(task_message):
        repo_root = get_repo_root()
        task_file = write_codex_message_file(
            repo_root, agent_id, "assign", task_message
        )
        task_message = (
            f"Task assignment received. Read and follow instructions from file: {task_file}\n"
            "Execute the task now and report progress/blocks."
        )
        print(f"ℹ️  Codex long assignment detected; using file pointer: {task_file}")

    if not send_keys(
        agent_id,
        task_message,
        send_enter=True,
        clear_input=is_codex,
        escape_first=is_codex,
        enter_via_key=is_codex,
    ):
        print(f"❌ Failed to assign task to {agent_name}")
        return 1

    print(f"✅ Task assigned to {agent_name}")
    print()
    print(
        f"Monitor progress: python3 {Path(deps.__file__).name} monitor {agent_name} --follow"
    )
    return 0
