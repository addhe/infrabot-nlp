# Architecture Document: Gemini-ChatGPT CLI

## 1. Introduction

This document outlines the architecture of the Gemini-ChatGPT CLI application, targeting Python 3.13+ environments. The application provides a unified command-line interface to interact with multiple AI models, including Google's Gemini, OpenAI's GPT models, and Anthropic's Claude. It supports various functionalities like executing shell commands, fetching time, and managing GCP projects.

## System Requirements

- Python 3.13 or later
- Primary support for macOS
- Secondary support for Linux and Windows
- Required dependencies as specified in requirements.txt
- Development dependencies as specified in requirements-dev.txt

## 2. High-Level Architecture

The application follows a modular architecture, primarily divided into two main implementation strategies:

1.  **Direct API Implementation**: Interacts directly with the respective AI provider APIs.
2.  **ADK (Agent Development Kit) Implementation**: Utilizes Google's ADK for a more integrated experience with Gemini, leveraging its specific capabilities.

```
+---------------------+      +-------------------------+      +-----------------------+
|     CLI Interface   |<---->|   Agent Core Logic      |<---->|   AI Model Providers  |
| (run_agent.py,      |      | (my_cli_agent/agent.py, |      | (Gemini, OpenAI,      |
|  run_adk_agent.py)  |      |  adk_cli_agent/agent.py)|      |  Anthropic)           |
+---------------------+      +-------------------------+      +-----------------------+
                                      ^
                                      |
                                      v
                             +-----------------------+
                             |      Tool Modules     |
                             | (command, gcp, time)  |
                             +-----------------------+
```

## 3. Key Components

### 3.1. CLI Interface (`run_agent.py`, `run_adk_agent.py`)

*   **Purpose**: Entry points for the application. They handle user input, initialize the appropriate agent, and manage the main interaction loop.
*   **Responsibilities**:
    *   Parse command-line arguments (if any).
    *   Load environment variables and configurations (e.g., API keys).
    *   Instantiate the selected agent (Direct API or ADK).
    *   Process user commands and display responses.
    *   Handle exit conditions.

### 3.2. Agent Core Logic

#### 3.2.1. Direct API Implementation (`my_cli_agent/agent.py`)

*   **Purpose**: Manages interactions when using AI models directly via their APIs.
*   **Responsibilities**:
    *   Initialize and manage connections to different AI provider SDKs (Google, OpenAI, Anthropic).
    *   Orchestrate calls to the selected AI model.
    *   Integrate with various `Tool Modules` to provide extended functionalities.
    *   Format requests to AI models and parse their responses.
    *   Maintain conversation history (if applicable).

#### 3.2.2. ADK Implementation (`adk_cli_agent/agent.py`)

*   **Purpose**: Manages interactions specifically for Google's Gemini model using the Agent Development Kit.
*   **Responsibilities**:
    *   Initialize and configure the ADK agent.
    *   Define and register tools compatible with the ADK framework.
    *   Leverage ADK's built-in capabilities for function calling and state management.
    *   Process instructions and delegate tasks to the appropriate ADK tools.

### 3.3. Tool Modules (`my_cli_agent/tools/`, `adk_cli_agent/tools/`)

*   **Purpose**: Provide specific functionalities that the AI agent can invoke. These are designed to be modular and reusable.
*   **Key Modules**:
    *   `command_tools.py`: Executes shell commands.
    *   `gcp_tools.py`: Interacts with Google Cloud Platform (listing/creating projects).
    *   `time_tools.py`: Fetches the current time for specified cities.
    *   `terminal_tools.py` (Direct API only): Provides tools for terminal interactions.
*   **Structure**: Each tool module typically defines functions that can be called by the agent, often with schemas describing their parameters and expected output.

### 3.4. AI Model Providers (`my_cli_agent/providers/`)

*   **Purpose**: (Primarily for Direct API Implementation) Abstract the specifics of interacting with different AI model APIs.
*   **Responsibilities**:
    *   Implement provider-specific logic for authentication, request formatting, and response parsing.
    *   Allow the `Agent Core Logic` to switch between AI models (Gemini, GPT, Claude) seamlessly.

## 4. Data Flow

1.  User enters a command/query via the CLI.
2.  The `CLI Interface` (`run_*.py`) captures the input.
3.  The input is passed to the active `Agent Core Logic` (`my_cli_agent/agent.py` or `adk_cli_agent/agent.py`).
4.  The Agent, potentially with the help of an AI model, determines if a `Tool Module` needs to be invoked.
    *   If a tool is needed, the Agent calls the relevant function in the `Tool Module`.
    *   The `Tool Module` executes its task (e.g., runs a shell command, calls GCP API).
    *   The result from the `Tool Module` is returned to the Agent.
5.  The Agent formulates a prompt (including tool results, if any) and sends it to the selected `AI Model Provider` (for Direct API) or through the ADK framework.
6.  The AI model processes the prompt and returns a response.
7.  The Agent receives the AI model's response.
8.  The Agent formats the final response and sends it back to the `CLI Interface`.
9.  The `CLI Interface` displays the response to the user.

## 5. Design Principles

*   **Modularity**: Components are separated by concern, making the system easier to understand, maintain, and extend.
*   **Extensibility**: Easy to add new AI models (especially in the Direct API path) and new tools.
*   **Configurability**: API keys and model preferences are managed through environment variables.
*   **Abstraction**: The core agent logic is abstracted from the specifics of individual AI models or tools.
*   **User-Centricity**: Provides a simple and intuitive command-line experience.

## 6. Future Considerations

*   **Enhanced State Management**: More sophisticated conversation history and context management.
*   **Plugin Architecture for Tools**: Allow for easier integration of third-party or user-defined tools.
*   **Improved Error Handling**: More granular error reporting and recovery mechanisms.
*   **Asynchronous Operations**: For long-running tools or API calls to prevent blocking the CLI.
*   **Testing Framework**: More comprehensive unit and integration tests.
*   **GUI Interface**: Potentially extending beyond a CLI to a graphical interface.