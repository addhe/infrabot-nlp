import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.agent_new import Agent
from my_cli_agent.models import ToolResult

class TestAgentNew(unittest.TestCase):

    @patch('my_cli_agent.agent_new.GeminiProvider')
    def setUp(self, MockGeminiProvider):
        """Set up a new Agent instance for each test."""
        self.mock_provider = MockGeminiProvider.return_value
        self.agent = Agent()
        self.agent.provider = self.mock_provider
        
        # Mock all tools to isolate the agent's logic
        self.agent.tools = {
            'get_current_time': MagicMock(return_value=ToolResult(success=True, result="Time is 12:00 PM")),
            'browser_navigate': MagicMock(return_value=ToolResult(success=True, result="Navigated successfully")),
            'browser_click': MagicMock(return_value=ToolResult(success=True, result="Clicked element")),
            'browser_snapshot': MagicMock(return_value=ToolResult(success=True, result="Snapshot taken"))
        }
        self.mock_tools = self.agent.tools

    def test_handle_chat_message_single_arg_tool(self):
        """Test a tool call with a single argument."""
        # Arrange
        llm_decision = 'TOOL: get_current_time\nARGS: {"city": "jakarta"}'
        self.mock_provider.generate_response.return_value = llm_decision
        
        # Act
        response = self.agent.handle_chat_message("what time is it in jakarta?")

        # Assert
        self.mock_tools['get_current_time'].assert_called_once_with(city="jakarta")
        self.assertEqual(response, "Time is 12:00 PM")

    def test_handle_chat_message_multi_arg_tool(self):
        """Test a tool call with multiple arguments, like browser_click."""
        # Arrange
        self.agent.browser_session_active = True  # Prerequisite for browser tools
        llm_decision = 'TOOL: browser_click\nARGS: {"ref": "ref123", "element": "Login Button"}'
        self.mock_provider.generate_response.return_value = llm_decision

        # Act
        response = self.agent.handle_chat_message("click the login button")

        # Assert
        self.mock_tools['browser_click'].assert_called_once_with(ref="ref123", element="Login Button")
        self.assertEqual(response, "Clicked element")

    def test_handle_chat_message_tool_with_no_args(self):
        """Test a tool call that takes no arguments, like browser_snapshot."""
        # Arrange
        self.agent.browser_session_active = True  # Prerequisite for browser tools
        llm_decision = 'TOOL: browser_snapshot\nARGS: {}'
        self.mock_provider.generate_response.return_value = llm_decision

        # Act
        response = self.agent.handle_chat_message("take a snapshot")

        # Assert
        self.mock_tools['browser_snapshot'].assert_called_once_with()
        self.assertEqual(response, "Snapshot taken")

    def test_handle_chat_message_malformed_json_args(self):
        """Test when the LLM returns invalid JSON in the ARGS line."""
        # Arrange
        llm_decision = 'TOOL: get_current_time\nARGS: {"city": "jakarta"' # Malformed JSON
        self.mock_provider.generate_response.side_effect = [
            llm_decision,
            "I had trouble understanding the tool arguments."
        ]

        # Act
        response = self.agent.handle_chat_message("some command")

        # Assert
        # It should fail to parse, not call the tool, and fall back to a conversational response.
        self.mock_tools['get_current_time'].assert_not_called()
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

if __name__ == '__main__':
    unittest.main()
