import subprocess
import os
from subprocess import TimeoutExpired
from my_cli_agent.models import ToolResult

def execute_command(command: str) -> ToolResult:
    """
    Executes a shell command and returns the result in a ToolResult object.
    This function no longer prints to stdout.

    Args:
        command (str): The command to execute.

    Returns:
        ToolResult: An object containing the execution result.
    """
    command = command.strip()

    # Security check for potentially dangerous commands
    dangerous_commands = [
        "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf ~/", "rm -rf ~/*",
        "mkfs", "dd if=/dev/zero", ":(){ :|:& };:", "> /dev/sda",
        "chmod -R 777 /", "mv ~ /dev/null"
    ]
    for dangerous in dangerous_commands:
        if dangerous in command:
            error_msg = f"Refusing to execute potentially dangerous command: {command}"
            return ToolResult(success=False, error_message=error_msg)

    try:
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=30  # 30-second timeout
        )

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        # Truncate long outputs
        max_len = 2000
        if len(stdout) > max_len:
            stdout = stdout[:max_len] + "\n... (stdout truncated)"
        if len(stderr) > max_len:
            stderr = stderr[:max_len] + "\n... (stderr truncated)"

        if process.returncode == 0:
            # On success, return stdout if it exists, otherwise a success message.
            output = stdout if stdout else f"Command '{command}' executed successfully with no output."
            return ToolResult(success=True, result=output)
        else:
            # On failure, combine stderr and stdout for a comprehensive error message.
            error_output = f"Command '{command}' failed with return code {process.returncode}.\n"
            if stderr:
                error_output += f"\n--- STDERR ---\n{stderr}"
            if stdout:
                error_output += f"\n--- STDOUT ---\n{stdout}"
            return ToolResult(success=False, error_message=error_output)

    except TimeoutExpired:
        error_msg = f"Command '{command}' timed out after 30 seconds."
        return ToolResult(success=False, error_message=error_msg)

    except Exception as e:
        error_msg = f"An unexpected error occurred while executing command '{command}': {e}"
        return ToolResult(success=False, error_message=error_msg)
