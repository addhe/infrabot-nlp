"""
Command tools module for the CLI agent.
This is a wrapper module that imports from terminal_tools for backward compatibility.
"""

from .terminal_tools import execute_command

# Re-export the execute_command function
__all__ = ['execute_command']
