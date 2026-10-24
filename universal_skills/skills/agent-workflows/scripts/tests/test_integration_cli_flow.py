import argparse
import io
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import main  # noqa: E402


class _FakeRuntime:
    def __init__(self):
        self.running = False
        self.start_commands: list[str] = []
        self.sent_messages: list[dict] = []
        self.monitor_output = "agent output line\n"

    def session_exists(self, _agent_id: str) -> bool:
        return self.running

    def start_session(
        self, _agent_id: str, command: str, layout: str = "sessions"
    ) -> bool:
        self.running = True
        self.start_commands.append(f"{layout}:{command}")
        return True

    def start_session_with_layout(
        self, _agent_id: str, command: str, **_kwargs
    ) -> bool:
        self.running = True
        self.start_commands.append(f"layout:{command}")
        return True

    def stop_session(self, _agent_id: str) -> bool:
        if not self.running:
            return False
        self.running = False
        return True

    def get_session_info(self, agent_id: str):
        if not self.running:
            return None
        return {"session": f"agent-{agent_id}", "mode": "sessions"}

    def capture_output(self, _agent_id: str, _lines: int = 100, **_kwargs):
        if not self.running:
            return None
        return self.monitor_output

    def send_keys(self, agent_id: str, message: str, **kwargs) -> bool:
        self.sent_messages.append(
            {"agent_id": agent_id, "message": message, "kwargs": kwargs}
        )
        return True


class CliIntegrationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_root = Path(tempfile.mkdtemp(prefix="agent-manager-integration-"))
        self.work_dir = self.temp_root / "workspace"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.agent_config = {
            "name": "dev",
            "file_id": "EMP_0001",
            "working_directory": str(self.work_dir),
            "launcher": "codex",
            "launcher_args": ["--model=gpt-5.2"],
            "heartbeat": {"enabled": True, "session_mode": "restore"},
            "enabled": True,
        }

    def _patch_common(self, stack: ExitStack, runtime: _FakeRuntime):
        stack.enter_context(patch("main.time.sleep", return_value=None))
        stack.enter_context(patch("main.check_tmux", return_value=True))
        stack.enter_context(
            patch("main.resolve_agent", side_effect=lambda _agent: self.agent_config)
        )
        stack.enter_context(
            patch(
                "main.resolve_launcher_command", side_effect=lambda launcher: launcher
            )
        )
        stack.enter_context(patch("main.get_repo_root", return_value=self.temp_root))
        stack.enter_context(patch("main.get_provider_key", return_value="codex"))
        stack.enter_context(
            patch("main.get_session_restore_mode", return_value="cli_optional_arg")
        )
        stack.enter_context(
            patch("main.get_session_restore_flag", return_value="resume")
        )
        stack.enter_context(
            patch("main._snapshot_provider_sessions", return_value=set())
        )
        stack.enter_context(patch("main._load_provider_session_id", return_value=""))
        stack.enter_context(patch("main._provider_session_exists", return_value=False))
        stack.enter_context(
            patch("main._find_new_provider_session_id_with_retry", return_value="")
        )
        stack.enter_context(patch("main._save_provider_session_id", return_value=None))
        stack.enter_context(patch("main.build_system_prompt", return_value=""))
        stack.enter_context(patch("main.get_system_prompt_mode", return_value=""))
        stack.enter_context(patch("main.get_system_prompt_flag", return_value=""))
        stack.enter_context(patch("main.get_system_prompt_key", return_value=""))
        stack.enter_context(patch("main.get_agents_md_mode", return_value=""))
        stack.enter_context(patch("main.get_mcp_config_mode", return_value=""))
        stack.enter_context(patch("main.get_mcp_config_flag", return_value=""))
        stack.enter_context(patch("main.wait_for_prompt", return_value=True))
        stack.enter_context(patch("main.wait_for_agent_ready", return_value=True))
        stack.enter_context(patch("main.inject_system_prompt", return_value=True))
        stack.enter_context(
            patch("main.list_all_agents", return_value={"EMP_0001": self.agent_config})
        )
        stack.enter_context(
            patch("main.start_session", side_effect=runtime.start_session)
        )
        stack.enter_context(
            patch(
                "main.start_session_with_layout",
                side_effect=runtime.start_session_with_layout,
            )
        )
        stack.enter_context(
            patch("main.stop_session", side_effect=runtime.stop_session)
        )
        stack.enter_context(
            patch("main.session_exists", side_effect=runtime.session_exists)
        )
        stack.enter_context(
            patch("main.get_session_info", side_effect=runtime.get_session_info)
        )
        stack.enter_context(
            patch("main.capture_output", side_effect=runtime.capture_output)
        )
        stack.enter_context(patch("main.send_keys", side_effect=runtime.send_keys))
        stack.enter_context(
            patch("main.get_agent_runtime_state", return_value={"state": "idle"})
        )

    def _run_stage_ok(
        self, stage: str, func, args, *, stdin_text: str | None = None
    ) -> str:
        output = io.StringIO()
        with redirect_stdout(output):
            if stdin_text is None:
                rc = func(args)
            else:
                with patch("sys.stdin", io.StringIO(stdin_text)):
                    rc = func(args)
        text = output.getvalue()
        self.assertEqual(rc, 0, msg=f"[stage:{stage}] expected rc=0, got {rc}\n{text}")
        return text

    def test_e2e_lifecycle_with_codex_file_pointer_fallback(self):
        runtime = _FakeRuntime()
        with ExitStack() as stack:
            self._patch_common(stack, runtime)
            stack.enter_context(
                patch("main._maybe_rollover_heartbeat_session", return_value=None)
            )

            self._run_stage_ok(
                "start",
                main.cmd_start,
                argparse.Namespace(
                    agent="dev", working_dir=None, restore=True, tmux_layout="sessions"
                ),
            )

            monitor_out = self._run_stage_ok(
                "monitor",
                main.cmd_monitor,
                argparse.Namespace(agent="dev", follow=False, lines=20),
            )
            self.assertIn(
                "Last 20 lines",
                monitor_out,
                msg="[stage:monitor] expected snapshot header",
            )

            long_message = "\n".join([f"line-{index}" for index in range(20)])
            self._run_stage_ok(
                "send",
                main.cmd_send,
                argparse.Namespace(agent="dev", message=long_message, send_enter=True),
            )
            send_payload = runtime.sent_messages[-1]["message"]
            self.assertIn(
                "Read and execute the message from file:",
                send_payload,
                msg="[stage:send] expected codex file-pointer send payload",
            )
            send_file = Path(send_payload.split("file:", 1)[1].splitlines()[0].strip())
            self.assertTrue(
                send_file.exists(),
                msg="[stage:send] expected generated send file to exist",
            )

            long_assignment = "\n".join([f"task-{index}" for index in range(24)])
            self._run_stage_ok(
                "assign",
                main.cmd_assign,
                argparse.Namespace(agent="dev", task_file=None),
                stdin_text=long_assignment,
            )
            assign_payload = runtime.sent_messages[-1]["message"]
            self.assertIn(
                "Read and follow instructions from file:",
                assign_payload,
                msg="[stage:assign] expected codex file-pointer assignment payload",
            )
            assign_file = Path(
                assign_payload.split("file:", 1)[1].splitlines()[0].strip()
            )
            self.assertTrue(
                assign_file.exists(),
                msg="[stage:assign] expected generated assignment file to exist",
            )

            self._run_stage_ok(
                "heartbeat",
                main.cmd_heartbeat_run,
                argparse.Namespace(agent="dev", timeout=None),
            )
            hb_payload = runtime.sent_messages[-1]["message"]
            self.assertIn(
                "[HB_ID:",
                hb_payload,
                msg="[stage:heartbeat] expected traceable HB_ID marker",
            )

            self._run_stage_ok("stop", main.cmd_stop, argparse.Namespace(agent="dev"))

    def test_start_restore_reuses_existing_session(self):
        runtime = _FakeRuntime()
        runtime.running = True

        with ExitStack() as stack:
            self._patch_common(stack, runtime)
            output = self._run_stage_ok(
                "start-restore",
                main.cmd_start,
                argparse.Namespace(
                    agent="dev", working_dir=None, restore=True, tmux_layout="sessions"
                ),
            )
            self.assertIn(
                "Restored existing session",
                output,
                msg="[stage:start-restore] expected restore confirmation",
            )
            self.assertEqual(
                len(runtime.start_commands),
                0,
                msg="[stage:start-restore] should not create a new tmux session",
            )

    def test_heartbeat_auto_session_mode_rollover_path(self):
        runtime = _FakeRuntime()
        runtime.running = True
        self.agent_config["heartbeat"] = {"enabled": True, "session_mode": "auto"}
        handoff_file = self.temp_root / "auto-handoff.md"

        with ExitStack() as stack:
            self._patch_common(stack, runtime)
            stack.enter_context(
                patch("main._detect_agent_context_left_percent", return_value=10)
            )
            stack.enter_context(
                patch(
                    "main._write_heartbeat_handoff_template", return_value=handoff_file
                )
            )
            stack.enter_context(
                patch("main._wait_for_idle_after_handoff", return_value="idle")
            )
            stack.enter_context(
                patch("main._heartbeat_handoff_saved", return_value=True)
            )
            stack.enter_context(patch("main.cmd_start", return_value=0))

            output = self._run_stage_ok(
                "heartbeat-auto",
                main.cmd_heartbeat_run,
                argparse.Namespace(agent="dev", timeout="30s"),
            )
            self.assertIn(
                "rollover triggered (context<25%)",
                output,
                msg="[stage:heartbeat-auto] expected auto rollover reason",
            )
            self.assertGreaterEqual(
                len(runtime.sent_messages),
                2,
                msg="[stage:heartbeat-auto] expected handoff + heartbeat send",
            )
            self.assertIn(
                "HEARTBEAT_HANDOFF_SAVED",
                runtime.sent_messages[-2]["message"],
                msg="[stage:heartbeat-auto] expected handoff prompt before heartbeat",
            )
            self.assertIn(
                "First read rollover handoff file:",
                runtime.sent_messages[-1]["message"],
                msg="[stage:heartbeat-auto] expected heartbeat message to include handoff file",
            )

    def test_heartbeat_fresh_session_mode_rollover_path(self):
        runtime = _FakeRuntime()
        runtime.running = True
        self.agent_config["heartbeat"] = {"enabled": True, "session_mode": "fresh"}
        handoff_file = self.temp_root / "fresh-handoff.md"

        with ExitStack() as stack:
            self._patch_common(stack, runtime)
            stack.enter_context(
                patch("main._detect_agent_context_left_percent", return_value=None)
            )
            stack.enter_context(
                patch(
                    "main._write_heartbeat_handoff_template", return_value=handoff_file
                )
            )
            stack.enter_context(
                patch("main._wait_for_idle_after_handoff", return_value="idle")
            )
            stack.enter_context(
                patch("main._heartbeat_handoff_saved", return_value=True)
            )
            stack.enter_context(patch("main.cmd_start", return_value=0))

            output = self._run_stage_ok(
                "heartbeat-fresh",
                main.cmd_heartbeat_run,
                argparse.Namespace(agent="dev", timeout="30s"),
            )
            self.assertIn(
                "rollover triggered (fresh session_mode)",
                output,
                msg="[stage:heartbeat-fresh] expected fresh rollover reason",
            )
            self.assertGreaterEqual(
                len(runtime.sent_messages),
                2,
                msg="[stage:heartbeat-fresh] expected handoff + heartbeat send",
            )
            self.assertIn(
                "HEARTBEAT_HANDOFF_SAVED",
                runtime.sent_messages[-2]["message"],
                msg="[stage:heartbeat-fresh] expected handoff prompt before heartbeat",
            )


if __name__ == "__main__":
    unittest.main()
