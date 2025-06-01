#!/usr/bin/env python3
"""Runner script for ADK CLI Agent."""

import os
import sys
import signal
import time
import subprocess
from datetime import datetime

# Set the environment variable for the agent module
os.environ["AGENT_MODULE"] = "adk_cli_agent"

# Check for Google API key and configure it properly for ADK
def check_api_key():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it using: export GOOGLE_API_KEY=your-api-key")
        sys.exit(1)
    
    # Make sure the API key is also set in the ADK-specific environment variable
    os.environ["GOOGLE_API_KEY"] = api_key
    print(f"Google API key configured successfully.")

def setup_logging():
    """Set up logging directory and symlinks."""
    log_dir = os.path.join(os.getenv("TMPDIR", "/tmp"), "agents_log")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"agent.{timestamp}.log")
    latest_link = os.path.join(log_dir, "agent.latest.log")
    
    # Remove old symlink if it exists
    try:
        os.remove(latest_link)
    except OSError:
        pass
    
    # Create symlink to latest log
    try:
        os.symlink(log_file, latest_link)
    except OSError:
        pass
    
    print(f"Log setup complete: {log_file}")
    print(f"To access latest log: tail -F {latest_link}")
    
    return log_file

if __name__ == "__main__":
    # Check API key before running
    check_api_key()
    
    # Set up logging
    log_file = setup_logging()
    
    # Set up environment variables
    os.environ["ADK_LOG_FILE"] = log_file
    os.environ["ADK_DEBUG"] = "1"  # Enable debug logging
    
    # Print environment configuration
    print("Starting ADK agent with configuration:")
    print(f"  - Log file: {log_file}")
    print(f"  - Debug mode: {'enabled' if os.getenv('ADK_DEBUG') else 'disabled'}")
    
    def signal_handler(signum, frame):
        print("\n\n🛑 Received interrupt signal. Shutting down gracefully...")
        sys.exit(0)

def log_subprocess_output(pipe, is_error=False):
    """Log output from subprocess in real-time."""
    output_buffer = []
    while True:
        line = pipe.readline()
        if not line:
            break
        line = line.rstrip()
        if line:
            output_buffer.append(line)
            if is_error:
                print(f"[ERROR] {line}", file=sys.stderr, flush=True)
            else:
                print(f"[ADK] {line}", flush=True)
    return '\n'.join(output_buffer)
        
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Run ADK using subprocess
        print("\nStarting ADK agent...")
        print("Command: adk run adk_cli_agent")
        print("Press Ctrl+C to exit\n")

        # Prepare environment variables
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"  # Ensure output is unbuffered

        # Check if 'adk' is available in PATH
        from shutil import which
        if which("adk") is None:
            print("Error: 'adk' command not found in your PATH. Please ensure google-adk is installed and available.", file=sys.stderr)
            print("Try: pip install google-adk or check your PATH.", file=sys.stderr)
            sys.exit(1)

        # Use Popen for better control over the process
        # Use the correct path to the agent folder (relative to this script)
        agent_path = os.path.join(os.path.dirname(__file__), "adk_cli_agent")
        process = subprocess.Popen(
            ["adk", "run", agent_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
            env=env
        )

        # Start threads to capture stdout and stderr
        from threading import Thread

        stdout_thread = Thread(target=log_subprocess_output, args=(process.stdout, False))
        stderr_thread = Thread(target=log_subprocess_output, args=(process.stderr, True))

        stdout_thread.daemon = True
        stderr_thread.daemon = True

        stdout_thread.start()
        stderr_thread.start()

        try:
            # Wait for the process to complete
            while process.poll() is None:
                time.sleep(0.1)
                # Check if threads are still alive
                if not stdout_thread.is_alive() and not stderr_thread.is_alive():
                    break
        except KeyboardInterrupt:
            print("\n🛑 Shutting down agent...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            finally:
                sys.exit(0)

        # Ensure threads are done
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)

        # Check the return code
        if process.returncode != 0:
            print(f"\n❌ ADK command failed with return code {process.returncode}", file=sys.stderr)

            # Debug information
            print("\n=== Debug Information ===")
            print(f"Python executable: {sys.executable}")
            print(f"Working directory: {os.getcwd()}")
            print(f"Environment PATH: {os.getenv('PATH')}")

            try:
                import google_adk
                print(f"ADK version: {google_adk.__version__ if hasattr(google_adk, '__version__') else 'unknown'}")
            except ImportError as e:
                print(f"ADK import error: {e}")
                print("Make sure ADK is installed: pip install google-adk")

            # Check Python path
            print("\nPython path:")
            for p in sys.path:
                print(f"  {p}")

            sys.exit(process.returncode)
        else:
            print("\n✅ ADK agent finished successfully.")

    except FileNotFoundError:
        print("Error: ADK command not found. Please ensure google-adk is installed: pip install google-adk", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running ADK agent: {e}", file=sys.stderr)
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
