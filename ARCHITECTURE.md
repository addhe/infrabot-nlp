# Dokumen Arsitektur: Gemini-ChatGPT CLI

## 1. Pendahuluan

Dokumen ini menguraikan arsitektur aplikasi Gemini-ChatGPT CLI yang ditargetkan untuk lingkungan Python 3.13+. Aplikasi ini menyediakan antarmuka baris perintah terpadu untuk berinteraksi dengan berbagai model AI, termasuk Gemini dari Google, model GPT dari OpenAI, dan Claude dari Anthropic. Aplikasi ini mendukung berbagai fungsi seperti mengeksekusi perintah shell, mengambil waktu, dan mengelola proyek GCP.

## Persyaratan Sistem

- Python 3.13 atau yang lebih baru
- Dukungan utama untuk macOS
- Dukungan sekunder untuk Linux dan Windows
- Dependensi yang diperlukan seperti yang ditentukan dalam requirements.txt
- Dependensi pengembangan seperti yang ditentukan dalam requirements-dev.txt

## 2. Arsitektur Tingkat Tinggi

Aplikasi ini mengikuti arsitektur modular, terutama dibagi menjadi dua strategi implementasi utama:

1.  **Implementasi API Langsung**: Berinteraksi langsung dengan API penyedia AI masing-masing.
2.  **Implementasi ADK (Agent Development Kit)**: Memanfaatkan ADK Google untuk pengalaman yang lebih terintegrasi dengan Gemini, memanfaatkan kemampuan spesifiknya.

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

## 3. Komponen Utama

### 3.1. Antarmuka CLI (`run_agent.py`, `run_adk_agent.py`)

*   **Tujuan**: Titik masuk untuk aplikasi. Mereka menangani masukan pengguna, menginisialisasi agen yang sesuai, dan mengelola loop interaksi utama.
*   **Tanggung Jawab**:
    *   Mengurai argumen baris perintah (jika ada).
    *   Memuat variabel lingkungan dan konfigurasi (misalnya, kunci API).
    *   Membuat instance agen yang dipilih (API Langsung atau ADK).
    *   Memproses perintah pengguna dan menampilkan respons.
    *   Menangani kondisi keluar.

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