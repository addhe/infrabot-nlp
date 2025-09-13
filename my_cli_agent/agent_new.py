import os
import logging
from typing import Dict, List, Callable

# Import AI provider
from .providers.gemini import GeminiProvider

# Import tools and models
from .tools.time_tools import get_current_time
from .tools.command_tools import execute_command
from .tools.gcp_tools import list_gcp_projects, create_gcp_project, HAS_GCP_TOOLS
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
        from .tools.playwright_tools import browser_navigate, browser_snapshot, browser_click, browser_type
        self.tools["browser_navigate"] = browser_navigate
        self.tools["browser_snapshot"] = browser_snapshot
        self.tools["browser_click"] = browser_click
        self.tools["browser_type"] = browser_type
        
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

        Args:
            prompt: The user's message from the chat.

        Returns:
            A string containing the response to be sent back to the user.
        """
        try:
            # 1. Create a prompt to ask the LLM to select a tool.
            tool_selection_prompt = self._create_tool_selection_prompt(prompt)
            
            # 2. Get the LLM's decision on which tool to use.
            # We use a short, non-streamed response for this internal step.
            llm_decision_str = self.provider.generate_response(tool_selection_prompt, [])

            # 3. Parse the decision and execute the tool if needed.
            if "TOOL:" in llm_decision_str:
                try:
                    tool_name, tool_arg = self._parse_tool_call(llm_decision_str)

                    if tool_name in self.tools:
                        logging.info(f"Executing tool '{tool_name}' with arg: '{tool_arg}'")
                        tool_function = self.tools[tool_name]
                        result: ToolResult = tool_function(tool_arg)
                        
                        if result.success:
                            return result.result
                        else:
                            logging.warning(f"Tool '{tool_name}' failed: {result.error_message}")
                            return f"Error executing tool: {result.error_message}"
                    else:
                        logging.warning(f"LLM requested an unknown tool: '{tool_name}'")
                        # Fall through to conversational response if tool is unknown
                except ValueError as e:
                    logging.warning(f"Could not parse LLM tool decision: {e}. Raw response: '{llm_decision_str}'")
                    # Fall through to conversational response
        
            # 4. If no tool is needed (or if parsing failed), generate a direct conversational response.
            logging.info("No tool executed. Generating conversational response.")
            # For the final response, we can stream it if the provider supports it.
            # For simplicity in this backend version, we'll use the standard generation.
            conversation_history = [{"role": "user", "content": prompt}]
            response = self.provider.generate_response(prompt, conversation_history)
            return response

        except Exception as e:
            logging.error(f"An unexpected error occurred in handle_chat_message: {e}", exc_info=True)
            return f"I'm sorry, but I encountered an unexpected error: {e}"

    def _create_tool_selection_prompt(self, user_prompt: str) -> str:
        """Creates a system prompt for the LLM to select a tool."""
        
        # Basic instructions
        instructions = [
            f"User request: \"{user_prompt}\"",
            "Analyze the user's request and determine if one of the following tools can fulfill it.",
            "Available tools:",
        ]

        # Dynamically list available tools
        for name in self.tools.keys():
            instructions.append(f"- {name}")

        instructions.append(
            "\nUse the 'call_mcp_server' tool for complex, multi-step tasks such as code reviews, debugging, planning, or security audits."
        )
        instructions.append(
            "Use the 'call_sequential_thinking_server' tool for problems that require deep, step-by-step reasoning, analysis, or breaking down a complex question."
        )
        instructions.append(
            "Use the 'convert_file_to_markdown' tool to read and convert the content of a local file (like a PDF or DOCX) into Markdown text."
        )
        instructions.extend([
            "\nFor web browser tasks, use the following tools in sequence:",
            "- Use 'browser_navigate' to go to a URL.",
            "- Use 'browser_snapshot' to get a list of elements on the page.",
            "- Use 'browser_click' or 'browser_type' with the 'ref' from the snapshot to interact with elements."
        ])

        # Response format instructions
        instructions.extend([
            "If a tool is appropriate, respond in the following format ONLY:",
            "TOOL: <tool_name>",
            "ARGS: <arguments_for_the_tool>",
            "\nIf no tool is suitable, respond with the single phrase: NO_TOOL_NEEDED"
        ])
        
        return "\n".join(instructions)

    def _parse_tool_call(self, llm_response: str) -> tuple[str, str]:
        """Parses the LLM's response to extract the tool name and arguments."""
        lines = llm_response.strip().split('\n')
        tool_name = ""
        tool_arg = ""

        for line in lines:
            if line.startswith("TOOL:"):
                tool_name = line.replace("TOOL:", "").strip()
            elif line.startswith("ARGS:"):
                tool_arg = line.replace("ARGS:", "").strip()
        
        if not tool_name:
            raise ValueError("Response did not contain 'TOOL:' line.")
            
        return tool_name, tool_arg
