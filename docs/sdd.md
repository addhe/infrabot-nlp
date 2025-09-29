# Software Design Document: Infrabot NLP for Google Chat

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Referensi:** TDD v1.0, PRD v1.0

---

## 1. Pendahuluan

Dokumen ini menyediakan spesifikasi desain perangkat lunak terperinci untuk Infrabot Google Chat Bot. Tujuannya adalah untuk memberikan cetak biru (blueprint) bagi para engineer dalam mengimplementasikan kode. Dokumen ini menguraikan struktur modul, definisi kelas, antarmuka (API) internal, model data, dan strategi penanganan kesalahan.

## 2. Tinjauan Desain Sistem

Sistem ini dirancang sebagai aplikasi web Python stateless yang di-container-isasi, mengikuti arsitektur yang diuraikan dalam TDD. Desain perangkat lunak ini berfokus pada modularitas, pemisahan tanggung jawab (*separation of concerns*), dan ekstensibilitas.

Tiga lapisan utama dalam desain perangkat lunak adalah:
1.  **Presentation Layer (`my_cli_agent/app.py`):** Bertanggung jawab untuk menangani interaksi HTTP dengan Google Chat API.
2.  **Business Logic Layer (`my_cli_agent/agent_new.py`):** Mengandung logika inti untuk memproses permintaan dan mengorkestrasi penggunaan *tools*.
3.  **Data & Service Access Layer (`my_cli_agent/tools/` & `my_cli_agent/providers/`):** Bertanggung jawab untuk berinteraksi dengan layanan eksternal (shell, GCP, LLM API).

## 3. Desain Modul dan Kelas

### 3.1. Modul: `my_cli_agent/app.py` (Presentation Layer)

*   **Tujuan:** Bertindak sebagai *entry point* dan menangani semua komunikasi HTTP.
*   **Struktur:**
    *   **`app = Flask(__name__)`**: Objek global instance Flask.
    *   **`agent = Agent()`**: Objek global instance `Agent` yang diinisialisasi saat startup untuk efisiensi.
    *   **`handle_event(request)`**: Fungsi utama yang akan menjadi endpoint webhook (`@app.route('/', methods=['POST'])`).
*   **Fungsi: `handle_event(request)`**
    *   **Input:** Objek `request` dari Flask.
    *   **Logika:**
        1.  **Verifikasi Keamanan:**
            *   Mengekstrak header `Authorization` dari `request`.
            *   Menggunakan `google.oauth2.id_token.verify_oauth2_token` untuk memverifikasi Bearer Token (JWT) terhadap audiens yang diharapkan (ID proyek Google Cloud). Jika gagal, kembalikan status `401 Unauthorized`.
        2.  **Parsing Event:**
            *   Mendapatkan body JSON dari `request.get_json()`.
            *   Memeriksa tipe event. Hanya proses jika `event['type'] == 'MESSAGE'`. 
            *   Mengekstrak teks pesan dari `event['message']['text']`. Teks ini akan berisi nama mention bot, yang perlu dibersihkan.
        3.  **Pemanggilan Logika Bisnis:**
            *   Memanggil `response_text = agent.handle_chat_message(cleaned_text)`.
        4.  **Pembuatan Respons:**
            *   Membuat dictionary Python: `response_payload = {"text": response_text}`.
        5.  **Return:** Mengembalikan `jsonify(response_payload)` dengan status `200 OK`.
    *   **Penanganan Kesalahan:** Seluruh logika di dalam fungsi ini akan dibungkus dalam blok `try...except`. Jika terjadi *exception*, catat (*log*) kesalahan tersebut dan kembalikan respons JSON yang ramah pengguna seperti `jsonify({"text": "Maaf, terjadi kesalahan internal."})` dengan status `500 Internal Server Error`.

### 3.2. Kelas: `Agent` (Business Logic Layer)

*   **File:** `my_cli_agent/agent_new.py`
*   **Tujuan:** Mengorkestrasi pemrosesan permintaan pengguna.
*   **Properti Utama:**
    *   `self.provider: LLMProvider`: Instance dari provider LLM yang aktif.
    *   `self.tools: Dict[str, Callable]`: Dictionary yang memetakan nama *tool* ke fungsi yang dapat dieksekusi.
*   **Metode Kunci (Baru): `handle_chat_message(self, prompt: str) -> str`**
    *   **Tanggung Jawab:** Mengadaptasi logika `process_with_tools` untuk lingkungan web yang *stateless* dan non-interaktif.
    *   **Input:** `prompt` (string), teks bersih dari pesan pengguna.
    *   **Output:** `str`, respons teks lengkap untuk dikirim kembali ke pengguna.
    *   **Alur Logika Internal:**
        1.  Buat prompt untuk seleksi *tool* (menggunakan metode internal `_create_tool_selection_prompt`).
        2.  Panggil `self.provider.generate_response(...)` untuk mendapatkan keputusan *tool* dari LLM.
        3.  Parse respons LLM untuk mendapatkan `tool_name` dan `tool_arg`.
        4.  Jika `tool_name` valid dan ada di `self.tools`:
            a. Panggil fungsi *tool* yang sesuai: `result: ToolResult = self.tools[tool_name](tool_arg)`.
            b. Periksa `result.success`.
            c. Format `result.result` atau `result.error_message` menjadi string yang dapat dibaca.
        5.  Jika tidak ada *tool* yang diperlukan, panggil `self.provider.generate_response(prompt, ...)` untuk mendapatkan respons percakapan biasa.
        6.  Kembalikan string hasil pemformatan.
    *   **Penanganan Kesalahan:** Blok `try...except` akan menangkap kegagalan saat memanggil LLM atau *tools*, dan memformat pesan kesalahan untuk dikembalikan sebagai string.

### 3.3. Antarmuka `Tool` (Service Access Layer)

*   **Tujuan:** Menstandarisasi cara `Agent` berinteraksi dengan semua *tools*.
*   **Struktur Data Kunci:** `ToolResult` (Dataclass).
    *   **File:** `my_cli_agent/models.py` (file baru untuk model data bersama).
    *   **Definisi:** 
        ```python
        from dataclasses import dataclass
        from typing import Any, Optional

        @dataclass
        class ToolResult:
            success: bool
            result: Optional[str] = None
            error_message: Optional[str] = None
        ```
*   **Kontrak Fungsi Tool:**
    *   Setiap fungsi yang dapat dieksekusi sebagai *tool* **HARUS** mengembalikan sebuah instance dari `ToolResult`.
    *   Tanda tangan input bervariasi tergantung pada kebutuhan *tool* (misalnya, `command: str` untuk `execute_command`, `ref: str, element: str, text: str` untuk `browser_type`). `Agent` bertanggung jawab untuk mem-parsing argumen yang benar dari LLM.

## 4. Model Data dan Struktur

*   **Payload Masuk Google Chat (Contoh Disederhanakan):**
    ```json
    {
      "eventTime": "2025-09-13T10:00:00.000Z",
      "type": "MESSAGE",
      "message": {
        "name": "spaces/AAAA.../messages/BBBB...",
        "text": "@Infrabot list gcp projects in dev",
        "sender": { "displayName": "Devon" }
      },
      "space": { "name": "spaces/AAAA..." }
    }
    ```
*   **Payload Keluar Google Chat:**
    ```json
    {
      "text": "Berikut adalah proyek di lingkungan dev:\n- proj-a\n- proj-b"
    }
    ```
*   **Struktur Data Internal:** `ToolResult` (seperti yang didefinisikan di 3.3).

## 5. Strategi Penanganan Kesalahan

*   **Level 1: Kegagalan Verifikasi (di `my_cli_agent/app.py`)**
    *   **Penyebab:** Token JWT tidak valid atau tidak ada.
    *   **Tindakan:** Segera kembalikan status `401` atau `403`. Tidak ada pemrosesan lebih lanjut.
*   **Level 2: Kegagalan Eksekusi Tool (di `tools/*.py`)**
    *   **Penyebab:** Perintah shell gagal, API GCP mengembalikan error.
    *   **Tindakan:** Fungsi *tool* mengembalikan `ToolResult(success=False, error_message="...")`.
*   **Level 3: Kegagalan Logika Bisnis (di `Agent`)**
    *   **Penyebab:** LLM tidak merespons, *tool* yang diminta tidak ada.
    *   **Tindakan:** `handle_chat_message` menangkap ini dan mengembalikan string kesalahan, misalnya, `"Maaf, saya tidak dapat menemukan tool bernama '...'"`.
*   **Level 4: Kegagalan Aplikasi Umum (di `my_cli_agent/app.py`)**
    *   **Penyebab:** Kesalahan tak terduga (misalnya, kehabisan memori).
    *   **Tindakan:** Blok `try...except` utama menangkap *exception*, mencatatnya, dan mengembalikan pesan kesalahan umum dengan status `500`.

## 6. Pertimbangan Keamanan

*   **Verifikasi Webhook:** Implementasi verifikasi JWT adalah **wajib** untuk mencegah serangan *unauthenticated request*.
*   **Manajemen Secret:** Semua kunci API (`GOOGLE_API_KEY`, dll.) dan kredensial GCP akan di-mount sebagai variabel lingkungan di Cloud Run, yang ditarik dari Google Secret Manager. **Tidak ada kredensial yang boleh ada di dalam kode atau image Docker.**
*   **Risiko Eksekusi Perintah (`execute_command`):** *Tool* ini memiliki risiko keamanan yang tinggi. Untuk v1.0, penggunaannya harus dibatasi pada lingkungan yang tepercaya.
    *   **Mitigasi Jangka Panjang (di luar v1.0):** Menjalankan perintah di dalam sandbox terisolasi, menggunakan daftar perintah yang diizinkan (*allowlist*), atau menggantinya dengan fungsi *tool* yang lebih spesifik dan aman.

## 7. Konfigurasi dan Deployment

*   **Variabel Lingkungan yang Diperlukan:**
    *   `GOOGLE_API_KEY`: Untuk Gemini.
    *   `GCP_PROJECT`: ID Proyek Google Cloud tempat bot berjalan.
    *   `MCP_SERVER_URL`: URL untuk Zen MCP Server.
    *   `SEQ_THINKING_MCP_SERVER_URL`: URL untuk Sequential Thinking MCP Server.
    *   `PLAYWRIGHT_MCP_SERVER_URL`: URL untuk Playwright MCP Server.
    *   (Kredensial GCP untuk `gcloud` akan di-handle oleh *service account* yang terpasang pada layanan Cloud Run).
*   **Dockerfile:**
    *   `CMD` akan diatur ke `["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]` sebagai titik awal yang baik untuk produksi.
