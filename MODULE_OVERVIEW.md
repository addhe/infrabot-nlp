# Module Overview

This document provides an overview of the key modules and components within the `infrabot-nlp` project.

## System Requirements

- Python 3.13 or later
- macOS (primary supported platform)
- Linux/Windows (secondary supported platforms)

## Core Implementations

The project offers two main implementations for interacting with AI models:

1.  **Direct API Implementation (`my_cli_agent/`)**: This implementation interacts directly with the APIs of various AI providers (Google Gemini, OpenAI GPT, Anthropic Claude).
2.  **ADK Implementation (`adk_cli_agent/`)**: This implementation utilizes Google's Agent Development Kit (ADK) for an enhanced and potentially more integrated experience, primarily with Google's Gemini models.

## Directory Structure and Key Files

### 1. `my_cli_agent/` - Direct API Implementation

This directory contains the code for the direct API interaction agent.

*   **`agent.py`**: Main agent implementation with core functionality
*   **`agent_new.py`**: Enhanced agent implementation with additional features and optimizations
*   **`models.py`**: Pydantic models for request/response handling and tool definitions
*   **`providers/`**: AI model provider implementations
    *   `anthropic.py`: Anthropic Claude API integration
    *   `base.py`: Base provider interface and common utilities
    *   `gemini.py`: Google Gemini API integration
    *   `openai.py`: OpenAI GPT API integration
*   **`tools/`**: Agent capability implementations
    *   `base.py`: Base tool classes and interfaces
    *   `command_tools.py`: Shell command execution tools
    *   `gcp_tools.py`: Google Cloud Platform integration tools
    *   `terminal_tools.py`: Terminal interaction utilities
    *   `time_tools.py`: Time-related functionality

### 2. `adk_cli_agent/` - ADK Implementation

This directory contains the code for the agent built using Google's Agent Development Kit.

*   **`agent.py`**: The main agent implementation leveraging ADK functionalities. This likely involves defining agent behavior, tools, and interaction flows as per ADK's framework.
*   **`tools/`**: Similar to the direct API implementation, this sub-directory contains tool modules, but these are specifically designed and integrated for use with the ADK.
    *   `__init__.py`
    *   `command_tools.py`: ADK-compatible tools for shell command execution.
    *   `gcp_tools.py`: ADK-compatible tools for GCP interactions.
    *   `time_tools.py`: ADK-compatible tools for time-related information.

### 3. Root Directory Files

*   **`run_agent.py`**: The primary entry point script to launch and run the Direct API Implementation agent (`my_cli_agent`).
*   **`run_adk_agent.py`**: The primary entry point script to launch and run the ADK Implementation agent (`adk_cli_agent`).
*   **`run_openai_agent.py`**: An entry point that might be specifically tailored to run an OpenAI-only version of the agent, possibly a simplified version or for specific testing/demonstration purposes. (Further investigation may be needed to confirm its exact relationship with `my_cli_agent/agent.py`.)
*   **`requirements.txt`**: Lists all Python package dependencies for the project.
*   **`Dockerfile`**: Defines the environment and steps to build a Docker container for the application, facilitating deployment and consistent execution.
*   **`README.md`**: Provides a general introduction to the project, setup instructions, usage guidelines, and other relevant information.
*   **`CODING_STYLE.md`**: Outlines the coding conventions and style guidelines to be followed by contributors to the project.

## Interaction Flow (General Concept)

1.  **User Input**: The user provides a prompt or command to the CLI.
2.  **Agent Selection**: The user runs either `run_agent.py` (Direct) or `run_adk_agent.py` (ADK).
3.  **Processing**:
    *   The selected agent (`my_cli_agent/agent.py` or `adk_cli_agent/agent.py`) processes the input.
    *   It may interact with one of the AI models (via `my_cli_agent/providers/` or ADK's mechanisms).
    *   If the AI model determines a need to use a tool, the agent invokes the appropriate tool from the respective `tools/` directory.
4.  **Tool Execution**: The tool performs its action (e.g., runs a shell command, calls a GCP API).
5.  **Response**: The result from the tool and/or the AI model is presented back to the user.

This overview provides a high-level understanding of the project's modules. For more detailed information, refer to the source code and specific documentation for each module.