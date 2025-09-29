import os
import logging
import io
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Load environment variables ---
dotenv_secret = os.environ.get("DOTENV_CONTENTS")
logging.info(f"DOTENV_CONTENTS variable found: {dotenv_secret is not None}")
if dotenv_secret:
    logging.info("Attempting to load environment from DOTENV_CONTENTS...")
    # Use StringIO to treat the string as a file for dotenv.
    load_dotenv(stream=io.StringIO(dotenv_secret))
else:
    logging.info("DOTENV_CONTENTS not found. Loading from .env file for local dev.")
    load_dotenv()

# Explicitly log the key we are looking for to confirm it was loaded.
api_key_check = os.environ.get("GOOGLE_API_KEY")
logging.info(f"GOOGLE_API_KEY is set after load: {api_key_check is not None}")
if not api_key_check:
    logging.warning("CRITICAL: GOOGLE_API_KEY was not loaded into the environment.")

# --- Placeholder for future imports ---
# from google.oauth2 import id_token
# from google.auth.transport import requests as auth_requests

from my_cli_agent.agent_new import Agent

app = Flask(__name__)

# Initialize the agent once at startup for efficiency.
# This avoids reloading the model and tools for every request.
try:
    agent = Agent()
    logging.info("Agent initialized successfully.")
except Exception as e:
    agent = None
    logging.critical(f"FATAL: Failed to initialize Agent at startup: {e}", exc_info=True)

@app.route('/', methods=['POST'])
def handle_event():
    """Handles incoming events from Google Chat."""
    
    # 1. Verify the request is from Google Chat (placeholder)
    # In a real-world scenario, you MUST verify the JWT token.
    # See: https://developers.google.com/chat/api/guides/auth/authenticating-bots
    # For now, we will skip this for initial local testing.
    # Example verification logic:
    # bearer_token = request.headers.get('Authorization', '').split(' ')[-1]
    # try:
    #     id_token.verify_oauth2_token(bearer_token, auth_requests.Request(), AUDIENCE)
    # except ValueError:
    #     return jsonify({'error': 'Unauthorized'}), 401

    # Check if agent failed to initialize
    if not agent:
        logging.error("Agent is not initialized. Cannot process request.")
        return jsonify({"text": "Maaf, bot sedang mengalami masalah teknis dan tidak dapat memproses permintaan Anda."})

    # 2. Parse the incoming event JSON
    event_data = request.get_json()
    if not event_data:
        logging.warning("Received an empty request body.")
        return jsonify({"error": "Empty request body"}), 400

    # 3. Handle different event types
    event_type = event_data.get('type')

    if event_type == 'MESSAGE':
        message = event_data.get('message', {}).get('text', '')
        # Clean the bot's name from the message if it's a mention
        # The first element in a mention is typically "@BotName".
        cleaned_prompt = ' '.join(message.split(' ')[1:]).strip()

        if not cleaned_prompt:
            return jsonify({"text": "Halo! Anda bisa bertanya kepada saya atau memberikan perintah. Coba 'bantuan' untuk melihat apa yang bisa saya lakukan."})

        try:
            # 4. Call the agent's business logic
            # We will create the `handle_chat_message` method in the next step.
            response_text = agent.handle_chat_message(cleaned_prompt)
            
            # 5. Format and return the response
            return jsonify({"text": response_text})

        except Exception as e:
            logging.error(f"Error processing message: {e}", exc_info=True)
            return jsonify({"text": f"Maaf, terjadi kesalahan saat memproses permintaan Anda: {e}"})

    elif event_type == 'ADDED_TO_SPACE':
        return jsonify({"text": "Terima kasih telah menambahkan saya ke ruang ini! Saya siap membantu. Ketik '@Infrabot bantuan' untuk memulai."})
    
    elif event_type == 'REMOVED_FROM_SPACE':
        logging.info("Bot removed from a space.")
        return jsonify({}) # No response needed

    else:
        logging.debug(f"Received unhandled event type: {event_type}")
        return jsonify({}) # Acknowledge other events with an empty 200 OK

if __name__ == '__main__':
    # Cloud Run provides the PORT environment variable.
    port = int(os.environ.get('PORT', 8080))
    # For local development, set debug=True.
    # In production, a proper WSGI server like Gunicorn will be used.
    app.run(debug=True, host='0.0.0.0', port=port)
