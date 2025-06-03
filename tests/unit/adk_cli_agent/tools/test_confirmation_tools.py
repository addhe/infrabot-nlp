"""Unit tests for confirmation_tools module."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

import pytest
from adk_cli_agent.tools.confirmation_tools import confirm_action
from unittest.mock import patch

class TestConfirmationTools:
    pass
    def test_confirm_action_yes_variants(self):
        for user_input in ["y", "Y", "yes", "YES", "Yes"]:
            with patch("builtins.input", return_value=user_input):
                assert confirm_action("Proceed?") is True

    def test_confirm_action_no_variants(self):
        for user_input in ["n", "N", "no", "NO", "No", "", " "]:
            with patch("builtins.input", return_value=user_input):
                assert confirm_action("Proceed?") is False

    def test_confirm_action_invalid_then_yes(self):
        # Simulate user entering invalid input, then 'y'
        with patch("builtins.input", side_effect=["maybe", "y"]):
            assert confirm_action("Proceed?") is True

    def test_confirm_action_invalid_then_no(self):
        # Simulate user entering invalid input, then 'n'
        with patch("builtins.input", side_effect=["what?", "n"]):
            assert confirm_action("Proceed?") is False
