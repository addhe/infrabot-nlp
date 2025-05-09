#!/usr/bin/env python3
import os
import sys
import subprocess

# Set the environment variable for the agent module
os.environ["AGENT_MODULE"] = "adk_cli_agent.agent"

if __name__ == "__main__":
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
