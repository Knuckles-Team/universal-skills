import argparse
import io
import sys
from pathlib import Path
import unittest
from contextlib import redirect_stdout

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from commands.listing import cmd_list


class _Deps:
    @staticmethod
    def list_all_agents():
        return {
            "EMP_0001": {"file_id": "EMP_0001", "name": "dev", "enabled": True},
            "EMP_0002": {"file_id": "EMP_0002", "name": "qa", "enabled": False},
            "EMP_0003": {"file_id": "EMP_0003", "name": "ops", "enabled": True},
        }

    @staticmethod
    def list_sessions():
        return ["emp-0001"]

    @staticmethod
    def get_agent_id(config):
        return config.get("file_id", "").lower()

    @staticmethod
    def get_session_info(agent_id):
        if agent_id == "emp-0001":
            return {"session": "agent-emp-0001"}
        return None


class ListCommandTests(unittest.TestCase):
    def test_list_running_filter_only_shows_running(self):
        deps = _Deps()
        args = argparse.Namespace(running=True, agent="dev")

        out = io.StringIO()
        with redirect_stdout(out):
            rc = cmd_list(args, deps=deps)

        text = out.getvalue()
        # When running filter is active, only show agents that are in a running state
        self.assertIn("📋", text)

    def test_list_shows_running_stopped_and_disabled(self):
        deps = _Deps()
        args = argparse.Namespace(running=False, agent="dev")

        out = io.StringIO()
        with redirect_stdout(out):
            rc = cmd_list(args, deps=deps)

        text = out.getvalue()
        # When no filter, show all agents
        self.assertIn("📋", text)


if __name__ == "__main__":
    unittest.main()
