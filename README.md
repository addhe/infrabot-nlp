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
├── my_cli_agent/             # Logika inti agen
│   ├── __init__.py
│   ├── app.py                  # Entry point aplikasi Flask
│   ├── agent_new.py          # Kelas Agent utama
│   ├── models.py             # Model data (Tool, ToolResult)
│   ├── providers/            # Penyedia LLM dan Tool
│   │   ├── gemini.py
│   │   └── mcp.py            # <-- Provider untuk MCP Tools
│   └── tools/                # Tool-tool individual
│       ├── command_tools.py
│       ├── gcp_tools.py
│       ├── markdown_tools.py
│       ├── playwright_tools.py # (Contoh tool yang lebih kompleks)
│       └── tool_utils.py     # <-- Helper untuk MCP Tools
│
├── tests/                    # Semua tes unit
│   └── unit/
│
├── Dockerfile                # Konfigurasi container
├── requirements.txt          # Dependensi Python
└── *.md                      # Dokumentasi proyek
```

## 6. Menambahkan Tools Baru (MCP)

Sistem ini dirancang agar mudah diperluas, terutama untuk menambahkan *tool* baru yang berinteraksi dengan server MCP (Mission Control Plane) berbasis HTTP POST.

Untuk menambahkan *tool* MCP baru yang mengikuti pola "prompt-in, response-out" sederhana:

1.  **Buka file `my_cli_agent/providers/mcp.py`**.
2.  **Tambahkan definisi baru** ke dalam list `MCP_TOOL_DEFINITIONS`. Setiap definisi adalah sebuah dictionary yang berisi:
    *   `name`: Nama unik untuk *tool* Anda (misalnya, `call_my_new_mcp`).
    *   `description`: Penjelasan tentang apa yang dilakukan oleh *tool* ini. Penjelasan ini sangat penting karena akan digunakan oleh model AI untuk memutuskan kapan harus menggunakan *tool* tersebut.
    *   `env_var`: Nama variabel lingkungan (environment variable) yang akan menyimpan URL endpoint untuk server MCP Anda (misalnya, `MY_NEW_MCP_URL`).
3.  **Tambahkan variabel lingkungan baru** ke dalam file konfigurasi `.env` Anda, dengan URL yang sesuai.

**Contoh Penambahan Tool Baru:**

Misalkan Anda ingin menambahkan *tool* untuk menganalisis data cuaca. Anda cukup menambahkan dictionary berikut ke list `MCP_TOOL_DEFINITIONS`:

```python
# di dalam my_cli_agent/providers/mcp.py

MCP_TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    # ... definisi yang sudah ada ...
    {
        "name": "call_weather_mcp",
        "description": "Mengirimkan permintaan ke server cuaca untuk mendapatkan analisis cuaca terkini berdasarkan lokasi.",
        "env_var": "WEATHER_MCP_URL",
    },
]
```

Setelah itu, tambahkan `WEATHER_MCP_URL=http://your-weather-service.com/api` ke file `.env` Anda. Agen akan secara otomatis mengenali dan dapat menggunakan *tool* baru ini tanpa perlu mengubah kode inti lainnya.

## 7. Kontribusi

Kontribusi sangat diterima! Silakan ajukan Pull Request.

## 7. Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk detailnya.