# Dokumen Arsitektur: Infrabot NLP Google Chat Bot

## 1. Pendahuluan

Dokumen ini menguraikan arsitektur teknis dari Infrabot NLP, sebuah chatbot yang dirancang untuk diintegrasikan dengan Google Chat. Arsitektur ini telah berevolusi dari aplikasi CLI menjadi layanan web yang kuat, modular, dan dapat diperluas, yang di-hosting di lingkungan *serverless*.

## 2. Prinsip Desain

Arsitektur ini dibangun di atas prinsip-prinsip berikut:

*   **Stateless:** Setiap permintaan dari Google Chat diperlakukan sebagai transaksi independen, membuat aplikasi sangat skalabel.
*   **Modularitas:** Fungsionalitas dipisahkan ke dalam lapisan yang berbeda (Presentasi, Logika Bisnis, Akses Layanan), memungkinkan pemeliharaan dan perluasan yang mudah.
*   **Ekstensibilitas:** Sistem "Tool" yang menjadi inti dari agen memungkinkan penambahan kemampuan baru (misalnya, integrasi MCP, library pihak ketiga) tanpa mengubah logika inti.
*   **Cloud-Native:** Dirancang dari awal untuk di-container-isasi dengan Docker dan di-deploy di platform *serverless* seperti Google Cloud Run.

## 3. Arsitektur Tingkat Tinggi

Sistem ini menggunakan arsitektur berbasis webhook. Google Chat mengirimkan event (pesan) sebagai permintaan HTTP POST ke endpoint publik yang di-hosting oleh Google Cloud Run. Aplikasi memproses permintaan ini, berinteraksi dengan berbagai layanan backend, dan mengembalikan respons dalam format yang dapat ditampilkan di ruang chat.

```
+-------------------+      +--------------------------------+      +------------------------+
| Google Chat User  | <--> |      Google Chat Platform      | <--> |   Infrabot Service     |
+-------------------+      +--------------------------------+      | (on Google Cloud Run)  |
                                                                   +-----------+------------+
                                                                               | (Webhook)
                                                                               |
                                     +-----------------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------------+
| Infrabot Container (Python/Flask/Gunicorn)                                   |
|                                                                              |
|  +------------------+      +-----------------------+      +------------------+
|  | app.py           | <--> | my_cli_agent/         | <--> | Tools & Services |
|  | (Web Endpoint)   |      | agent_new.py          |      | (MCPs, GCP, etc.)|
|  +------------------+      | (Orchestration Logic) |      +------------------+
|                            +-----------------------+                         |
|                                       |                                      |
|                                       v                                      |
|                            +-----------------------+                         |
|                            | my_cli_agent/         |                         |
|                            | providers/gemini.py   |                         |
|                            | (LLM Interaction)     |                         |
|                            +-----------------------+                         |
|                                                                              |
+------------------------------------------------------------------------------+
```

## 4. Komponen Utama

### 4.1. Lapisan Presentasi (`app.py`)

*   **Teknologi:** Flask, Gunicorn.
*   **Tanggung Jawab:**
    *   Menyediakan endpoint `POST /` untuk menerima webhook dari Google Chat.
    *   Melakukan verifikasi keamanan pada setiap permintaan untuk memastikan permintaan tersebut sah.
    *   Mem-parsing payload JSON dari Google Chat untuk mengekstrak pesan pengguna.
    *   Memanggil lapisan logika bisnis (`Agent`) dengan pesan yang telah dibersihkan.
    *   Memformat respons dari `Agent` ke dalam format JSON yang diharapkan oleh Google Chat.
    *   Menangani berbagai jenis event dari Google Chat (`MESSAGE`, `ADDED_TO_SPACE`, dll.).

### 4.2. Lapisan Logika Bisnis (`my_cli_agent/agent_new.py`)

*   **Teknologi:** Python.
*   **Tanggung Jawab:**
    *   Bertindak sebagai "otak" dari bot.
    *   Mengelola daftar *tools* yang tersedia.
    *   Menggunakan LLM (Google Gemini) untuk melakukan **seleksi tool**. Ini adalah langkah kunci di mana agen memutuskan apakah permintaan pengguna dapat dipenuhi oleh salah satu *tool* yang terdaftar.
    *   Mem-parsing argumen yang diperlukan untuk *tool* yang dipilih dari permintaan pengguna.
    *   Mengorkestrasi eksekusi *tool*.
    *   Jika tidak ada *tool* yang cocok, ia akan menghasilkan respons percakapan umum menggunakan LLM.

### 4.3. Lapisan Akses Layanan & Data (`my_cli_agent/tools/`)

*   **Teknologi:** Python, `requests`, library pihak ketiga (`markitdown`, `google-cloud-resource-manager`).
*   **Tanggung Jawab:**
    *   Mengabstraksi interaksi dengan layanan eksternal. Setiap file di direktori ini mewakili satu set kemampuan.
    *   **`command_tools.py`:** Berinteraksi dengan shell sistem lokal.
    *   **`gcp_tools.py`:** Berinteraksi dengan Google Cloud APIs.
    *   **`mcp_tools.py`, `sequential_thinking_tools.py`, `playwright_tools.py`:** Berinteraksi dengan server MCP eksternal melalui HTTP.
    *   **`markdown_tools.py`:** Berinteraksi dengan library `markitdown` lokal.
    *   Setiap *tool* bertanggung jawab untuk menangani logikanya sendiri, termasuk penanganan kesalahan, dan mengembalikan hasil dalam format `ToolResult` yang terstandardisasi.

## 5. Alur Data

1.  Pengguna mengirim pesan ke bot di Google Chat.
2.  Google Chat mengirimkan `POST` request ke URL layanan Cloud Run.
3.  `app.py` menerima dan memverifikasi permintaan.
4.  `app.py` meneruskan teks pesan ke `agent.handle_chat_message()`.
5.  `Agent` membuat prompt khusus untuk LLM, menanyakan *tool* mana (jika ada) yang harus digunakan.
6.  LLM merespons dengan nama *tool* dan argumennya.
7.  `Agent` memanggil fungsi *tool* yang sesuai dari direktori `tools/`.
8.  *Tool* dieksekusi (misalnya, melakukan panggilan API ke server MCP).
9.  *Tool* mengembalikan objek `ToolResult` (berisi sukses/gagal dan hasilnya).
10. `Agent` memformat hasil dari `ToolResult` menjadi string yang ramah-baca.
11. `app.py` membungkus string respons dalam format JSON Google Chat dan mengirimkannya kembali sebagai respons HTTP `200 OK`.
12. Google Chat menampilkan balasan bot kepada pengguna.

## 6. Pertimbangan Deployment

*   **Containerisasi:** `Dockerfile` mendefinisikan lingkungan runtime yang konsisten, menginstal semua dependensi, dan mengonfigurasi Gunicorn sebagai server WSGI produksi.
*   **Manajemen Konfigurasi:** Kunci API dan URL endpoint dikelola di luar kode. Untuk deployment produksi, ini disimpan dengan aman di Google Secret Manager dan di-mount ke layanan Cloud Run sebagai variabel lingkungan.
