# Technical Design Document: Infrabot NLP Google Chat Bot

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Penulis Teknis:** Gemini CLI Agent

---

## 1. Pendahuluan dan Tujuan

Dokumen ini menyediakan desain teknis terperinci untuk proyek transformasi Infrabot NLP dari aplikasi Command-Line Interface (CLI) menjadi chatbot yang terintegrasi dengan Google Chat. Tujuannya adalah untuk memberikan panduan implementasi yang jelas bagi para developer, mencakup arsitektur sistem, komponen utama, alur data, dan strategi deployment.

Dokumen ini mengasumsikan pembaca telah memahami persyaratan yang diuraikan dalam BRD dan PRD.

## 2. Arsitektur Sistem Tingkat Tinggi

Sistem akan mengadopsi arsitektur berbasis webhook yang *serverless*, di-hosting di Google Cloud Run. Arsitektur ini memastikan skalabilitas, ketersediaan tinggi, dan biaya yang efisien karena hanya berjalan saat ada permintaan.

### Diagram Arsitektur:

```
[Google Chat User] <--> [Google Chat UI]
       |
       | (1. User sends message @Infrabot)
       v
[Google Chat API]
       |
       | (2. POST request with JSON payload to Webhook)
       v
[Google Cloud Run Service]
  |
  |-- [Container: Python + Gunicorn]
  |     |
  |     |-- [app.py: Flask Web Server] -- (3. Receives & Verifies Request)
  |     |      |
  |     |      | (4. Calls Agent logic)
  |     |      v
  |     |-- [my_cli_agent/agent_new.py: Agent Core]
  |     |      |
  |     |      | (5. Interacts with LLM & Tools)
  |     |      |
  |     |      +------> [LLM Provider (Gemini API)]
  |     |      |
  |     |      +------> [Tools (command, gcp, time)]
  |     |
  |     | (6. Returns formatted string response)
  |     v
  |-- [app.py: Flask Web Server] -- (7. Wraps response in Chat JSON format)
  |
  v
[Google Chat API] -- (8. Receives 200 OK with JSON response)
       |
       v
[Google Chat UI] -- (9. Displays bot's message)
```

### Komponen Utama:

1.  **Google Chat API:** Bertindak sebagai antarmuka antara pengguna dan layanan bot kita.
2.  **Google Cloud Run:** Platform hosting *serverless* yang akan menjalankan container Docker aplikasi kita.
3.  **Flask Web Service (`app.py`):** Titik masuk aplikasi. Bertanggung jawab untuk menerima permintaan HTTP dari Google Chat, memverifikasinya, dan mengembalikan respons yang diformat.
4.  **Agent Core (`my_cli_agent/agent_new.py`):** Otak dari aplikasi. Berisi logika untuk berinteraksi dengan LLM (Gemini) dan mengeksekusi *tools* yang sesuai.
5.  **Tool Modules (`my_cli_agent/tools/`):** Kumpulan fungsi Python yang dapat dieksekusi oleh agen. Ini termasuk *tools* sederhana (seperti `execute_command`) dan klien untuk layanan yang lebih kompleks (seperti server MCP Playwright dan Zen).
6.  **LLM Provider (`my_cli_agent/providers/`):** Modul yang bertanggung jawab untuk berkomunikasi dengan API model bahasa (Gemini).

## 3. Desain Komponen Terperinci

### 3.1. Flask Web Service (`app.py`)

*   **File:** `app.py` (akan dibuat di direktori root).
*   **Framework:** Flask.
*   **Endpoint:** Akan ada satu endpoint utama: `POST /`.
*   **Logika Endpoint:**
    1.  **Verifikasi Permintaan:** Setiap permintaan masuk dari Google Chat akan menyertakan `Authorization` header dengan Bearer Token (JWT). Endpoint harus memverifikasi token ini menggunakan pustaka klien Google API untuk memastikan permintaan tersebut sah dan berasal dari Google. Ini mencegah penyalahgunaan webhook.
    2.  **Parsing Payload:** Jika verifikasi berhasil, endpoint akan mem-parsing body JSON dari permintaan untuk mengekstrak konten pesan (`event.message.text`), ID ruang (`event.space.name`), dan informasi relevan lainnya.
    3.  **Inisialisasi Agen:** Satu instance dari `Agent` akan diinisialisasi saat aplikasi dimulai untuk digunakan kembali di seluruh permintaan.
    4.  **Pemanggilan Logika Inti:** Teks pesan akan diteruskan ke metode baru di dalam kelas `Agent`, yaitu `handle_chat_message(prompt)`.
    5.  **Pemformatan Respons:** String yang dikembalikan oleh `handle_chat_message` akan dibungkus dalam struktur JSON yang diharapkan oleh Google Chat API. Contoh: `{"text": "Ini adalah hasil dari perintah Anda..."}`.
    6.  **Pengembalian Respons:** Mengembalikan objek JSON ini dengan status HTTP `200 OK`.

### 3.2. Refactoring Agent Core (`my_cli_agent/agent_new.py`)

Logika agen yang ada dirancang untuk sesi CLI interaktif dan stateful. Ini harus diadaptasi untuk lingkungan web yang stateless.

*   **Metode Baru: `handle_chat_message(self, prompt: str) -> str`**
    *   Metode ini akan ditambahkan ke kelas `Agent`.
    *   Tujuannya adalah untuk menjadi *entry point* baru untuk permintaan yang berasal dari web.
    *   Logikanya akan sangat mirip dengan `process_with_tools`, tetapi dengan perubahan kunci:
        *   **Tidak ada `print()`:** Semua output yang sebelumnya dicetak ke konsol (hasil *tool*, pesan kesalahan) sekarang harus ditangkap sebagai string.
        *   **Return Value:** Metode ini harus mengembalikan satu string tunggal yang berisi respons akhir untuk ditampilkan kepada pengguna.
        *   **Penanganan Kesalahan:** *Exception* harus ditangkap dan diubah menjadi pesan kesalahan yang ramah pengguna dalam string yang dikembalikan.
*   **Manajemen State:** Untuk v1.0, setiap panggilan ke `handle_chat_message` akan bersifat *stateless*. Riwayat percakapan tidak akan dipertahankan di antara permintaan. Objek `self.history` dan `self.conversation` akan diinisialisasi ulang untuk setiap permintaan atau diabaikan.

## 4. Alur Data (End-to-End)

Berikut adalah alur data langkah-demi-langkah untuk satu interaksi:

1.  **Input Pengguna:** Pengguna mengetik `@Infrabot list gcp projects in dev` di Google Chat.
2.  **Webhook Trigger:** Google Chat mengirimkan permintaan `POST` ke URL Cloud Run yang telah dikonfigurasi.
3.  **Verifikasi:** `app.py` menerima permintaan dan memverifikasi Bearer Token di header.
4.  **Ekstraksi:** `app.py` mengekstrak teks: `"list gcp projects in dev"`.
5.  **Pemrosesan Agen:** `app.py` memanggil `agent.handle_chat_message("list gcp projects in dev")`.
6.  **Pemahaman LLM:** `Agent` mengirimkan prompt ke Gemini untuk menentukan *tool* yang akan digunakan. Gemini merespons dengan indikasi untuk menggunakan `list_gcp_projects` dengan argumen `dev`.
7.  **Eksekusi Tool:** `Agent` memanggil fungsi `list_gcp_projects('dev')` dari `gcp_tools.py`.
8.  **Pengumpulan Hasil:** Fungsi tersebut mengembalikan string yang berisi daftar proyek.
9.  **Pemformatan Awal:** `handle_chat_message` menerima hasil ini dan memformatnya, lalu mengembalikan string tunggal: `"Berikut adalah proyek di lingkungan dev:\n- proj-a\n- proj-b"`.
10. **Pemformatan Akhir:** `app.py` mengambil string ini dan membungkusnya dalam JSON: `{"text": "Berikut adalah proyek di lingkungan dev:\n- proj-a\n- proj-b"}`.
11. **Respons HTTP:** `app.py` mengirimkan JSON ini kembali ke Google Chat API dengan status `200 OK`.
12. **Output Pengguna:** Google Chat menampilkan pesan dari bot di ruang chat.

## 5. Deployment dan Infrastruktur

*   **Containerisasi (`Dockerfile`):**
    *   `FROM python:3.10-slim` akan tetap digunakan.
    *   `requirements.txt` akan diperbarui untuk menyertakan `Flask`, `gunicorn`, dan `google-api-python-client`.
    *   `COPY` akan menyertakan file `app.py` yang baru.
    *   `CMD` akan diubah untuk menjalankan server aplikasi web Gunicorn, yang lebih kuat daripada server development Flask. Perintahnya adalah:
        ```sh
        CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
        ```
        Cloud Run secara otomatis akan menyediakan variabel lingkungan `$PORT`, tetapi `8080` adalah default yang baik.

*   **Google Cloud Run:**
    *   Layanan Cloud Run baru akan dibuat.
    *   Image Docker akan dibangun dan diunggah ke Google Artifact Registry.
    *   Layanan akan dikonfigurasi untuk menggunakan image ini.
    *   Variabel lingkungan untuk kunci API (misalnya, `GOOGLE_API_KEY`) akan dikonfigurasi menggunakan integrasi Secret Manager Cloud Run untuk keamanan.

## 6. Desain Ekstensibilitas (Extensions & MCP)

Arsitektur yang diusulkan secara inheren dapat diperluas melalui mekanisme *tool* di dalam `Agent`.

*   **Mekanisme:** `Agent` memiliki dictionary `self.tools` yang memetakan nama *tool* ke fungsi yang dapat dipanggil.
*   **Menambahkan "Extension" Baru:**
    1.  Buat file Python baru di `my_cli_agent/tools/` (misalnya, `new_tool.py`).
    2.  Implementasikan fungsi yang diperlukan di dalam file tersebut, pastikan ia mengembalikan objek `ToolResult`.
    3.  Di `my_cli_agent/agent_new.py`, impor fungsi baru tersebut.
    4.  Daftarkan di dalam `__init__` kelas `Agent`: `self.tools["new_tool_name"] = new_tool_function`.
    5.  Perbarui metode `_create_tool_selection_prompt` dengan instruksi bagi LLM tentang kapan harus menggunakan *tool* baru ini.
*   **Peningkatan di Masa Depan:** Untuk menghindari modifikasi kode `agent_new.py` setiap kali *tool* baru ditambahkan, sistem dapat ditingkatkan untuk memuat *tools* secara dinamis dari file konfigurasi (misalnya, `tools.yaml`). File ini akan memetakan nama *tool* ke path fungsi yang dapat diimpor secara dinamis. Ini akan menjadi bagian dari v2.0.
