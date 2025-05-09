#!/usr/bin/env python3
import os
import sys
import subprocess

# Set the environment variable for the agent module
os.environ["AGENT_MODULE"] = "adk_cli_agent.agent"

# Check for Google API key and configure it properly for ADK
def check_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it using: export GOOGLE_API_KEY=your-api-key")
        sys.exit(1)
    
    # Make sure the API key is also set in the ADK-specific environment variable
    # ADK uses GOOGLE_API_KEY directly but we set it explicitly to be sure
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Also configure the generative AI library directly
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print(f"Google API key configured successfully.")
    except ImportError:
        # If the library isn't available, we can still proceed with ADK
        pass

if __name__ == "__main__":
    # Check API key before running
    check_api_key()
    
    # Run the agent using ADK's CLI command
    try:
        # Use subprocess to run the adk command
        result = subprocess.run(
            ['adk', 'run', 'adk_cli_agent'],
            env=os.environ.copy()
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running ADK agent: {e}")
        sys.exit(1)
