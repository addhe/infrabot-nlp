#!/usr/bin/env python3
import os
import sys
import traceback

print("Starting agent script")
print(f"Python version: {sys.version}")

# Check environment
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), "my_cli_agent", ".env")
if os.path.exists(env_path):
    print(f"Found .env file at {env_path}")
    load_dotenv(env_path)
    print("Loaded environment variables from .env")

# Load GCP credentials if available
gcp_env_path = os.path.join(os.path.dirname(__file__), "my_cli_agent", "gcp_credentials.env")
if os.path.exists(gcp_env_path):
    print(f"Found GCP credentials file at {gcp_env_path}")
    load_dotenv(gcp_env_path, override=True)
    print("Loaded GCP credentials from gcp_credentials.env")
    
    # Verify GCP service account key file exists and is set in environment
    gcp_creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if gcp_creds_path and os.path.exists(gcp_creds_path):
        print(f"GCP service account key found at: {gcp_creds_path}")
    else:
        print(f"Warning: GCP service account key not found at: {gcp_creds_path}")
        print("GCP functionality may be limited to mock data only.")
        # Try to reuse gcloud application default credentials if available
        try:
            import subprocess
            print("Checking for gcloud application default credentials...")
            subprocess.run(['gcloud', 'info'], check=False, 
                          capture_output=True, text=True)
        except:
            print("No gcloud installation detected. GCP operations will use mock data only.")

try:
    from my_cli_agent.agent import main
    print("Successfully imported main")
    
    if __name__ == "__main__":
        print("Calling main function")
        main()
        print("Main function completed")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()