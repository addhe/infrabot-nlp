# Infrabot NLP: Google Chat Bot Edition

## 1. Pendahuluan

**Infrabot NLP** adalah sebuah chatbot cerdas yang dirancang untuk diintegrasikan dengan Google Chat. Proyek ini mentransformasikan fungsionalitas dari *tool* CLI menjadi sebuah asisten kolaboratif, memungkinkan tim untuk berinteraksi dengan *tools*, layanan cloud, dan *workflow* otomasi yang kompleks langsung dari dalam ruang chat mereka.

Bot ini menggunakan Google Gemini untuk memahami bahasa alami dan secara dinamis memilih *tool* yang tepat untuk dieksekusi. Arsitekturnya yang modular dan dapat diperluas memungkinkannya untuk dengan mudah diintegrasikan dengan berbagai layanan eksternal (MCPs - Mission Control Planes).

## 2. Fitur Utama

- **Antarmuka Percakapan:** Berinteraksi dengan *tools* yang kompleks menggunakan bahasa alami di Google Chat.
- **Eksekusi Perintah Aman:** Menjalankan perintah shell dasar dari dalam chat.
- **Manajemen GCP:** Mendaftar dan membuat proyek Google Cloud.
- **Integrasi MCP Bawaan:**
  - **Zen MCP Server:** Untuk *workflow* pengembangan perangkat lunak yang kompleks seperti *code review*, *debugging*, dan perencanaan.
  - **Sequential Thinking:** Untuk memecahkan masalah yang memerlukan penalaran mendalam dan analisis langkah-demi-langkah.
  - **Playwright MCP:** Untuk otomasi browser, memungkinkan bot berinteraksi dengan situs web, mengisi formulir, dan melakukan scraping.
- **Konversi Dokumen:**
  - **Markitdown:** Mengonversi berbagai format file (PDF, DOCX, dll.) menjadi teks Markdown yang mudah dibaca.
- **Dapat Diperluas:** Arsitektur berbasis *tool* yang memudahkan penambahan kemampuan baru.

## 3. Arsitektur

Infrabot dirancang sebagai layanan web stateless yang di-container-isasi, ideal untuk deployment di platform *serverless* seperti Google Cloud Run.

- **Backend:** Python dengan Flask.
- **Model Bahasa:** Google Gemini.
- **Platform:** Docker, dirancang untuk Google Cloud Run.

## 4. Memulai (Deployment)

Bot ini dimaksudkan untuk di-deploy sebagai layanan web. Cara yang direkomendasikan adalah melalui Google Cloud Run.

### Prasyarat
- Proyek Google Cloud dengan penagihan aktif.
- `gcloud` CLI terinstal dan terotentikasi.
- Docker terinstal.
- API berikut diaktifkan di proyek GCP Anda: Cloud Build, Artifact Registry, Cloud Run.

### Langkah-langkah Deployment

1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/addhe/infrabot-nlp.git
    cd infrabot-nlp
    ```

2.  **Konfigurasi Lingkungan:**
    - Salin file `.env.example` ke `.env`:
      ```bash
      cp my_cli_agent/.env.example .env
      ```
    - Edit file `.env` dan isi dengan kredensial Anda:
      - `GOOGLE_API_KEY`: Kunci API Anda dari Google AI Studio.
      - `MCP_SERVER_URL`: URL ke instance Zen MCP Anda yang sedang berjalan.
      - `SEQ_THINKING_MCP_SERVER_URL`: URL ke instance Sequential Thinking Anda.
      - `PLAYWRIGHT_MCP_SERVER_URL`: URL ke instance Playwright MCP Anda.

3.  **Simpan Rahasia di Secret Manager:**
    Untuk keamanan, simpan konten file `.env` Anda di Google Secret Manager. Buat secret baru (misalnya, `infrabot-env`) dan tambahkan konten file `.env` sebagai versi secret.

4.  **Bangun dan Deploy:**
    Gunakan Google Cloud Build untuk membangun dan men-deploy aplikasi Anda dalam satu langkah. Perintah ini akan:
    - Membangun image Docker.
    - Mendorong image ke Artifact Registry.
    - Men-deploy image ke Cloud Run dengan secret yang telah Anda buat.

    ```bash
    gcloud run deploy infrabot-nlp \
      --source . \
      --region <YOUR_GCP_REGION> \
      --set-env-vars-from-secret infrabot-env:latest \
      --allow-unauthenticated
    ```
    - Ganti `<YOUR_GCP_REGION>` dengan region pilihan Anda (misalnya, `us-central1`).
    - `--allow-unauthenticated` diperlukan agar Google Chat dapat mengirim pesan ke webhook Anda.

5.  **Konfigurasi Google Chat:**
    - Setelah deployment berhasil, Cloud Run akan memberikan Anda **URL Layanan**.
    - Buka Google Cloud Console -> APIs & Services -> Credentials.
    - Aktifkan Google Chat API.
    - Di halaman konfigurasi Chat API, atur **App URL** ke URL Layanan Cloud Run Anda.
    - Tambahkan bot ke ruang Google Chat dan mulailah berinteraksi!

## 5. Struktur Proyek

Struktur proyek telah di-refactor untuk mendukung arsitektur layanan web:

```
├── app.py                    # Entry point aplikasi Flask
├── my_cli_agent/             # Logika inti agen
│   ├── __init__.py
│   ├── agent_new.py          # Kelas Agent utama
│   ├── models.py             # Model data (misalnya, ToolResult)
│   ├── providers/            # Penyedia LLM (hanya Gemini)
│   └── tools/                # Semua tool yang dapat dieksekusi
│       ├── command_tools.py
│       ├── gcp_tools.py
│       ├── markdown_tools.py
│       ├── mcp_tools.py
│       ├── playwright_tools.py
│       ├── sequential_thinking_tools.py
│       └── time_tools.py
│
├── tests/                    # Semua tes unit
│   └── unit/
│
├── Dockerfile                # Konfigurasi container
├── requirements.txt          # Dependensi Python
└── *.md                      # Dokumentasi proyek
```

## 6. Kontribusi

Kontribusi sangat diterima! Silakan ajukan Pull Request.

## 7. Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk detailnya.