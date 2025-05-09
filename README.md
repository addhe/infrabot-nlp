# Gemini-ChatGPT CLI

## Introduction

This Python CLI application provides a unified interface to interact with multiple AI models including Google's Gemini, OpenAI's GPT models, and Anthropic's Claude. It can perform various tasks including executing shell commands, checking time in different cities, listing GCP projects, and creating new GCP projects.

The application has two implementations:
1. **Direct API Implementation** - Uses the AI providers' APIs directly (supports Gemini, OpenAI, and Anthropic)
2. **ADK Implementation** - Uses Google's Agent Development Kit (ADK) for enhanced Gemini integration

## Prerequisites

* Python 3.7 or later
* API keys for the models you want to use:
  * Google Gemini API key
  * OpenAI API key (optional, only for direct API implementation)
  * Anthropic API key (optional, only for direct API implementation)
* Google Cloud Application Default Credentials (for GCP project operations)
* Virtual environment
* Dependencies listed in requirements.txt

## Installation

1. Clone the repository:

```bash
git clone https://github.com/addhe/gemini-chatgpt-cli.git
```

2. Create a virtual environment:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Install the requirements:

```bash
pip install -r requirements.txt
```

## Usage

1. Obtain the necessary API keys:
   - Google Gemini API key: https://makersuite.google.com/app/apikey
   - OpenAI API key (optional): https://platform.openai.com/api-keys
   - Anthropic API key (optional): https://console.anthropic.com/settings/keys

2. Set up Google Cloud Application Default Credentials (for GCP operations):

```bash
gcloud auth application-default login
```

3. Set up your environment variables using one of these methods:

   **Option A: Using environment variables directly**
   ```bash
   export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
   export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"  # Optional
   export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"  # Optional

   # Optional model IDs
   export GEMINI_MODEL_ID="learnlm-2.0-flash-experimental"
   export OPENAI_MODEL_ID="gpt-4-turbo-preview"
   export CLAUDE_MODEL_ID="claude-3-opus-20240229"
   ```

   **Option B: Using .env file**
   ```bash
   # Copy the example environment file
   cp my_cli_agent/.env.example my_cli_agent/.env
   
   # Edit the .env file with your actual API keys
   nano my_cli_agent/.env
   ```
   
   Note: The `.env` file is ignored by git to prevent accidental exposure of your API keys.

4. Run the application using one of the two implementations:

   a. Direct API Implementation (supports multiple AI providers):
   ```bash
   python run_agent.py
   ```

   b. ADK Implementation (Gemini only, with enhanced integration):
   ```bash
   python run_adk_agent.py
   ```

5. Exit the program:

```
> exit()
```

## Using Docker

### Prerequisites
1. Make sure Docker is installed on your system
2. Authenticate to your Docker registry if needed

### Installation via Docker
1. Build the Docker image:
```bash
docker build --tag gemini-chatgpt-cli:v1.0 .
```

2. Run the container with your API keys:
```bash
docker run -it --name your-container-name \
  --env GOOGLE_API_KEY=your-gemini-api-key \
  --env OPENAI_API_KEY=your-openai-api-key \
  --env ANTHROPIC_API_KEY=your-anthropic-api-key \
  gemini-chatgpt-cli:v1.0
```

Example:
```bash
docker run -it --name ai-cli-test --env GOOGLE_API_KEY=your-actual-key gemini-chatgpt-cli:v1.0
```

## Features

- Multi-model support (Gemini, GPT, Claude) in the direct API implementation
- Enhanced Gemini integration via Google's ADK in the ADK implementation
- Execute shell commands directly from the CLI
- Get current time in different cities
- List GCP projects by environment (dev/stg/prod)
- Create new GCP projects with custom IDs, names, and organization IDs
- Modular code structure with separate modules for different tool categories
- Simple and intuitive interface

## Troubleshooting

If you encounter any issues, check the following:

* Ensure that you have active API keys for the models you want to use
* Make sure the API keys are set as environment variables
* Check that the Python script is running in the virtual environment
* Verify that all requirements are installed correctly
* For GCP operations, ensure you have set up Google Cloud Application Default Credentials by running `gcloud auth application-default login`
* If you see a warning about "Default value is not supported in function declaration schema for Google AI", this is a known issue with the Google AI SDK and does not affect functionality

## Project Structure

The project has been refactored into a modular structure:

```
├── adk_cli_agent/            # ADK implementation
│   ├── agent.py              # Main agent implementation using ADK
│   ├── tools/                # Tool modules for ADK implementation
│   │   ├── __init__.py
│   │   ├── command_tools.py  # Shell command execution tools
│   │   ├── gcp_tools.py      # GCP project management tools
│   │   └── time_tools.py     # Time-related tools
│
├── my_cli_agent/             # Direct API implementation
│   ├── agent.py              # Main agent implementation using direct APIs
│   ├── tools/                # Tool modules for direct API implementation
│   │   ├── __init__.py
│   │   ├── base.py           # Base classes for tools
│   │   ├── command_tools.py  # Shell command execution tools
│   │   ├── gcp_tools.py      # GCP project management tools
│   │   ├── terminal_tools.py # Terminal interaction tools
│   │   └── time_tools.py     # Time-related tools
│
├── run_agent.py              # Entry point for direct API implementation
├── run_adk_agent.py          # Entry point for ADK implementation
└── requirements.txt          # Project dependencies
```

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
