import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SCRIPTS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR.parent))

import main  # noqa: E402
from providers import get_session_restore_flag, get_session_restore_mode  # noqa: E402


class ProviderRestoreTests(unittest.TestCase):
    def test_codex_provider_restore_config(self):
        self.assertEqual(get_session_restore_mode("codex"), "cli_optional_arg")
        self.assertEqual(get_session_restore_flag("codex"), "resume")

    def test_codex_restore_args_are_prefixed_with_resume_and_session(self):
        args = main._apply_session_restore_args(
            provider_key="codex",
            launcher="codex",
            launcher_args=[
                "--model=gpt-5.3-codex",
                "--dangerously-bypass-approvals-and-sandbox",
            ],
            restore_flag="resume",
            session_id="019c3eb0-bca0-7ab0-8b93-3b54b5f582dc",
        )
        self.assertGreaterEqual(len(args), 2)
        self.assertEqual(args[0], "resume")
        self.assertEqual(args[1], "019c3eb0-bca0-7ab0-8b93-3b54b5f582dc")
        self.assertIn("--model=gpt-5.3-codex", args)


if __name__ == "__main__":
    unittest.main()
