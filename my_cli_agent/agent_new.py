import os
import logging
import json
from typing import Dict, List, Callable

# Import AI provider
from .providers.gemini import GeminiProvider

# Import tools and models
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS
from .tools.mcp_tools import call_mcp_server
from .tools.sequential_thinking_tools import call_sequential_thinking_server
from .tools.markdown_tools import convert_file_to_markdown
from .tools.playwright_tools import browser_navigate, browser_snapshot, browser_click, browser_type
from .tools.gcloud_mcp_tools import run_gcloud_command
from .models import ToolResult

class Agent:
    """
    A conversational agent that uses an LLM to process requests and execute tools.
    This version is refactored for backend, non-interactive use.
    """
    
    def __init__(self):
        """Initializes the agent, its provider, and its tools."""
        self.provider = self._setup_provider()
        self.tools: Dict[str, Callable[..., ToolResult]] = {
            "get_current_time": get_current_time,
            "execute_command": execute_command,
        }
        
        if HAS_GCP_TOOLS:
            self.tools["list_gcp_projects"] = list_gcp_projects
            self.tools["create_gcp_project"] = create_gcp_project
        
        # Add the MCP tool by default if its dependencies are met
        from .tools.mcp_tools import call_mcp_server
        self.tools["call_mcp_server"] = call_mcp_server
        
        # Add the Sequential Thinking MCP tool
        from .tools.sequential_thinking_tools import call_sequential_thinking_server
        self.tools["call_sequential_thinking_server"] = call_sequential_thinking_server
        
        # Add the MarkItDown tool
        from .tools.markdown_tools import convert_file_to_markdown
        self.tools["convert_file_to_markdown"] = convert_file_to_markdown
        
        # Add Playwright tools for browser automation
        from .tools.playwright_tools import browser_initialize, browser_navigate, browser_snapshot, browser_click, browser_type
        self.tools["browser_initialize"] = browser_initialize
        self.tools["browser_navigate"] = browser_navigate
        self.tools["browser_snapshot"] = browser_snapshot
        self.tools["browser_click"] = browser_click
        self.tools["browser_type"] = browser_type
        
        # Add gcloud MCP tool for native GCP commands
        from .tools.gcloud_mcp_tools import run_gcloud_command
        self.tools["run_gcloud_command"] = run_gcloud_command
        
        # Internal state to track browser session
        self.browser_session_active = False
        
        logging.info(f"Agent initialized with {len(self.tools)} tools.")

    def _setup_provider(self) -> GeminiProvider:
        """Sets up the Gemini provider."""
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("Missing GOOGLE_API_KEY environment variable for Gemini provider.")
        
        provider = GeminiProvider()
        provider.setup()
        return provider

    def handle_chat_message(self, prompt: str) -> str:
        """
        Processes a user's chat message, decides whether to use a tool,
        executes it, and returns a formatted string response.
        """
        try:
            tool_selection_prompt = self._create_tool_selection_prompt(prompt)
            llm_decision_str = self.provider.generate_response(tool_selection_prompt, [])

            if "TOOL:" in llm_decision_str:
                try:
                    tool_name, tool_args = self._parse_tool_call(llm_decision_str)

                    if tool_name in self.tools:
                        logging.info(f"Executing tool '{tool_name}' with args: {tool_args}")
                        tool_function = self.tools[tool_name]
                        
                        # Check if a browser tool is called without an active session
                        if tool_name.startswith("browser_") and tool_name != "browser_initialize" and not self.browser_session_active:
                            return "Error: A browser session has not been initialized. Please start by asking to initialize the browser."

                        result: ToolResult = tool_function(**tool_args)
                        
                        if result.success:
                            # If initialization was successful, update the state
                            if tool_name == "browser_initialize":
                                self.browser_session_active = True
                            return result.result
                        else:
                            logging.warning(f"Tool '{tool_name}' failed: {result.error_message}")
                            return f"Error executing tool: {result.error_message}"
                    else:
                        logging.warning(f"LLM requested an unknown tool: '{tool_name}'")
                except ValueError as e:
                    logging.warning(f"Could not parse LLM tool decision: {e}. Raw response: '{llm_decision_str}'")
        
            logging.info("No tool executed or tool call failed. Generating conversational response.")
            conversation_history = [{"role": "user", "content": prompt}]
            response = self.provider.generate_response(prompt, conversation_history)
            return response

        except Exception as e:
            logging.error(f"An unexpected error occurred in handle_chat_message: {e}", exc_info=True)
            return f"I'm sorry, but I encountered an unexpected error: {e}"

    def _create_tool_selection_prompt(self, user_prompt: str) -> str:
        """Creates a system prompt for the LLM to select a tool."""
        instructions = [
            f'User request: "{user_prompt}"',
            "Analyze the user's request and determine if one of the following tools can fulfill it.",
            "Available tools:",
        ]
        for name in self.tools.keys():
            instructions.append(f"- {name}")

        instructions.append("\nUse the 'call_mcp_server' tool for complex, multi-step tasks such as code reviews, debugging, planning, or security audits.")
        instructions.append("Use the 'call_sequential_thinking_server' tool for problems that require deep, step-by-step reasoning, analysis, or breaking down a complex question.")
        instructions.append("Use the 'convert_file_to_markdown' tool to read and convert the content of a local file (like a PDF or DOCX) into Markdown text.")
        instructions.extend([
            "\nFor web browser tasks, you MUST follow this sequence:",
            "1. ALWAYS call 'browser_initialize' FIRST to start the session.",
            "2. Then, you can use other browser tools like 'browser_navigate', 'browser_snapshot', 'browser_click', or 'browser_type'."
        ])
        instructions.append("Use 'run_gcloud_command' for any tasks related to Google Cloud Platform. The arguments should be a list of strings, for example: ['compute', 'instances', 'list', '--project=my-project']")
        
        instructions.extend([
            "\nRespond in the following format ONLY:",
            "TOOL: <tool_name>",
            "ARGS: {\"arg_name1\": \"value1\", \"arg_name2\": \"value2\"}",
            "\nIf no tool is suitable, respond with the single phrase: NO_TOOL_NEEDED"
        ])
        
        return "\n".join(instructions)

    def _parse_tool_call(self, llm_response: str) -> tuple[str, dict]:
        """Parses the LLM's response to extract the tool name and arguments as a dictionary."""
        lines = llm_response.strip().split('\n')
        tool_name = ""
        args_str = ""

        for line in lines:
            if line.startswith("TOOL:"):
                tool_name = line.replace("TOOL:", "").strip()
            elif line.startswith("ARGS:"):
                json_start = line.find('{')
                if json_start != -1:
                    args_str = line[json_start:]
        
        if not tool_name:
            raise ValueError("Response did not contain 'TOOL:' line.")
        
        if not args_str:
            return tool_name, {{}}

        try:
            args_dict = json.loads(args_str)
            return tool_name, args_dict
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON arguments: {e}. Raw args string: '{args_str}'")
