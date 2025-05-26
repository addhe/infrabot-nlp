# Ikhtisar Modul

Dokumen ini memberikan gambaran umum tentang modul dan komponen kunci dalam proyek `infrabot-nlp`.

## Persyaratan Sistem

- Python 3.13 atau yang lebih baru
- macOS (platform utama yang didukung)
- Linux/Windows (platform dengan dukungan sekunder)

## Implementasi Inti

Proyek ini menawarkan dua implementasi utama untuk berinteraksi dengan model AI:

1.  **Implementasi API Langsung (`my_cli_agent/`)**: Implementasi ini berinteraksi langsung dengan API dari berbagai penyedia AI (Google Gemini, OpenAI GPT, Anthropic Claude).
2.  **Implementasi ADK (`adk_cli_agent/`)**: Implementasi ini memanfaatkan Agent Development Kit (ADK) dari Google untuk pengalaman yang lebih baik dan terintegrasi, terutama dengan model Gemini dari Google.

## Struktur Direktori dan File Utama

### 1. `my_cli_agent/` - Implementasi API Langsung

Direktori ini berisi kode untuk agen interaksi API langsung.

*   **`agent.py`**: Implementasi agen utama dengan fungsionalitas inti
*   **`agent_new.py`**: Implementasi agen yang ditingkatkan dengan fitur dan pengoptimalan tambahan
*   **`models.py`**: Model Pydantic untuk penanganan permintaan/respons dan definisi alat
*   **`providers/`**: Implementasi penyedia model AI
    *   `anthropic.py`: Integrasi API Anthropic Claude
    *   `base.py`: Antarmuka penyedia dasar dan utilitas umum
    *   `gemini.py`: Integrasi API Google Gemini
    *   `openai.py`: Integrasi API OpenAI GPT
*   **`tools/`**: Implementasi kemampuan agen
    *   `base.py`: Kelas dan antarmuka alat dasar
    *   `command_tools.py`: Alat eksekusi perintah shell
    *   `gcp_tools.py`: Alat integrasi Google Cloud Platform
    *   `terminal_tools.py`: Utilitas interaksi terminal
    *   `time_tools.py`: Fungsi terkait waktu

### 2. `adk_cli_agent/` - Implementasi ADK

Direktori ini berisi kode untuk agen yang dibangun menggunakan Agent Development Kit (ADK) Google.

*   **`agent.py`**: Implementasi agen utama yang memanfaatkan fungsionalitas ADK. Ini melibatkan definisi perilaku agen, alat, dan alur interaksi sesuai dengan kerangka kerja ADK.
*   **`tools/`**: Mirip dengan implementasi API langsung, sub-direktori ini berisi modul alat, tetapi dirancang khusus dan terintegrasi untuk digunakan dengan ADK.
    *   `__init__.py`
    *   `command_tools.py`: Alat yang kompatibel dengan ADK untuk eksekusi perintah shell.
    *   `gcp_tools.py`: Alat yang kompatibel dengan ADK untuk interaksi GCP.
    *   `time_tools.py`: Alat yang kompatibel dengan ADK untuk informasi terkait waktu.

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