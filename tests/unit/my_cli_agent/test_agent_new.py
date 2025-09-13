import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.agent_new import Agent
from my_cli_agent.models import ToolResult

class TestAgentNew(unittest.TestCase):

    @patch('my_cli_agent.agent_new.GeminiProvider')
    def setUp(self, MockGeminiProvider):
        """Set up a new Agent instance for each test."""
        # Mock the provider to avoid actual API calls during initialization
        self.mock_provider = MockGeminiProvider.return_value
        self.agent = Agent()

        # Now that the agent instance exists, we can mock its instance attributes
        self.agent.provider = self.mock_provider
        self.agent.tools = {
            'get_current_time': MagicMock(return_value=ToolResult(success=True, result="Mock time is 12:00 PM")),
            'execute_command': MagicMock(return_value=ToolResult(success=True, result="Mock command output"))
        }
        self.mock_tools = self.agent.tools

    def test_handle_chat_message_tool_success(self):
        """Test when LLM selects a tool and it executes successfully."""
        # Arrange: Configure the mock provider to return a tool call
        llm_decision = "TOOL: get_current_time\nARGS: jakarta"
        self.mock_provider.generate_response.return_value = llm_decision
        
        # Act: Call the method under test
        prompt = "what time is it in jakarta?"
        response = self.agent.handle_chat_message(prompt)

        # Assert: Check that the correct tool was called and its result was returned
        self.mock_tools['get_current_time'].assert_called_once_with("jakarta")
        self.assertEqual(response, "Mock time is 12:00 PM")

    def test_handle_chat_message_tool_failure(self):
        """Test when LLM selects a tool and it fails."""
        # Arrange: Configure the mock tool to return a failure
        self.mock_tools['execute_command'].return_value = ToolResult(
            success=False, 
            error_message="Command not found"
        )
        llm_decision = "TOOL: execute_command\nARGS: non_existent_command"
        self.mock_provider.generate_response.return_value = llm_decision

        # Act
        prompt = "run non_existent_command"
        response = self.agent.handle_chat_message(prompt)

        # Assert
        self.mock_tools['execute_command'].assert_called_once_with("non_existent_command")
        self.assertIn("Error executing tool: Command not found", response)

    def test_handle_chat_message_no_tool_needed(self):
        """Test when LLM decides no tool is needed and generates a conversational response."""
        # Arrange: First call to decide tool, second to generate conversation
        self.mock_provider.generate_response.side_effect = [
            "NO_TOOL_NEEDED",
            "Hello! How can I help you today?"
        ]

        # Act
        prompt = "hello"
        response = self.agent.handle_chat_message(prompt)

        # Assert
        self.assertEqual(self.mock_provider.generate_response.call_count, 2)
        self.assertEqual(response, "Hello! How can I help you today?")
        # Ensure no tools were called
        for tool_mock in self.mock_tools.values():
            tool_mock.assert_not_called()

    def test_handle_chat_message_unknown_tool(self):
        """Test when LLM requests a tool that doesn't exist."""
        # Arrange: LLM requests a tool not in self.agent.tools
        llm_decision = "TOOL: make_coffee\nARGS: black"
        # The agent should then fall back to a conversational response
        self.mock_provider.generate_response.side_effect = [
            llm_decision,
            "I'm sorry, I can't make coffee, but I can help with other tasks."
        ]

        # Act
        prompt = "make me a coffee"
        response = self.agent.handle_chat_message(prompt)

        # Assert
        self.assertEqual(response, "I'm sorry, I can't make coffee, but I can help with other tasks.")
        for tool_mock in self.mock_tools.values():
            tool_mock.assert_not_called()

    def test_handle_chat_message_malformed_llm_response(self):
        """Test when the LLM tool decision is malformed."""
        # Arrange: LLM gives a response that can't be parsed
        llm_decision = "I think you should use a tool but I'm not sure which."
        self.mock_provider.generate_response.side_effect = [
            llm_decision,
            "I'm not sure how to handle that request. Could you rephrase?"
        ]

        # Act
        prompt = "some confusing request"
        response = self.agent.handle_chat_message(prompt)

        # Assert
        self.assertEqual(response, "I'm not sure how to handle that request. Could you rephrase?")

if __name__ == '__main__':
    unittest.main()
