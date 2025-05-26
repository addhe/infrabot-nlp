import subprocess
import os
import shlex
import sys
from subprocess import TimeoutExpired
from .base import ToolResult

def execute_command(command: str) -> ToolResult:
    """
    Executes a shell command and returns the result.
    
    Args:
        command (str): The command to execute
        
    Returns:
        ToolResult: Contains the command output or error information
    """
    # Clean up the command
    command = command.strip()
    
    # Print the command being executed
    print(f"\nExecuting command: {command}")
    
    # Check for potentially dangerous commands
    dangerous_commands = [
        "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf ~/", "rm -rf ~/*",
        "mkfs", "dd if=/dev/zero", ":(){ :|:& };:", "> /dev/sda",
        "chmod -R 777 /", "mv ~ /dev/null"
    ]
    
    for dangerous in dangerous_commands:
        if dangerous in command:
            error_msg = f"Refusing to execute potentially dangerous command: {command}"
            print(f"\nSecurity Warning:\n{'-' * 80}\n{error_msg}\n{'-' * 80}\n")
            return ToolResult(
                success=False,
                error_message=error_msg,
                result={
                    'stdout': '',
                    'stderr': error_msg,
                    'return_code': -1
                }
            )
    
    try:
        # Set a timeout to prevent hanging commands
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=30  # 30 second timeout
        )
        
        # Format and limit output for better readability
        stdout = result.stdout.rstrip() if result.stdout else ''
        stderr = result.stderr.rstrip() if result.stderr else ''
        
        # Limit output length if too long
        max_output_length = 2000
        if len(stdout) > max_output_length:
            stdout = stdout[:max_output_length] + "\n... (output truncated, too long)"
        
        # Print command output immediately and clearly
        print(f"\nCommand completed with return code: {result.returncode}")
        print("=" * 80)
        if stdout:
            print(stdout)
        if stderr:
            print("Error output:")
            print(stderr)
        if not stdout and not stderr:
            print("(No output)")
        print("=" * 80 + "\n")
        
        # Return a more structured result
        return ToolResult(
            success=result.returncode == 0,
            result={
                'stdout': stdout,
                'stderr': stderr,
                'return_code': result.returncode,
                'command': command
            }
        )
        
    except TimeoutExpired:
        error_msg = f"Command timed out after 30 seconds: {command}"
        print(f"\nTimeout Error:\n{'-' * 80}\n{error_msg}\n{'-' * 80}\n")
        return ToolResult(
            success=False,
            error_message=error_msg,
            result={
                'stdout': '',
                'stderr': error_msg,
                'return_code': -1,
                'command': command
            }
        )
        
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        print(f"\nExecution Error:\n{'-' * 80}\n{error_msg}\n{'-' * 80}\n")
        
        return ToolResult(
            success=False,
            error_message=error_msg,
            result={
                'stdout': '',
                'stderr': error_msg,
                'return_code': -1,
                'command': command
            }
        )