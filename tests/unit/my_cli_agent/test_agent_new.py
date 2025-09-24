import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.agent_new import Agent
from my_cli_agent.models import Tool, ToolResult

class TestAgentNew(unittest.TestCase):

    @patch('my_cli_agent.agent_new.GeminiProvider')
    def setUp(self, MockGeminiProvider):
        """Set up a new Agent instance for each test."""
        # Mock the provider to avoid actual API calls
        self.mock_provider = MockGeminiProvider.return_value

        # We must patch the agent's dependencies BEFORE it is instantiated
        with patch('my_cli_agent.agent_new.get_mcp_tools', return_value=[]), \
             patch('my_cli_agent.agent_new.HAS_GCP_TOOLS', False):
            self.agent = Agent()

        self.agent.provider = self.mock_provider
        
        # Create mock tool functions
        self.mock_get_time_func = MagicMock(return_value=ToolResult(success=True, result="Time is 12:00 PM"))

        # Register a mock Tool object with the agent
        self.agent.tools["get_current_time"] = Tool(
            name="get_current_time",
            description="Gets the current time.",
            func=self.mock_get_time_func
        )

    def test_handle_chat_message_single_arg_tool(self):
        """Test a tool call with a single argument."""
        # Arrange
        llm_decision = 'TOOL: get_current_time\nARGS: {"city": "jakarta"}'
        self.mock_provider.generate_response.return_value = llm_decision
        
        # Act
        response = self.agent.handle_chat_message("what time is it in jakarta?")

        # Assert
        self.mock_get_time_func.assert_called_once_with(city="jakarta")
        self.assertEqual(response, "Time is 12:00 PM")

    def test_handle_chat_message_tool_failure(self):
        """Test the scenario where a tool executes but returns a failure."""
        # Arrange
        self.mock_get_time_func.return_value = ToolResult(success=False, error_message="Time machine broke")
        llm_decision = 'TOOL: get_current_time\nARGS: {}'
        self.mock_provider.generate_response.return_value = llm_decision

        # Act
        response = self.agent.handle_chat_message("what time is it?")

        # Assert
        self.assertIn("Error executing tool: Time machine broke", response)
        self.mock_get_time_func.assert_called_once_with()

    def test_handle_chat_message_malformed_json_args(self):
        """Test when the LLM returns invalid JSON in the ARGS line."""
        # Arrange
        llm_decision = 'TOOL: get_current_time\nARGS: {"city": "jakarta"' # Malformed JSON
        # The agent should catch the parsing error and then fall back to a conversational response.
        self.mock_provider.generate_response.side_effect = [
            llm_decision,
            "I had trouble understanding the tool arguments."
        ]

        # Act
        response = self.agent.handle_chat_message("some command")

        # Assert
        self.mock_get_time_func.assert_not_called()
        self.assertEqual(response, "I had trouble understanding the tool arguments.")

    def test_no_tool_needed_fallback(self):
        """Test the standard conversational fallback."""
        # Arrange
        self.mock_provider.generate_response.side_effect = [
            "NO_TOOL_NEEDED",
            "Hello there!"
        ]
        
        # Act
        response = self.agent.handle_chat_message("hello")

        # Assert
        self.assertEqual(self.mock_provider.generate_response.call_count, 2)
        self.assertEqual(response, "Hello there!")

    def test_parse_tool_call_no_tool_line(self):
        """Test parsing a response that is missing the TOOL: line."""
        with self.assertRaisesRegex(ValueError, "did not contain 'TOOL:' line"):
            self.agent._parse_tool_call('ARGS: {"city": "jakarta"}')

    def test_parse_tool_call_no_args_line(self):
        """Test parsing a response with a tool but no ARGS line."""
        tool_name, args = self.agent._parse_tool_call('TOOL: some_tool')
        self.assertEqual(tool_name, 'some_tool')
        self.assertEqual(args, {})

    @patch.dict(os.environ, {"GOOGLE_API_KEY": ""})
    def test_setup_provider_no_api_key(self):
        """Test that the agent raises an error if the API key is not set."""
        with self.assertRaises(ValueError):
            # This test needs to instantiate a new agent to trigger the real _setup_provider
            Agent()

if __name__ == '__main__':
    unittest.main()
