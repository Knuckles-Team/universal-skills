import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import main  # noqa: E402


class HeartbeatRecoveryTests(unittest.TestCase):
    def test_parse_recovery_policy_defaults(self):
        policy = main._parse_heartbeat_recovery_policy({"enabled": True})
        self.assertEqual(policy["max_retries"], 1)
        self.assertEqual(policy["retry_backoff_seconds"], 3)
        self.assertEqual(policy["fallback_mode"], "fresh")
        self.assertFalse(policy["notify_on_failure"])

    def test_parse_recovery_policy_with_nested_config(self):
        heartbeat = {
            "recovery": {
                "max_retries": 2,
                "retry_backoff_seconds": 5,
                "fallback_mode": "none",
                "notify_on_failure": True,
                "notifier_channel": "slack",
            }
        }
        policy = main._parse_heartbeat_recovery_policy(heartbeat)
        self.assertEqual(policy["max_retries"], 2)
        self.assertEqual(policy["retry_backoff_seconds"], 5)
        self.assertEqual(policy["fallback_mode"], "none")
        self.assertTrue(policy["notify_on_failure"])
        self.assertEqual(policy["notifier_channel"], "slack")

    def test_parse_recovery_policy_cli_overrides(self):
        args = type(
            "Args",
            (),
            {
                "retry": 4,
                "backoff_seconds": 1,
                "fallback_mode": "fresh",
                "notify_on_failure": True,
                "notifier_channel": "all",
            },
        )()
        policy = main._parse_heartbeat_recovery_policy(
            {"recovery": {"max_retries": 1}}, args
        )
        self.assertEqual(policy["max_retries"], 4)
        self.assertEqual(policy["retry_backoff_seconds"], 1)
        self.assertEqual(policy["fallback_mode"], "fresh")
        self.assertTrue(policy["notify_on_failure"])

    def test_classify_heartbeat_ack(self):
        self.assertEqual(
            main._classify_heartbeat_ack(
                waited_for_ack=False, last_state=None, timed_out=False
            ),
            ("not_checked", ""),
        )
        self.assertEqual(
            main._classify_heartbeat_ack(
                waited_for_ack=True, last_state="idle", timed_out=False
            ),
            ("ack", ""),
        )
        self.assertEqual(
            main._classify_heartbeat_ack(
                waited_for_ack=True, last_state="blocked", timed_out=False
            ),
            ("blocked", "blocked"),
        )
        self.assertEqual(
            main._classify_heartbeat_ack(
                waited_for_ack=True, last_state="busy", timed_out=True
            ),
            ("timeout", "timeout"),
        )
        self.assertEqual(
            main._classify_heartbeat_ack(
                waited_for_ack=True, last_state="busy", timed_out=False
            ),
            ("no_ack", "no_ack"),
        )

    def test_should_retry_heartbeat_attempt(self):
        self.assertTrue(
            main._should_retry_heartbeat_attempt(
                failure_type="send_fail", attempt_index=0, max_retries=1
            )
        )
        self.assertTrue(
            main._should_retry_heartbeat_attempt(
                failure_type="timeout", attempt_index=0, max_retries=1
            )
        )
        self.assertFalse(
            main._should_retry_heartbeat_attempt(
                failure_type="unknown", attempt_index=0, max_retries=1
            )
        )
        self.assertFalse(
            main._should_retry_heartbeat_attempt(
                failure_type="send_fail", attempt_index=1, max_retries=1
            )
        )

    @patch("main.send_keys", return_value=False)
    def test_run_heartbeat_attempt_send_fail(self, _mock_send):
        result = main._run_heartbeat_attempt(
            agent_id="emp-0001",
            agent_name="qa-agent",
            launcher="codex",
            heartbeat_message="hello",
            timeout_seconds=30,
            is_codex=True,
        )
        self.assertEqual(result["send_status"], "fail")
        self.assertEqual(result["failure_type"], "send_fail")

    @patch("main.time.sleep", return_value=None)
    @patch("main.capture_output", return_value="tail output")
    @patch("main.get_agent_runtime_state", return_value={"state": "idle"})
    @patch("main.send_keys", return_value=True)
    def test_run_heartbeat_attempt_ack(
        self, _mock_send, _mock_state, _mock_capture, _mock_sleep
    ):
        result = main._run_heartbeat_attempt(
            agent_id="emp-0001",
            agent_name="qa-agent",
            launcher="codex",
            heartbeat_message="hello",
            timeout_seconds=30,
            is_codex=True,
        )
        self.assertEqual(result["send_status"], "ok")
        self.assertEqual(result["ack_status"], "ack")

    @patch("main.cmd_start", return_value=0)
    @patch("main.stop_session", return_value=True)
    @patch("main.time.sleep", return_value=None)
    def test_restart_heartbeat_session_fresh(
        self, _mock_sleep, _mock_stop, _mock_start
    ):
        ok = main._restart_heartbeat_session_fresh("EMP_0001", "qa-agent", "emp-0001")
        self.assertTrue(ok)

    @patch("main._notify_heartbeat_failure", return_value=True)
    @patch("main._append_heartbeat_audit_event")
    @patch("main.time.sleep", return_value=None)
    @patch("main._run_heartbeat_attempt")
    @patch("main._maybe_rollover_heartbeat_session", return_value=None)
    @patch("main._detect_agent_context_left_percent", return_value=77)
    @patch("main.resolve_launcher_command", return_value="codex")
    @patch("main.session_exists", return_value=True)
    @patch("main.resolve_agent")
    @patch("main.check_tmux", return_value=True)
    def test_cmd_heartbeat_run_retry_then_success(
        self,
        _mock_tmux,
        mock_resolve_agent,
        _mock_session,
        _mock_launcher,
        _mock_context,
        _mock_rollover,
        mock_run_attempt,
        _mock_sleep,
        mock_audit,
        mock_notify,
    ):
        mock_resolve_agent.return_value = {
            "name": "qa-agent",
            "file_id": "EMP_0001",
            "enabled": True,
            "heartbeat": {
                "enabled": True,
                "recovery": {
                    "max_retries": 1,
                    "retry_backoff_seconds": 0,
                    "fallback_mode": "none",
                },
            },
            "launcher": "codex",
        }
        mock_run_attempt.side_effect = [
            {
                "send_status": "fail",
                "ack_status": "not_checked",
                "failure_type": "send_fail",
                "duration_ms": 100,
            },
            {
                "send_status": "ok",
                "ack_status": "ack",
                "failure_type": "",
                "duration_ms": 120,
            },
        ]

        args = type(
            "Args",
            (),
            {
                "agent": "EMP_0001",
                "timeout": None,
                "retry": None,
                "backoff_seconds": 0,
                "fallback_mode": None,
                "notify_on_failure": False,
                "notifier_channel": None,
            },
        )()

        result = main.cmd_heartbeat_run(args)
        self.assertEqual(result, 0)
        self.assertEqual(mock_run_attempt.call_count, 2)
        self.assertEqual(mock_audit.call_count, 2)
        mock_notify.assert_not_called()

    @patch("main._notify_heartbeat_failure", return_value=True)
    @patch("main._restart_heartbeat_session_fresh", return_value=True)
    @patch("main._append_heartbeat_audit_event")
    @patch("main.time.sleep", return_value=None)
    @patch("main._run_heartbeat_attempt")
    @patch("main._maybe_rollover_heartbeat_session", return_value=None)
    @patch("main._detect_agent_context_left_percent", return_value=12)
    @patch("main.resolve_launcher_command", return_value="codex")
    @patch("main.session_exists", return_value=True)
    @patch("main.resolve_agent")
    @patch("main.check_tmux", return_value=True)
    def test_cmd_heartbeat_run_fallback_and_notify_on_failure(
        self,
        _mock_tmux,
        mock_resolve_agent,
        _mock_session,
        _mock_launcher,
        _mock_context,
        _mock_rollover,
        mock_run_attempt,
        _mock_sleep,
        mock_audit,
        mock_restart,
        mock_notify,
    ):
        mock_resolve_agent.return_value = {
            "name": "qa-agent",
            "file_id": "EMP_0001",
            "enabled": True,
            "heartbeat": {
                "enabled": True,
                "recovery": {
                    "max_retries": 0,
                    "retry_backoff_seconds": 0,
                    "fallback_mode": "fresh",
                    "notify_on_failure": True,
                    "notifier_channel": "all",
                },
            },
            "launcher": "codex",
        }
        mock_run_attempt.side_effect = [
            {
                "send_status": "ok",
                "ack_status": "timeout",
                "failure_type": "timeout",
                "duration_ms": 200,
            },
            {
                "send_status": "fail",
                "ack_status": "no_ack",
                "failure_type": "send_fail",
                "duration_ms": 300,
            },
        ]

        args = type(
            "Args",
            (),
            {
                "agent": "EMP_0001",
                "timeout": None,
                "retry": 0,
                "backoff_seconds": 0,
                "fallback_mode": "fresh",
                "notify_on_failure": True,
                "notifier_channel": "all",
            },
        )()

        result = main.cmd_heartbeat_run(args)
        self.assertEqual(result, 1)
        self.assertEqual(mock_run_attempt.call_count, 2)
        self.assertEqual(mock_audit.call_count, 2)
        mock_restart.assert_called_once()
        mock_notify.assert_called_once()

    @patch("main._notify_heartbeat_failure", return_value=True)
    @patch("main._append_heartbeat_audit_event")
    @patch("main.time.sleep", return_value=None)
    @patch("main._run_heartbeat_attempt")
    @patch("main._maybe_rollover_heartbeat_session", return_value=None)
    @patch("main._detect_agent_context_left_percent", return_value=40)
    @patch("main.resolve_launcher_command", return_value="codex")
    @patch("main.session_exists", return_value=True)
    @patch("main.resolve_agent")
    @patch("main.check_tmux", return_value=True)
    def test_cmd_heartbeat_run_ignores_legacy_guard_config_keys(
        self,
        _mock_tmux,
        mock_resolve_agent,
        _mock_session,
        _mock_launcher,
        _mock_context,
        _mock_rollover,
        mock_run_attempt,
        _mock_sleep,
        mock_audit,
        mock_notify,
    ):
        mock_resolve_agent.return_value = {
            "name": "qa-agent",
            "file_id": "EMP_0001",
            "enabled": True,
            "heartbeat": {
                "enabled": True,
                "watch_repo": True,
                "force_action_when_open_work": True,
                "recovery": {
                    "max_retries": 0,
                    "retry_backoff_seconds": 0,
                    "fallback_mode": "none",
                    "notify_on_failure": False,
                },
            },
            "launcher": "codex",
        }

        mock_run_attempt.return_value = {
            "send_status": "ok",
            "ack_status": "ack",
            "failure_type": "",
            "duration_ms": 80,
            "reason_code": "HB_ACK_OK",
        }

        args = type(
            "Args",
            (),
            {
                "agent": "EMP_0001",
                "timeout": None,
                "retry": 0,
                "backoff_seconds": 0,
                "fallback_mode": "none",
                "notify_on_failure": False,
                "notifier_channel": None,
            },
        )()

        result = main.cmd_heartbeat_run(args)
        self.assertEqual(result, 0)
        self.assertEqual(mock_run_attempt.call_count, 1)
        mock_notify.assert_not_called()

        self.assertEqual(mock_audit.call_count, 1)
        self.assertEqual(mock_audit.call_args.kwargs.get("phase"), "attempt")
        self.assertNotEqual(mock_audit.call_args.kwargs.get("phase"), "guard_followup")


if __name__ == "__main__":
    unittest.main()
