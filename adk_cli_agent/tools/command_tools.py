"""Command execution tools for ADK CLI Agent."""

import subprocess
import os

def execute_command(command: str) -> dict:
    """Executes a shell command and returns the result.
    
    Args:
        command (str): The command to execute
        
    Returns:
        dict: status and result or error message.
    """
    try:
        # Always use shell=True for consistent behavior with spaces in paths
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        # Print command output immediately and clearly
        print("\nOutput:")
        print("=" * 80)
        if result.stdout:
            print(result.stdout.rstrip())
        elif result.stderr:
            print("Error:", result.stderr.rstrip())
        else:
            print("(No output)")
        print("=" * 80 + "\n")
        
        if result.returncode == 0:
            return {
                "status": "success",
                "report": result.stdout.strip() if result.stdout else "(No output)"
            }
        else:
            return {
                "status": "error",
                "error_message": (result.stderr.strip() if result.stderr 
                                 else f"Command failed with return code {result.returncode}")
            }
        
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        print("\nError:")
        print("=" * 80)
        print(error_msg)
        print("=" * 80 + "\n")
        
        return {
            "status": "error",
            "error_message": error_msg
        }
