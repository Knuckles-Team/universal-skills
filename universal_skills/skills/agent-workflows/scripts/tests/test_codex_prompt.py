import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tmux_helper  # noqa: E402


class CodexPromptDetectionTests(unittest.TestCase):
    def test_detects_upgrade_model_choice_prompt(self):
        output = """
Codex just got an upgrade. Introducing gpt-5.2-codex.

Choose how you'd like Codex to proceed.

› 1. Try new model
  2. Use existing model
"""
        self.assertTrue(tmux_helper._is_codex_model_choice_prompt(output))

    def test_detects_generic_model_choice_prompt(self):
        output = """
Choose how you'd like Codex to proceed.
› 1. Try new model
  2. Use existing model
"""
        self.assertTrue(tmux_helper._is_codex_model_choice_prompt(output))

    def test_does_not_flag_regular_prompt_or_suggestions(self):
        output = """
› Summarize the changes
❯
"""
        self.assertFalse(tmux_helper._is_codex_model_choice_prompt(output))

    def test_menu_option_regex_matches_numbered_options_only(self):
        self.assertIsNotNone(
            tmux_helper._CODEX_MENU_OPTION_RE.match("› 1. Try new model")
        )
        self.assertIsNotNone(
            tmux_helper._CODEX_MENU_OPTION_RE.match("❯ 2. Use existing model")
        )
        self.assertIsNone(
            tmux_helper._CODEX_MENU_OPTION_RE.match("› Summarize the changes")
        )
        self.assertIsNone(tmux_helper._CODEX_MENU_OPTION_RE.match("❯"))


if __name__ == "__main__":
    unittest.main()
