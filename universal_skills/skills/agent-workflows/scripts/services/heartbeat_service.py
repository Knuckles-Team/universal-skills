import argparse
import subprocess
from pathlib import Path
from typing import Any, Optional

from .heartbeat_state_machine import classify_heartbeat_ack, failure_reason_code


def _parse_non_negative_int(value: object, default: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        return int(default)
    return max(0, parsed)


def _parse_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def parse_heartbeat_recovery_policy(
    heartbeat: dict,
    *,
    args: Optional[argparse.Namespace] = None,
    fallback_modes: Optional[set[str]] = None,
) -> dict:
    defaults = {
        "max_retries": 1,
        "retry_backoff_seconds": 3,
        "fallback_mode": "fresh",
        "notify_on_failure": False,
        "notifier_channel": "all",
    }

    recovery = heartbeat.get("recovery") if isinstance(heartbeat, dict) else {}
    raw = dict(recovery) if isinstance(recovery, dict) else {}

    for key in defaults.keys():
        if key in heartbeat and key not in raw:
            raw[key] = heartbeat.get(key)

    policy = {
        "max_retries": _parse_non_negative_int(
            raw.get("max_retries", defaults["max_retries"]), defaults["max_retries"]
        ),
        "retry_backoff_seconds": _parse_non_negative_int(
            raw.get("retry_backoff_seconds", defaults["retry_backoff_seconds"]),
            defaults["retry_backoff_seconds"],
        ),
        "fallback_mode": str(
            raw.get("fallback_mode", defaults["fallback_mode"])
            or defaults["fallback_mode"]
        )
        .strip()
        .lower(),
        "notify_on_failure": _parse_bool(
            raw.get("notify_on_failure", defaults["notify_on_failure"]),
            defaults["notify_on_failure"],
        ),
        "notifier_channel": str(
            raw.get("notifier_channel", defaults["notifier_channel"])
            or defaults["notifier_channel"]
        ).strip(),
    }

    if not policy["notifier_channel"]:
        policy["notifier_channel"] = defaults["notifier_channel"]

    normalized_fallback_modes = fallback_modes or {"none", "fresh"}
    if policy["fallback_mode"] == "restart":
        policy["fallback_mode"] = "fresh"
    if policy["fallback_mode"] not in normalized_fallback_modes:
        policy["fallback_mode"] = defaults["fallback_mode"]

    if args is not None:
        if getattr(args, "retry", None) is not None:
            policy["max_retries"] = _parse_non_negative_int(
                args.retry, policy["max_retries"]
            )
        if getattr(args, "backoff_seconds", None) is not None:
            policy["retry_backoff_seconds"] = _parse_non_negative_int(
                args.backoff_seconds, policy["retry_backoff_seconds"]
            )
        if getattr(args, "fallback_mode", None):
            fallback_mode = str(args.fallback_mode).strip().lower()
            if fallback_mode == "restart":
                fallback_mode = "fresh"
            if fallback_mode in normalized_fallback_modes:
                policy["fallback_mode"] = fallback_mode
        if getattr(args, "notify_on_failure", None) is not None:
            policy["notify_on_failure"] = _parse_bool(
                args.notify_on_failure, policy["notify_on_failure"]
            )
        if getattr(args, "notifier_channel", None):
            policy["notifier_channel"] = (
                str(args.notifier_channel).strip() or policy["notifier_channel"]
            )

    return policy


def _resolve_notifier_script(repo_root: Path) -> Optional[Path]:
    candidates = [
        repo_root / ".agent" / "skills" / "notifier" / "scripts" / "notify.py",
        repo_root / ".agent" / "skills" / "notifier" / "scripts" / "notify.py",
        Path.home() / ".agent" / "skills" / "notifier" / "scripts" / "notify.py",
        Path.home() / ".agent" / "skills" / "notifier" / "scripts" / "notify.py",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def notify_heartbeat_failure(
    repo_root: Path,
    *,
    channel: str,
    agent_name: str,
    agent_id: str,
    heartbeat_id: str,
    failure_type: str,
) -> bool:
    script = _resolve_notifier_script(repo_root)
    if not script:
        print("⚠️  notifier skill script not found; skip failure notification")
        return False

    reason_code = failure_reason_code(failure_type=failure_type)
    message = (
        f"Heartbeat recovery failed for **{agent_name}** (`{agent_id}`).\n\n"
        f"- HB_ID: `{heartbeat_id}`\n"
        f"- Failure: `{failure_type or 'unknown'}`\n"
        f"- Reason Code: `{reason_code}`\n"
        f"- Action: manual investigation required"
    )

    cmd = [
        "python3",
        str(script),
        "--channel",
        channel or "all",
        "--title",
        "Heartbeat Recovery Failed",
        "--message",
        message,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"📣 Failure notification sent via channel '{channel or 'all'}'")
            return True
        stderr = (result.stderr or "").strip()
        print(f"⚠️  notifier command failed (code={result.returncode})")
        if stderr:
            print(f"   {stderr}")
        return False
    except Exception as e:
        print(f"⚠️  notifier command error: {e}")
        return False


def restart_heartbeat_session_fresh(
    agent_file_id: str, agent_name: str, agent_id: str, *, deps: Any
) -> bool:
    print(f"♻️  Restarting '{agent_name}' with fresh session")
    deps.stop_session(agent_id)
    deps.time.sleep(1)

    restart_args = deps.argparse.Namespace(
        agent=agent_file_id,
        working_dir=None,
        restore=False,
        tmux_layout="sessions",
    )
    if deps.cmd_start(restart_args) != 0:
        print(f"❌ Failed to restart '{agent_name}'")
        return False
    deps.time.sleep(2)
    return True


def run_heartbeat_attempt(
    *,
    agent_id: str,
    agent_name: str,
    launcher: str,
    heartbeat_message: str,
    timeout_seconds: Optional[int],
    is_codex: bool,
    deps: Any,
) -> dict:
    started = deps.time.time()

    if not deps.send_keys(
        agent_id,
        heartbeat_message,
        send_enter=True,
        clear_input=is_codex,
        escape_first=is_codex,
        enter_via_key=is_codex,
    ):
        failure_type = "send_fail"
        return {
            "send_status": "fail",
            "ack_status": "not_checked",
            "failure_type": failure_type,
            "reason_code": failure_reason_code(
                failure_type=failure_type, send_status="fail", ack_status="not_checked"
            ),
            "last_state": None,
            "duration_ms": int((deps.time.time() - started) * 1000),
        }

    print(f"✅ Heartbeat sent to {agent_name}")

    waited_for_ack = bool(timeout_seconds and timeout_seconds > 0)
    last_state: Optional[str] = None
    timed_out = False

    if waited_for_ack:
        start_time = deps.time.time()
        poll_seconds = 2
        print(f"   Waiting for response (up to {int(timeout_seconds)}s)...")

        deps.time.sleep(3)
        while (deps.time.time() - start_time) < timeout_seconds:
            runtime = deps.get_agent_runtime_state(agent_id, launcher=launcher)
            last_state = str(runtime.get("state", "unknown"))

            if last_state == "idle":
                break
            if last_state in ("blocked", "error", "stuck"):
                break
            deps.time.sleep(poll_seconds)

        if last_state != "idle" and (deps.time.time() - start_time) >= timeout_seconds:
            timed_out = True

        deps.time.sleep(1)
        tail = deps.capture_output(agent_id, lines=50)
        if tail:
            print("----- Agent Output (tail) -----")
            print(tail.rstrip())
            print("----- End Agent Output -----")
        else:
            print("⚠️  Could not capture agent output")

    ack_status, failure_type, reason_code = classify_heartbeat_ack(
        waited_for_ack=waited_for_ack,
        last_state=last_state,
        timed_out=timed_out,
    )

    if last_state and last_state != "idle":
        print(f"⚠️  Agent state after wait: {last_state}")

    return {
        "send_status": "ok",
        "ack_status": ack_status,
        "failure_type": failure_type,
        "reason_code": reason_code,
        "last_state": last_state,
        "duration_ms": int((deps.time.time() - started) * 1000),
    }
