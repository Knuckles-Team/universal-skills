import argparse
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import agent_config  # noqa: E402
import tmux_helper  # noqa: E402
from commands.lifecycle import cmd_assign, cmd_monitor, cmd_send  # noqa: E402


class MainAgentConfigTests(unittest.TestCase):
    def test_resolve_agent_main_returns_reserved_config(self):
        config = agent_config.resolve_agent("main", agents_dir=Path("/tmp/not-needed"))

        self.assertIsNotNone(config)
        self.assertEqual(config.get("name"), "main")
        self.assertEqual(config.get("file_id"), "main")
        self.assertTrue(bool(config.get("working_directory")))
        self.assertTrue(bool(config.get("launcher")))

    def test_list_all_agents_includes_main_without_agents_dir(self):
        temp_root = Path(tempfile.mkdtemp(prefix="agent-manager-main-agent-"))
        agents_dir = temp_root / "agents"

        agents = agent_config.list_all_agents(agents_dir=agents_dir)

        self.assertIn("main", agents)
        self.assertEqual(agents["main"].get("name"), "main")

    @patch.dict(os.environ, {"AGENT_MANAGER_MAIN_LAUNCHER": "custom-launcher"})
    def test_main_launcher_env_override(self):
        config = agent_config.resolve_agent("main", agents_dir=Path("/tmp/not-needed"))
        self.assertEqual(config.get("launcher"), "custom-launcher")


class MainAgentTmuxNamingTests(unittest.TestCase):
    def test_session_name_for_main_has_no_prefix(self):
        self.assertEqual(tmux_helper._session_name_for_agent("main"), "main")
        self.assertEqual(tmux_helper._window_name_for_agent("main"), "main")
        self.assertEqual(
            tmux_helper._session_name_for_agent("emp-0001"), "agent-emp-0001"
        )


class MainAgentLifecycleTests(unittest.TestCase):
    def test_send_main_routes_message_to_main_agent_id(self):
        calls = []

        deps = SimpleNamespace(
            __file__="main.py",
            check_tmux=lambda: True,
            resolve_agent=lambda _agent: {
                "name": "main",
                "file_id": "main",
                "launcher": "droid",
            },
            get_agent_id=lambda config: config.get("file_id", "").lower(),
            session_exists=lambda agent_id: agent_id == "main",
            Path=Path,
            resolve_launcher_command=lambda launcher: launcher,
            _should_use_codex_file_pointer=lambda _msg: False,
            get_repo_root=lambda: Path("/tmp"),
            write_codex_message_file=lambda *_args, **_kwargs: Path("/tmp/message.md"),
            send_keys=lambda agent_id, message, **kwargs: calls.append(
                (agent_id, message, kwargs)
            )
            or True,
        )

        output = io.StringIO()
        with redirect_stdout(output):
            rc = cmd_send(
                argparse.Namespace(agent="main", message="hello-main", send_enter=True),
                deps=deps,
            )

        self.assertEqual(rc, 0)
        self.assertEqual(calls[0][0], "main")
        self.assertIn("Message sent to main", output.getvalue())

    def test_assign_main_reads_stdin_and_sends(self):
        calls = []

        deps = SimpleNamespace(
            __file__="main.py",
            check_tmux=lambda: True,
            resolve_agent=lambda _agent: {
                "name": "main",
                "file_id": "main",
                "launcher": "droid",
            },
            get_agent_id=lambda config: config.get("file_id", "").lower(),
            session_exists=lambda agent_id: agent_id == "main",
            argparse=argparse,
            time=SimpleNamespace(sleep=lambda _s: None),
            resolve_launcher_command=lambda launcher: launcher,
            _should_use_codex_file_pointer=lambda _msg: False,
            get_repo_root=lambda: Path("/tmp"),
            write_codex_message_file=lambda *_args, **_kwargs: Path("/tmp/assign.md"),
            send_keys=lambda agent_id, message, **kwargs: calls.append(
                (agent_id, message, kwargs)
            )
            or True,
            Path=Path,
            sys=SimpleNamespace(stdin=io.StringIO("run health check")),
        )

        output = io.StringIO()
        with redirect_stdout(output):
            rc = cmd_assign(
                argparse.Namespace(agent="main", task_file=None),
                deps=deps,
                start_handler=lambda _args: 0,
            )

        self.assertEqual(rc, 0)
        self.assertEqual(calls[0][0], "main")
        self.assertIn("# Task Assignment", calls[0][1])
        self.assertIn("Task assigned to main", output.getvalue())

    def test_monitor_main_shows_main_session_label(self):
        deps = SimpleNamespace(
            check_tmux=lambda: True,
            resolve_agent=lambda _agent: {"name": "main", "file_id": "main"},
            get_agent_id=lambda config: config.get("file_id", "").lower(),
            capture_output=lambda _agent_id, _lines: "line-1\nline-2\n",
            time=SimpleNamespace(sleep=lambda _s: None),
        )

        output = io.StringIO()
        with redirect_stdout(output):
            rc = cmd_monitor(
                argparse.Namespace(agent="main", follow=False, lines=20),
                deps=deps,
            )

        text = output.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("Last 20 lines from main(main)", text)
        self.assertNotIn("agent-main", text)


if __name__ == "__main__":
    unittest.main()
