# Panduan Konfigurasi Gemini-ChatGPT CLI

Panduan ini memberikan petunjuk rinci tentang cara mengonfigurasi aplikasi Gemini-ChatGPT CLI. Konfigurasi yang tepat sangat penting agar aplikasi dapat berinteraksi dengan berbagai model AI dan layanan cloud yang didukung.

## Daftar Isi

1.  [Prasyarat](#prasyarat)
2.  [Kunci API](#kunci-api)
    *   [Kunci API Google Gemini](#kunci-api-google-gemini)
    *   [Kunci API OpenAI](#kunci-api-openai)
    *   [Kunci API Anthropic](#kunci-api-anthropic)
3.  [Konfigurasi Google Cloud](#konfigurasi-google-cloud)
    *   [Kredensial Default Aplikasi (ADC)](#kredensial-default-aplikasi-adc)
    *   [Status Project GCP](#status-project-gcp)
4.  [Variabel Lingkungan](#variabel-lingkungan)
    *   [Mengatur Variabel Lingkungan](#mengatur-variabel-lingkungan)
        *   [Opsi A: Ekspor Langsung](#opsi-a-ekspor-langsung)
        *   [Opsi B: Menggunakan File `.env`](#opsi-b-menggunakan-file-env)
    *   [Variabel Lingkungan yang Diperlukan](#variabel-lingkungan-yang-diperlukan)
    *   [Variabel Lingkungan Opsional](#variabel-lingkungan-opsional)
5.  [Konfigurasi Model](#konfigurasi-model)
    *   [ID Model Default](#id-model-default)
    *   [Menyesuaikan ID Model](#menyesuaikan-id-model)
6.  [Konfigurasi Docker](#konfigurasi-docker)

## 1. Prasyarat

Sebelum mengonfigurasi aplikasi, pastikan Anda memiliki:
*   Python 3.13 atau yang lebih baru terinstal (direkomendasikan untuk performa optimal).
*   Akses ke akun penyedia AI yang diperlukan (Google, OpenAI, Anthropic).
*   Google Cloud SDK terinstal jika Anda berencana menggunakan fitur terkait GCP.
*   Kompatibilitas sistem operasi:
    * Sudah diuji sepenuhnya di macOS
    * Kompatibel dengan Linux dan Windows (beberapa fitur mungkin memerlukan pengaturan tambahan)

## 2. Kunci API

Aplikasi memerlukan kunci API untuk mengautentikasi dengan penyedia layanan AI.

### Kunci API Google Gemini
*   **Tujuan**: Diperlukan untuk berinteraksi dengan model Gemini dari Google.
*   **Cara Mendapatkan**: Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey) untuk membuat atau mengambil kunci API Anda.
*   **Variabel Lingkungan**: `GOOGLE_API_KEY`

### Kunci API OpenAI
*   **Tujuan**: Opsional, hanya diperlukan jika Anda bermaksud menggunakan model GPT dari OpenAI melalui implementasi API langsung.
*   **Cara Mendapatkan**: Kunjungi [halaman kunci API OpenAI](https://platform.openai.com/api-keys).
*   **Variabel Lingkungan**: `OPENAI_API_KEY`

### Kunci API Anthropic
*   **Tujuan**: Opsional, hanya diperlukan jika Anda bermaksud menggunakan model Claude dari Anthropic melalui implementasi API langsung.
*   **Cara Mendapatkan**: Kunjungi [pengaturan Konsol Anthropic](https://console.anthropic.com/settings/keys).
*   **Environment Variable**: `ANTHROPIC_API_KEY`

## 3. Google Cloud Configuration

### Application Default Credentials (ADC)
*   **Purpose**: Required for operations involving Google Cloud Platform (GCP), such as listing or creating GCP projects.
*   **How to set up**:
    ```bash
    gcloud auth application-default login
    ```
    This command authenticates your local environment to access Google Cloud services.

### Status Project GCP

Ketika Anda menjalankan perintah list project GCP, status project (misal: [ACTIVE], [DELETE_REQUESTED]) akan ditampilkan di samping nama project. Jika Anda mencoba menghapus project yang tidak aktif, aplikasi akan memberikan pesan yang jelas.

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

### Variabel Lingkungan yang Diperlukan
*   `GOOGLE_API_KEY`: Kunci API Anda untuk Google Gemini.

### Variabel Lingkungan Opsional
*   `OPENAI_API_KEY`: Kunci API Anda untuk model OpenAI. Diperlukan jika menggunakan model OpenAI.
*   `ANTHROPIC_API_KEY`: Kunci API Anda untuk model Anthropic. Diperlukan jika menggunakan model Anthropic.
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