# Dokumen Persyaratan Produk: Infrabot-NLP

## 1. Pendahuluan

Infrabot-NLP adalah aplikasi Command Line Interface (CLI) yang dirancang untuk menyediakan antarmuka terpadu dan interaktif bagi pengembang dan insinyur operasi untuk memanfaatkan berbagai Model Bahasa Besar (LLM) untuk tugas-tugas terkait infrastruktur dan kueri umum. Tujuannya adalah untuk menyederhanakan interaksi dengan model AI dengan menyediakan pengalaman pengguna yang konsisten dan mengintegrasikan alat-alat yang berguna untuk kebutuhan operasional umum.

## Persyaratan Sistem

### Persyaratan Teknis
- Python 3.13 atau yang lebih baru
- macOS (platform utama yang didukung)
- Linux/Windows (platform dengan dukungan sekunder)
- RAM minimal 4GB, direkomendasikan 8GB
- Koneksi internet untuk mengakses API

### Dependensi
- Dependensi inti yang tercantum dalam requirements.txt
- Dependensi pengembangan yang tercantum dalam requirements-dev.txt
- Kunci API untuk penyedia AI yang didukung

## 2. Tujuan dan Sasaran

*   **Akses AI Terpadu**: Menyediakan satu CLI untuk berinteraksi dengan berbagai model AI terkemuka (misalnya, Google Gemini, seri OpenAI GPT, Anthropic Claude).
*   **Otomatisasi Tugas**: Memungkinkan pengguna untuk melakukan tugas-tugas tertentu seperti eksekusi perintah shell, manajemen sumber daya GCP, dan pencarian waktu melalui perintah bahasa alami yang diproses oleh AI.
*   **Peningkatan Produktivitas**: Meningkatkan alur kerja untuk pengembang dan SRE dengan mengintegrasikan bantuan AI langsung ke dalam lingkungan terminal mereka.
*   **Kemampuan Pengembangan**: Merancang sistem yang mudah diperluas dengan model AI baru dan alat/kemampuan baru.
*   **CLI yang Ramah Pengguna**: Menawarkan pengalaman baris perintah yang intuitif dan mudah digunakan.

## 3. Target Pengguna

*   **Pengembang Perangkat Lunak**: Untuk pencarian cepat, bantuan pembuatan/pemahaman kode, dan eksekusi skrip sederhana.
*   **Insinyur DevOps / SRE**: Untuk mengotomatisasi tugas infrastruktur, mengkueri sumber daya cloud, dan pemecahan masalah.
*   **Administrator Sistem**: Untuk mengelola sistem dan mengeksekusi perintah dengan bantuan AI.
*   **Pecinta AI**: Untuk mengeksplorasi dan membandingkan kemampuan berbagai LLM melalui antarmuka yang umum.

## 4. Persyaratan Fungsional

### 4.1. Interaksi AI Inti

*   **FR1.1 Dukungan Multi-Model**: Aplikasi harus mendukung interaksi dengan:
    *   Model Google Gemini Pro dan Gemini Ultra (melalui API langsung dan ADK)
    *   Model OpenAI GPT-4 Turbo dan GPT-3.5 Turbo (melalui API langsung)
    *   Model Anthropic Claude 3 dan Claude 2.1 (melalui API langsung)
*   **FR1.2 Input Bahasa Alami**: Pengguna harus dapat memasukkan kueri dan perintah dalam bahasa alami
*   **FR1.3 Tampilan Respons AI**: Aplikasi harus menampilkan respons dari model AI dengan jelas
*   **FR1.4 Fallback Model**: Menerapkan fallback otomatis ke model alternatif jika model utama tidak tersedia

### 4.2. Tool Integration


The application must support the following tools, callable via AI understanding of user intent:

*   **FR2.1 Shell Command Execution:**
    *   **FR2.1.1**: Allow users to request the execution of shell commands on the local system.
    *   **FR2.1.2**: Display the output (stdout, stderr) of the executed commands.
    *   **FR2.1.3**: Implement safety measures or confirmations for potentially destructive commands (Future consideration: User confirmation).
*   **FR2.2 Time Lookup:**
    *   **FR2.2.1**: Allow users to ask for the current time in specified cities or timezones.
*   **FR2.3 GCP Project Management (requires user authentication with GCP):**
    *   **FR2.3.1**: List GCP projects. Users shall be able to list all projects or filter them by environment (e.g., dev, stg, prod) if such tagging/naming conventions are used or if "all" is specified as the environment. The status of each project (e.g., [ACTIVE], [DELETE_REQUESTED]) must be shown in the listing.
    *   **FR2.3.2**: Create new GCP projects, allowing specification of project ID, name, and organization ID.
    *   **FR2.3.3**: Delete GCP projects. If a project is not active or already scheduled for deletion, the user must receive a clear explanation.
    *   **FR2.3.4 VPC Management:**
        *   **FR2.3.4.1**: Create new VPC networks in GCP projects, allowing specification of network name, subnet mode (auto or custom), and routing mode (global or regional).
        *   **FR2.3.4.2**: Create custom subnets within VPCs, specifying region, CIDR range, and private Google access settings.
            *   Support for any valid CIDR range (e.g., 10.0.0.0/24, 172.0.0.0/24)
            *   User-friendly error messages for common issues like overlapping CIDR ranges
            *   Fallback to CLI if API operations fail with appropriate error handling
        *   **FR2.3.4.3**: List existing VPC networks and their subnets in a specified project.
        *   **FR2.3.4.4**: Display detailed information about a specific VPC network, including its subnets, firewall rules, and peering connections.
        *   **FR2.3.4.5**: Delete a subnet from a VPC network, with user confirmation and robust error handling (including fallback to CLI if API fails).
        *   **FR2.3.4.6**: Enable or disable private Google access on existing subnets.
            *   Proper handling of subnet fingerprint to ensure API operations succeed
            *   Graceful fallback to CLI when API returns errors
            *   Clear error messages for permission issues or resource not found errors

        *   **FR2.3.4.7**: Delete all subnets in a VPC network and then delete the VPC itself, with user confirmation and robust error handling. The workflow must:
            *   Prompt the user for confirmation before deleting all subnets and the VPC.
            *   Optionally allow confirmation for each subnet deletion.
            *   Abort the VPC deletion if any subnet deletion fails (unless cancelled by user).
            *   Provide user-friendly error messages for common scenarios (e.g., VPC still in use, permission denied, resource not found)
            *   Fallback to CLI if API operations fail

        **VPC Deletion Workflow Note:**
        When deleting a VPC network, the system will first attempt to delete all subnets within the VPC. Only after all subnets are successfully deleted will the VPC itself be deleted. The user will be prompted for confirmation before proceeding, and may be prompted for each subnet if desired. If any subnet cannot be deleted, the VPC deletion will be aborted and the user will be notified of the error(s). The system provides clear error messages for common scenarios like attempting to delete a VPC that is still in use by resources.

### 4.3. Configuration

*   **FR3.1 API Key Management**: Users must be able to configure API keys for the different AI services.
    *   Support for environment variables.
    *   Support for `.env` files.
*   **FR3.2 Model ID Configuration**: Users should be able to specify preferred model IDs for each provider (e.g., `gpt-4-turbo-preview`, `gemini-1.5-pro-latest`).

### 4.4. User Interface (CLI)

*   **FR4.1 Interactive Prompt**: The application shall provide an interactive prompt for user input.
*   **FR4.2 Clear Instructions**: Provide clear instructions on how to start, use, and exit the application.
*   **FR4.3 Exit Command**: A dedicated command (e.g., `exit()`) to terminate the application gracefully.

## 5. Non-Functional Requirements

*   **NFR1.1 Performance**:
    *   Responses from AI models should be streamed or returned within a reasonable time frame, acknowledging that AI processing time is a factor.
    *   Local tool execution (e.g., shell commands) should be near-instantaneous.
*   **NFR1.2 Reliability**:
    *   The application should handle API errors gracefully (e.g., network issues, invalid API keys) and provide informative messages to the user.
    *   The application should attempt to fall back to alternative methods (e.g., CLI commands) when API operations fail.
    *   All operations must include comprehensive error handling with user-friendly error messages.
    *   The application should be stable and not crash unexpectedly.
*   **NFR1.3 Usability**:
    *   The CLI should be intuitive and easy to learn.
    *   Error messages should be clear, actionable, and specific to the operation being performed.
    *   User feedback should be provided for long-running operations.
    *   Documentation (`README.md`, etc.) should be comprehensive.
*   **NFR1.4 Security**:
    *   API keys must be handled securely, not hardcoded, and primarily managed through environment variables or git-ignored `.env` files.
    *   Caution should be advised for executing shell commands, with potential future enhancements for user confirmation on sensitive operations.
*   **NFR1.5 Maintainability**:
    *   Code should be well-structured, modular, and follow defined coding standards (`CODING_STYLE.md`).
    *   Easy to debug and update.
*   **NFR1.6 Extensibility**:
    *   The architecture should allow for the addition of new AI model providers with minimal changes to the core system.
    *   The architecture should allow for the easy addition of new tools and capabilities.
*   **NFR1.7 Installation**:
    *   The installation process using `pip` and a virtual environment should be straightforward.
    *   Docker-based deployment should be supported and functional.

## 6. Future Considerations / Potential Roadmap

*   **FC1. Advanced Context Management**: More sophisticated session history and context management.
*   **FC2. Tool Discovery**: Mechanism for AI to discover available tools and their usage.
*   **FC3. User Confirmation for Sensitive Operations**: Implement a confirmation step before executing potentially destructive shell commands or creating/modifying cloud resources.
*   **FC4. Plugin Architecture for Tools**: A more formal plugin system for adding new tools.
*   **FC5. Support for More Cloud Providers**: Extend toolset to support other cloud providers (e.g., AWS, Azure).
*   **FC6. GUI Interface**: A web-based or desktop GUI as an alternative to the CLI.
*   **FC7. More Sophisticated GCP Tools**: Tools for managing other GCP resources (e.g., GCE instances, GCS buckets).
*   **FC8. Output Formatting**: Allow users to specify output formats for tool results (e.g., JSON, YAML, table).
*   **FC9. Logging and Auditing**: Enhanced logging for debugging and auditing user commands and AI interactions.
*   **FC10. Testing Framework**: Comprehensive unit and integration tests.
*   **FC11. Enhanced VPC Management**: Advanced VPC features including:
    *   Firewall rule management for VPC networks
    *   VPC Network Peering configuration
    *   Cloud NAT setup for private instances
    *   Shared VPC configuration across projects
    *   VPC Service Controls integration for security boundaries

## 7. Implementation Status and Recent Improvements

As of June 2025, the following key improvements have been implemented:

### 7.1 GCP VPC Management Enhancements

*   **Improved Error Handling**: 
    *   Comprehensive error detection and user-friendly messages across all VPC and subnet operations
    *   Specific error handling for common scenarios (e.g., resources in use, permission denied, invalid CIDR ranges)
    *   Structured try/except blocks for both API and CLI approaches

*   **Fixed API Operations**:
    *   Added proper fingerprint handling for subnet updates to resolve the "Required field 'resource.fingerprint' not specified" error
    *   Ensured proper fallback from API to CLI when API operations fail
    *   Enhanced verification of operation results

*   **User Experience Improvements**:
    *   More informative error messages that explain what went wrong and suggest solutions
    *   Better handling of edge cases like overlapping CIDR ranges or resources in use
    *   Improved validation and confirmation workflows

*   **Code Structure Improvements**:
    *   Resolved circular import issues by moving utility functions to appropriate modules
    *   Enhanced test coverage and fixed test failures
    *   Better modularization of functionality

These improvements aim to provide a more robust, reliable, and user-friendly experience when working with GCP VPC resources melalui CLI Infrabot-NLP.