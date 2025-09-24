import os
import logging
import json
from typing import Dict, List, Callable

# Import AI provider
from .providers.gemini import GeminiProvider

# Import AI provider
from .providers.gemini import GeminiProvider
from .providers.mcp import get_mcp_tools

# Import tools and models
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, list_gce_instances, HAS_GCP_TOOLS
from .tools.markdown_tools import convert_file_to_markdown
from .tools.gcloud_mcp_tools import run_gcloud_command
from .tools.web_tools import view_website
from .models import Tool, ToolResult

class Agent:
    """
    A conversational agent that uses an LLM to process requests and execute tools.
    This version is refactored for backend, non-interactive use.
    """
    
    def __init__(self):
        """Initializes the agent, its provider, and its tools."""
        self.provider = self._setup_provider()
        self.tools: Dict[str, Tool] = {}
        
        # Manually register tools
        self._register_tool(get_current_time)
        self._register_tool(execute_command)
        self._register_tool(convert_file_to_markdown)
        self._register_tool(view_website)
        self._register_tool(run_gcloud_command)

        if HAS_GCP_TOOLS:
            self._register_tool(list_gcp_projects)
            self._register_tool(create_gcp_project)
            self._register_tool(list_gce_instances)
        
        # Add MCP tools from the centralized provider
        mcp_tools = get_mcp_tools()
        for tool in mcp_tools:
            self.tools[tool.name] = tool
        
        logging.info(f"Agent initialized with {len(self.tools)} tools: {list(self.tools.keys())}")

    def _register_tool(self, tool_function: Callable[..., ToolResult]):
        """Helper to create a Tool object and register it."""
        tool = Tool(
            name=tool_function.__name__,
            description=tool_function.__doc__ or "No description available.",
            func=tool_function
        )
        self.tools[tool.name] = tool

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
                        tool_to_run = self.tools[tool_name]
                        
                        result: ToolResult = tool_to_run.func(**tool_args)
                        
                        if result.success:
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
        for name, tool in self.tools.items():
            # Clean up the description for better prompting
            clean_description = ' '.join(tool.description.strip().split())
            instructions.append(f"- {name}: {clean_description}")

        instructions.append("\nUse the 'call_mcp_server' tool for complex, multi-step tasks such as code reviews, debugging, planning, or security audits.")
        instructions.append("Use the 'call_sequential_thinking_server' tool for problems that require deep, step-by-step reasoning, analysis, or breaking down a complex question.")
        instructions.append("Use the 'convert_file_to_markdown' tool to read and convert the content of a local file (like a PDF or DOCX) into Markdown text.")
        instructions.append("Use the 'view_website' tool to get the text content of a URL.")
        instructions.append("Use 'list_gce_instances' to list virtual machine instances from Google Compute Engine.")
        instructions.append("Use 'run_gcloud_command' for any other tasks related to Google Cloud Platform. The arguments should be a list of strings, for example: ['compute', 'instances', 'list', '--project=my-project']")
        
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
            return tool_name, {}

        try:
            args_dict = json.loads(args_str)
            return tool_name, args_dict
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON arguments: {e}. Raw args string: '{args_str}'")
