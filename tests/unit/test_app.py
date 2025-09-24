import unittest
import json
from unittest.mock import patch, MagicMock

# Set environment variables before importing the app
import os
os.environ['GOOGLE_API_KEY'] = 'test-key'

from app import app

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up a test client for the Flask app."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.agent')
    def test_handle_event_message_success(self, mock_agent):
        """Test a successful MESSAGE event."""
        # Arrange
        mock_agent.handle_chat_message.return_value = "Agent response"
        chat_event = {
            "type": "MESSAGE",
            "message": {
                "text": "@Infrabot hello world"
            }
        }

        # Act
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data, {"text": "Agent response"})
        # Check that the agent was called with the cleaned prompt
        mock_agent.handle_chat_message.assert_called_once_with("hello world")

    def test_handle_event_added_to_space(self):
        """Test the ADDED_TO_SPACE event."""
        chat_event = {"type": "ADDED_TO_SPACE"}
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("Terima kasih telah menambahkan saya", response_data['text'])

    def test_handle_event_removed_from_space(self):
        """Test the REMOVED_FROM_SPACE event."""
        chat_event = {"type": "REMOVED_FROM_SPACE"}
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{}\n')

    def test_handle_event_empty_body(self):
        """Test receiving a request with an empty body."""
        response = self.app.post('/', data=None, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    @patch('app.agent')
    def test_handle_event_agent_exception(self, mock_agent):
        """Test when the agent throws an exception."""
        # Arrange
        mock_agent.handle_chat_message.side_effect = Exception("Something went wrong")
        chat_event = {
            "type": "MESSAGE",
            "message": {"text": "@Infrabot do something"}
        }

        # Act
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')

        # Assert
        self.assertEqual(response.status_code, 200) # The endpoint itself should not crash
        response_data = json.loads(response.data)
        self.assertIn("Maaf, terjadi kesalahan", response_data['text'])
        self.assertIn("Something went wrong", response_data['text'])

    def test_handle_event_unknown_type(self):
        """Test an unhandled event type."""
        chat_event = {"type": "CARD_CLICKED"} # An event type the app doesn't handle
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'{}\n') # Should do nothing and return empty JSON

    def test_handle_event_message_with_empty_prompt(self):
        """
        Test a MESSAGE event that results in an empty prompt.
        This happens if the message only contains the bot's name.
        """
        chat_event = {
            "type": "MESSAGE",
            "message": {"text": "@Infrabot"} # Results in empty prompt
        }
        response = self.app.post('/', data=json.dumps(chat_event), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("Halo! Anda bisa bertanya kepada saya", response_data['text'])

if __name__ == '__main__':
    unittest.main()
