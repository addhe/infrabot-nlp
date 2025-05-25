# Configuration Guide for Gemini-ChatGPT CLI

This guide provides detailed instructions on how to configure the Gemini-ChatGPT CLI application. Proper configuration is essential for the application to interact with the various AI models and cloud services it supports.

## Table of Contents

1.  [Prerequisites](#prerequisites)
2.  [API Keys](#api-keys)
    *   [Google Gemini API Key](#google-gemini-api-key)
    *   [OpenAI API Key](#openai-api-key)
    *   [Anthropic API Key](#anthropic-api-key)
3.  [Google Cloud Configuration](#google-cloud-configuration)
    *   [Application Default Credentials (ADC)](#application-default-credentials-adc)
4.  [Environment Variables](#environment-variables)
    *   [Setting Environment Variables](#setting-environment-variables)
        *   [Option A: Direct Export](#option-a-direct-export)
        *   [Option B: Using a `.env` File](#option-b-using-a-env-file)
    *   [Required Environment Variables](#required-environment-variables)
    *   [Optional Environment Variables](#optional-environment-variables)
5.  [Model Configuration](#model-configuration)
    *   [Default Model IDs](#default-model-ids)
    *   [Customizing Model IDs](#customizing-model-ids)
6.  [Docker Configuration](#docker-configuration)

## 1. Prerequisites

Before configuring the application, ensure you have:
*   Python 3.13 or later installed (recommended for optimal performance).
*   Access to the necessary AI provider accounts (Google, OpenAI, Anthropic).
*   Google Cloud SDK installed if you plan to use GCP-related features.
*   Operating system compatibility:
    * Fully tested on macOS
    * Compatible with Linux and Windows (some features may require additional setup)

## 2. API Keys

The application requires API keys to authenticate with the AI service providers.

### Google Gemini API Key
*   **Purpose**: Required for interacting with Google's Gemini models.
*   **How to obtain**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to create or retrieve your API key.
*   **Environment Variable**: `GOOGLE_API_KEY`

### OpenAI API Key
*   **Purpose**: Optional, required only if you intend to use OpenAI's GPT models via the direct API implementation.
*   **How to obtain**: Visit the [OpenAI API keys page](https://platform.openai.com/api-keys).
*   **Environment Variable**: `OPENAI_API_KEY`

### Anthropic API Key
*   **Purpose**: Optional, required only if you intend to use Anthropic's Claude models via the direct API implementation.
*   **How to obtain**: Visit the [Anthropic Console settings](https://console.anthropic.com/settings/keys).
*   **Environment Variable**: `ANTHROPIC_API_KEY`

## 3. Google Cloud Configuration

### Application Default Credentials (ADC)
*   **Purpose**: Required for operations involving Google Cloud Platform (GCP), such as listing or creating GCP projects.
*   **How to set up**:
    ```bash
    gcloud auth application-default login
    ```
    This command authenticates your local environment to access Google Cloud services.

## 4. Environment Variables

The application uses environment variables to store sensitive information like API keys and to customize its behavior.

### Setting Environment Variables

You can set up your environment variables using one of the following methods:

#### Option A: Direct Export
Set the variables directly in your shell session or add them to your shell's profile file (e.g., `.bashrc`, `.zshrc`).

```bash
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"  # Optional
export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"  # Optional

# Optional model IDs
export GEMINI_MODEL_ID="gemini-1.5-flash-latest" # Or your preferred Gemini model
export OPENAI_MODEL_ID="gpt-4-turbo-preview" # Or your preferred OpenAI model
export CLAUDE_MODEL_ID="claude-3-opus-20240229" # Or your preferred Claude model
```
Replace `"YOUR_..._API_KEY"` with your actual keys.

#### Option B: Using a `.env` File
This method is recommended for development as it keeps your keys out of your shell history and makes it easier to manage different configurations. The `.env` file should be placed in the `my_cli_agent/` directory.

1.  Copy the example environment file:
    ```bash
    cp my_cli_agent/.env.example my_cli_agent/.env
    ```
2.  Edit the `my_cli_agent/.env` file with your actual API keys and desired model IDs:
    ```dotenv
    # my_cli_agent/.env
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"

    # Optional: Specify model IDs
    GEMINI_MODEL_ID="gemini-1.5-flash-latest"
    OPENAI_MODEL_ID="gpt-4-turbo-preview"
    CLAUDE_MODEL_ID="claude-3-opus-20240229"
    ```
    **Note**: The `my_cli_agent/.env` file is included in `.gitignore` to prevent accidental commits of sensitive information.

### Required Environment Variables
*   `GOOGLE_API_KEY`: Your API key for Google Gemini.

### Optional Environment Variables
*   `OPENAI_API_KEY`: Your API key for OpenAI models. Needed if using OpenAI models.
*   `ANTHROPIC_API_KEY`: Your API key for Anthropic models. Needed if using Anthropic models.
*   `GEMINI_MODEL_ID`: Specifies the Gemini model to use. Defaults to a predefined value if not set.
*   `OPENAI_MODEL_ID`: Specifies the OpenAI model to use. Defaults to a predefined value if not set.
*   `CLAUDE_MODEL_ID`: Specifies the Anthropic Claude model to use. Defaults to a predefined value if not set.

## 5. Model Configuration

The application allows you to specify which AI models to use.

### Default Model IDs
If no specific model IDs are provided via environment variables, the application will use default models. These defaults are typically recent and capable models from each provider.
*   Gemini: `gemini-1.5-flash-latest` (or similar, check `my_cli_agent/providers/google_vertexai_provider.py` or `adk_cli_agent/agent.py` for defaults)
*   OpenAI: `gpt-4-turbo-preview` (or similar, check `my_cli_agent/providers/openai_provider.py`)
*   Claude: `claude-3-opus-20240229` (or similar, check `my_cli_agent/providers/anthropic_provider.py`)

### Customizing Model IDs
You can override the default model IDs by setting the corresponding environment variables:
*   `GEMINI_MODEL_ID`
*   `OPENAI_MODEL_ID`
*   `CLAUDE_MODEL_ID`

Refer to the documentation of each AI provider for a list of available model IDs.

## 6. Docker Configuration

When running the application using Docker, you need to pass the environment variables to the container at runtime.

```bash
docker run -it --name your-container-name \
  --env GOOGLE_API_KEY="your-gemini-api-key" \
  --env OPENAI_API_KEY="your-openai-api-key" \  # Optional
  --env ANTHROPIC_API_KEY="your-anthropic-api-key" \  # Optional
  # You can also pass model ID environment variables here
  # --env GEMINI_MODEL_ID="gemini-pro" \
  infrabot-nlp:v1.0 # Or your image tag
```

Replace `"your-..."` with your actual keys and desired model IDs.

This concludes the configuration guide. With these settings in place, you should be able to run the Gemini-ChatGPT CLI application and utilize its features. For troubleshooting, refer to `TROUBLESHOOTING.md` or the main `README.md`.