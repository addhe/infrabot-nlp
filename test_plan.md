# Test Plan & Test Cases: Infrabot NLP for Google Chat

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Referensi:** PRD v1.0, SDD v1.0

---

## 1. Pendahuluan

Dokumen ini menguraikan rencana, strategi, dan kasus uji untuk pengujian Infrabot Google Chat Bot. Tujuannya adalah untuk memverifikasi bahwa fungsionalitas produk memenuhi persyaratan yang ditetapkan dalam *Product Requirements Document* (PRD) dan diimplementasikan sesuai dengan *Software Design Document* (SDD).

## 2. Ruang Lingkup Pengujian

### 2.1. Dalam Ruang Lingkup (In-Scope)

*   **Pengujian Unit:** Verifikasi fungsi dan kelas individual, terutama logika `Agent` yang telah di-refactor dan fungsi *tools*.
*   **Pengujian Integrasi:** Verifikasi interaksi antara komponen utama (Flask App -> Agent -> Tools).
*   **Pengujian End-to-End (E2E):** Pengujian fungsionalitas penuh dari perspektif pengguna, mulai dari mengirim pesan di Google Chat hingga menerima balasan.
*   **Pengujian Keamanan Dasar:** Verifikasi otentikasi webhook.
*   **Fungsionalitas yang Diuji:**
    *   Penerimaan dan pemrosesan pesan dari Google Chat.
    *   Eksekusi semua *tools* yang ada (`execute_command`, `get_current_time`, `list_gcp_projects`, `create_gcp_project`).
    *   Penanganan respons percakapan non-tool.
    *   Penanganan kesalahan yang terstruktur.
    *   Deployment dan operasi dasar di Google Cloud Run.

### 2.2. Di Luar Ruang Lingkup (Out-of-Scope)

*   Pengujian Kinerja dan Beban (Stress/Load Testing).
*   Pengujian UI Google Chat itu sendiri.
*   Pengujian *tools* atau "extensions" baru yang belum diimplementasikan.
*   Pengujian kompatibilitas browser/klien Google Chat.
*   Pengujian manajemen konteks percakapan yang kompleks (di luar lingkup v1.0).

## 3. Strategi Pengujian

### 3.1. Pengujian Unit (Unit Testing)
*   **Tujuan:** Memastikan setiap komponen kode individual berfungsi seperti yang diharapkan.
*   **Tools:** `pytest`.
*   **Area Fokus:**
    *   Fungsi-fungsi di dalam `tools` harus diuji untuk memastikan mereka mengembalikan objek `ToolResult` yang benar untuk kasus sukses dan gagal.
    *   Metode `Agent.handle_chat_message` akan diuji secara terpisah dengan *mocking* panggilan ke LLM API dan *tools* untuk memverifikasi logika orkestrasinya.

### 3.2. Pengujian Integrasi (Integration Testing)
*   **Tujuan:** Memastikan komponen-komponen yang terpisah dapat bekerja sama dengan benar.
*   **Tools:** `pytest` dengan `requests`.
*   **Area Fokus:**
    *   Menguji endpoint Flask (`app.py`) secara lokal dengan mengirimkan payload JSON yang disimulasikan dan memverifikasi bahwa `Agent` dipanggil dengan benar.
    *   Menguji panggilan dari `Agent` ke fungsi *tool* yang sebenarnya (bukan *mock*) untuk memastikan data diteruskan dengan benar.

### 3.3. Pengujian End-to-End (E2E) / Pengujian Fungsional
*   **Tujuan:** Memvalidasi alur kerja aplikasi penuh dari perspektif pengguna akhir.
*   **Tools:** Manual (melalui antarmuka Google Chat).
*   **Proses:**
    1.  Aplikasi di-deploy ke lingkungan staging di Google Cloud Run.
    2.  Bot dikonfigurasi dalam ruang Google Chat khusus untuk pengujian.
    3.  Penguji menjalankan kasus uji manual dengan mengirimkan pesan ke bot dan memverifikasi responsnya secara visual.

## 4. Lingkungan Pengujian

*   **Lingkungan Lokal:** Digunakan untuk pengujian unit dan integrasi. Memerlukan Python, `pytest`, dan variabel lingkungan yang dikonfigurasi.
*   **Lingkungan Staging:**
    *   **Platform:** Proyek Google Cloud terpisah.
    *   **Hosting:** Layanan Google Cloud Run.
    *   **Konfigurasi:** Variabel lingkungan dan rahasia dikelola melalui Google Secret Manager.
    *   **Klien:** Klien web atau desktop Google Chat.

## 5. Kasus Uji (Test Cases)

### 5.1. Kategori: Konektivitas & Keamanan Webhook

| ID | Deskripsi | Langkah-langkah | Hasil yang Diharapkan | Prioritas |
|---|---|---|---|---|
| TC-SEC-01 | Permintaan dengan token otentikasi yang valid | Kirim `POST` request ke URL webhook dengan header `Authorization` yang valid dan payload `MESSAGE`. | Server merespons dengan `200 OK` dan payload JSON balasan. | Tinggi |
| TC-SEC-02 | Permintaan tanpa token otentikasi | Kirim `POST` request ke URL webhook tanpa header `Authorization`. | Server merespons dengan `401 Unauthorized` atau `403 Forbidden`. | Tinggi |
| TC-SEC-03 | Permintaan dengan token otentikasi yang tidak valid | Kirim `POST` request dengan Bearer Token yang salah/kadaluwarsa. | Server merespons dengan `401 Unauthorized` atau `403 Forbidden`. | Tinggi |
| TC-CON-01 | Event selain `MESSAGE` | Kirim payload event yang valid dengan tipe `ADDED_TO_SPACE`. | Server merespons dengan `200 OK` tetapi tidak melakukan tindakan atau mengirim balasan. | Sedang |

### 5.2. Kategori: Eksekusi Tool

| ID | Deskripsi | Langkah-langkah | Hasil yang Diharapkan | Prioritas |
|---|---|---|---|---|
| TC-TOOL-01 | `execute_command` - Kasus Sukses | Kirim pesan: `@Infrabot jalankan perintah echo "test berhasil"` | Bot membalas dengan: `test berhasil` | Tinggi |
| TC-TOOL-02 | `execute_command` - Kasus Gagal | Kirim pesan: `@Infrabot jalankan perintah ls /direktori_tidak_ada` | Bot membalas dengan pesan kesalahan yang jelas, misalnya, "Error: ls: cannot access ... No such file or directory". | Tinggi |
| TC-TOOL-03 | `get_current_time` - Kasus Sukses | Kirim pesan: `@Infrabot jam berapa di Jakarta?` | Bot membalas dengan waktu saat ini di Jakarta dalam format yang dapat dibaca. | Tinggi |
| TC-TOOL-04 | `list_gcp_projects` - Kasus Sukses | Kirim pesan: `@Infrabot daftar proyek gcp di dev` | Bot membalas dengan daftar proyek yang diformat dengan benar. | Tinggi |
| TC-TOOL-05 | `create_gcp_project` - Kasus Sukses | Kirim pesan: `@Infrabot buat proyek gcp dengan id my-test-project-123` | Bot membalas dengan pesan konfirmasi bahwa proyek sedang dibuat atau telah berhasil dibuat. | Tinggi |
| TC-TOOL-06 | Permintaan *tool* dengan argumen tidak valid | Kirim pesan: `@Infrabot daftar proyek gcp di env_salah` | Bot membalas dengan pesan kesalahan dari *tool* yang menyatakan lingkungan tidak valid. | Sedang |

### 5.3. Kategori: Percakapan & Penanganan Kesalahan

| ID | Deskripsi | Langkah-langkah | Hasil yang Diharapkan | Prioritas |
|---|---|---|---|---|
| TC-CHAT-01 | Sapaan Sederhana | Kirim pesan: `@Infrabot halo` | Bot memberikan balasan percakapan yang ramah. | Sedang |
| TC-CHAT-02 | Permintaan Tidak Jelas | Kirim pesan: `@Infrabot proyek` | Bot membalas dengan meminta klarifikasi atau memberikan contoh perintah yang valid. | Sedang |
| TC-ERR-01 | *Tool* tidak ditemukan (simulasi) | (Memerlukan modifikasi kode sementara) Kirim permintaan untuk *tool* yang tidak terdaftar. | Bot membalas dengan: "Maaf, saya tidak dapat menemukan tool tersebut." | Sedang |
| TC-ERR-02 | Kesalahan Internal Server (simulasi) | (Memerlukan modifikasi kode sementara) Paksa adanya *exception* di dalam `handle_chat_message`. | Bot membalas dengan pesan kesalahan umum: "Maaf, terjadi kesalahan internal." | Tinggi |
