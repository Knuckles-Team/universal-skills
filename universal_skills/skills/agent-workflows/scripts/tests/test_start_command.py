import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import main  # noqa: E402


class BuildStartCommandTests(unittest.TestCase):
    def test_quotes_working_dir_and_args_with_spaces(self):
        cmd = main.build_start_command(
            working_dir="/tmp/a b",
            launcher="/path/with space/codex",
            launcher_args=["--model=gpt-5.2", "--flag", "value with space"],
        )
        self.assertIn("cd '/tmp/a b'", cmd)
        self.assertIn("'/path/with space/codex'", cmd)
        self.assertIn("'value with space'", cmd)

    def test_filters_empty_and_none_args(self):
        cmd = main.build_start_command(
            working_dir="/tmp",
            launcher="codex",
            launcher_args=["", None, "--x", 0],
        )
        self.assertIn("codex", cmd)
        self.assertIn("--x", cmd)
        self.assertNotIn("None", cmd)
        self.assertNotIn("''", cmd)

    def test_path_env_prefix_is_present(self):
        cmd = main.build_start_command(
            working_dir="/tmp",
            launcher="codex",
            launcher_args=[],
        )
        self.assertIn('export PATH="$HOME/.local/bin:$HOME/bin:$PATH"', cmd)


if __name__ == "__main__":
    unittest.main()
