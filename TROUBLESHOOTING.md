# Troubleshooting Guide / Panduan Penyelesaian Masalah

This document helps you identify and resolve common issues that may arise when using the Gemini-ChatGPT CLI application.

Dokumen ini bertujuan untuk membantu Anda mengidentifikasi dan menyelesaikan masalah umum yang mungkin timbul saat menggunakan aplikasi CLI Gemini-ChatGPT.

## System Requirements / Persyaratan Sistem
- Python 3.13+ / Python 3.13 ke atas
- macOS (primary) / macOS (utama)
- Linux/Windows (secondary) / Linux/Windows (sekunder)
- Virtual Environment / Lingkungan Virtual

## Table of Contents / Daftar Isi

1.  [Common Issues / Masalah Umum](#common-issues)
    *   [API Key Issues / Masalah Kunci API](#api-key-issues)
    *   [Python Virtual Environment Issues / Masalah Lingkungan Virtual Python](#python-virtual-environment-issues)
    *   [Dependency Installation Issues / Masalah Instalasi Dependensi](#dependency-installation-issues)
    *   [GCP Operation Issues / Masalah Operasi GCP](#gcp-operation-issues)
    *   [Google AI SDK Warnings / Peringatan SDK Google AI](#google-ai-sdk-warnings)
    *   [Connectivity Issues / Masalah Konektivitas](#connectivity-issues)
2.  [Masalah Spesifik Implementasi](#masalah-spesifik-implementasi)
    *   [Implementasi API Langsung](#implementasi-api-langsung)
    *   [Implementasi ADK](#implementasi-adk)
3.  [Masalah Docker](#masalah-docker)
4.  [Mendapatkan Bantuan Lebih Lanjut](#mendapatkan-bantuan-lebih-lanjut)

## 1. Masalah Umum

### Kesalahan Terkait Kunci API

**Gejala:**
*   Pesan error yang menyebutkan "API key invalid", "Authentication failed", "401 Unauthorized", atau sejenisnya.
*   Aplikasi gagal terhubung ke layanan AI (Gemini, OpenAI, Anthropic).

**Solusi:**
*   **Pastikan Kunci API Aktif:** Verifikasi bahwa kunci API Anda masih valid dan belum kedaluwarsa atau dicabut. Kunjungi dasbor penyedia layanan AI masing-masing:
    *   Google Gemini: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
    *   OpenAI: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
    *   Anthropic: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
*   **Variabel Lingkungan Sudah Benar:**
    *   Pastikan variabel lingkungan (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) sudah diatur dengan benar di terminal Anda atau di file `.env` (`my_cli_agent/.env`).
    *   Periksa ejaan nama variabel dan pastikan tidak ada spasi ekstra di sekitar kunci.
    *   Jika menggunakan file `.env`, pastikan file tersebut berada di direktori yang benar (`my_cli_agent/`) dan aplikasi dimuat dengan benar.
    *   Ingatlah untuk me-restart terminal atau memuat ulang file `.env` setelah melakukan perubahan.
*   **Kunci Sesuai Model:** Pastikan Anda menggunakan kunci API yang benar untuk model yang ingin Anda akses.

### Masalah Lingkungan Virtual Python

**Gejala:**
*   Error "ModuleNotFoundError" untuk paket yang seharusnya sudah terinstal.
*   Perintah `python` atau `pip` tidak ditemukan atau merujuk ke instalasi Python sistem global.

**Solusi:**
*   **Aktifkan Lingkungan Virtual:** Pastikan Anda telah mengaktifkan lingkungan virtual sebelum menjalankan aplikasi atau menginstal dependensi.
    ```bash
    source venv/bin/activate  # Untuk Linux/macOS
    .\venv\Scripts\activate    # Untuk Windows
    ```
    Anda akan melihat nama lingkungan virtual (misalnya, `(venv)`) di prompt terminal Anda jika sudah aktif.
*   **Instal Ulang di Lingkungan Virtual:** Jika Anda tidak sengaja menginstal paket secara global, nonaktifkan lingkungan virtual, aktifkan kembali, lalu instal ulang dependensi menggunakan `pip install -r requirements.txt`.

### Masalah Instalasi Dependensi

**Gejala:**
*   Error saat menjalankan `pip install -r requirements.txt`.
*   "ModuleNotFoundError" meskipun lingkungan virtual sudah aktif.

**Solusi:**
*   **Koneksi Internet:** Pastikan Anda memiliki koneksi internet yang stabil.
*   **Versi Pip dan Setuptools:** Coba perbarui `pip` dan `setuptools`:
    ```bash
    pip install --upgrade pip setuptools
    ```
*   **Dependensi Sistem:** Beberapa paket Python mungkin memerlukan dependensi tingkat sistem (misalnya, pustaka C). Periksa pesan error untuk petunjuk tentang pustaka yang hilang dan instal menggunakan manajer paket sistem Anda (misalnya, `apt`, `yum`, `brew`).
*   **File `requirements.txt` Benar:** Pastikan file `requirements.txt` tidak rusak dan berisi daftar paket yang valid.

### Masalah Terkait Operasi GCP

**Gejala:**
*   Error saat mencoba mencantumkan atau membuat proyek GCP.
*   Pesan yang berkaitan dengan "Permissions", "Credentials", atau "Authentication" untuk layanan Google Cloud.

**Solusi:**
*   **Google Cloud Application Default Credentials (ADC):** Pastikan Anda telah mengautentikasi menggunakan `gcloud` CLI:
    ```bash
    gcloud auth application-default login
    ```
    Ikuti petunjuk di browser untuk login dengan akun Google Anda yang memiliki izin yang diperlukan pada proyek GCP.
*   **Izin IAM:** Akun yang Anda gunakan untuk ADC harus memiliki peran IAM yang sesuai (misalnya, "Project Creator", "Project Viewer") untuk melakukan operasi yang diinginkan.
*   **Proyek GCP Dikonfigurasi:** Pastikan Anda telah mengkonfigurasi proyek default untuk `gcloud` jika diperlukan, atau bahwa aplikasi menggunakan ID proyek yang benar.

### Peringatan SDK Google AI

**Gejala:**
*   Anda melihat peringatan di konsol seperti: `"Default value is not supported in function declaration schema for Google AI"`.

**Solusi:**
*   Ini adalah masalah yang diketahui dengan Google AI SDK versi tertentu. **Peringatan ini umumnya tidak mempengaruhi fungsionalitas inti aplikasi** dan dapat diabaikan jika aplikasi tetap berjalan sesuai harapan. Pantau pembaruan SDK Google AI untuk perbaikan di masa mendatang.

### Masalah Konektivitas

**Gejala:**
*   Timeout saat mencoba menghubungi API model AI.
*   Error "Connection refused" atau sejenisnya.

**Solusi:**
*   **Periksa Koneksi Internet Anda:** Pastikan mesin Anda memiliki akses internet yang berfungsi.
*   **Firewall/Proxy:** Jika Anda berada di belakang firewall atau menggunakan proxy, pastikan konfigurasi jaringan Anda mengizinkan koneksi keluar ke endpoint API penyedia AI.
    *   Google: `*.googleapis.com`
    *   OpenAI: `api.openai.com`
    *   Anthropic: `api.anthropic.com`
*   **Status Layanan Penyedia AI:** Periksa halaman status penyedia AI untuk melihat apakah ada gangguan layanan yang diketahui.

## 2. Masalah Spesifik Implementasi

### Implementasi API Langsung (`run_agent.py`)

*   **Pemilihan Model:** Pastikan variabel lingkungan untuk ID model (misalnya, `GEMINI_MODEL_ID`, `OPENAI_MODEL_ID`, `CLAUDE_MODEL_ID`) diatur ke ID model yang valid dan didukung oleh kunci API Anda.
*   **Format Respons API:** Jika Anda memodifikasi kode untuk menangani respons API secara langsung, pastikan Anda menangani berbagai kode status HTTP dan format error dengan benar.

### Implementasi ADK (`run_adk_agent.py`)

*   **Dependensi ADK:** Pastikan semua dependensi spesifik ADK (jika ada, di luar `requirements.txt` utama) terinstal dengan benar.
*   **Konfigurasi Agen ADK:** Periksa `adk_cli_agent/agent.py` untuk konfigurasi agen yang mungkin spesifik untuk ADK.
*   **Masalah Kompatibilitas ADK:** ADK adalah teknologi yang lebih baru. Periksa dokumentasi resmi Google ADK untuk masalah kompatibilitas atau batasan yang diketahui.

## 3. Masalah Docker

**Gejala:**
*   Gagal membangun image Docker.
*   Container Docker keluar secara tak terduga.
*   Error saat menjalankan aplikasi di dalam container.

**Solusi:**
*   **Dockerfile:**
    *   Seperti yang disebutkan di `README.md`, `Dockerfile` mungkin perlu diperbarui untuk menggunakan entrypoint yang benar (`run_agent.py` atau `run_adk_agent.py`) bukan `gemini-bot.py`.
    *   Pastikan semua perintah `COPY` dan `RUN` di `Dockerfile` sudah benar dan dependensi diinstal di dalam image.
*   **Variabel Lingkungan untuk Docker:** Saat menjalankan container Docker, pastikan Anda meneruskan semua kunci API yang diperlukan dan variabel konfigurasi lainnya menggunakan flag `--env` atau file env:
    ```bash
    docker run -it --name your-container-name \
      --env GOOGLE_API_KEY=your-gemini-api-key \
      # ... variabel env lainnya ...
      infrabot-nlp:v1.0
    ```
*   **Log Container:** Periksa log container Docker untuk pesan error yang lebih detail:
    ```bash
    docker logs your-container-name
    ```
*   **Konektivitas Jaringan dari Dalam Docker:** Pastikan container Docker memiliki akses jaringan untuk mencapai API eksternal.

## 4. Mendapatkan Bantuan Lebih Lanjut

Jika panduan ini tidak menyelesaikan masalah Anda:

1.  **Periksa Pesan Error Secara Detail:** Pesan error seringkali memberikan petunjuk paling jelas tentang apa yang salah.
2.  **Aktifkan Logging (Jika Ada):** Jika aplikasi memiliki opsi logging yang lebih detail, aktifkan untuk mendapatkan lebih banyak informasi. (Saat ini, aplikasi ini menggunakan `print` untuk output, tetapi logging yang lebih formal bisa ditambahkan).
3.  **Sederhanakan Kasus Anda:** Coba isolasi masalah dengan menjalankan bagian terkecil dari fungsionalitas yang menyebabkan error.
4.  **Cari Isu Terbuka/Tertutup:** Periksa bagian "Issues" di repositori GitHub proyek untuk melihat apakah orang lain telah melaporkan masalah serupa.
5.  **Buat Isu Baru:** Jika Anda yakin ini adalah bug atau masalah yang belum didokumentasikan, buat isu baru di repositori GitHub. Sertakan informasi berikut:
    *   Langkah-langkah untuk mereproduksi masalah.
    *   Output error lengkap (salin-tempel sebagai teks).
    *   Versi Python yang Anda gunakan.
    *   Sistem operasi Anda.
    *   Implementasi mana yang Anda gunakan (`run_agent.py` atau `run_adk_agent.py`).
    *   Setiap perubahan yang telah Anda buat pada kode.