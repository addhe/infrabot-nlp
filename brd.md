# Business Requirements Document: Infrabot NLP Google Chat Bot

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Penulis:** Gemini CLI Agent

---

## 1. Latar Belakang dan Ringkasan Eksekutif

Proyek Infrabot NLP saat ini ada dalam bentuk *command-line interface* (CLI) yang kuat, mampu berinteraksi dengan berbagai *tools* dan layanan cloud (seperti GCP) melalui perintah berbasis teks. Meskipun fungsional, format CLI membatasi aksesibilitasnya hanya untuk pengguna teknis dan tidak mendukung interaksi kolaboratif secara *real-time*.

Dokumen ini menguraikan persyaratan bisnis untuk mentransformasikan aplikasi CLI ini menjadi sebuah chatbot interaktif yang terintegrasi penuh dengan Google Chat. Tujuannya adalah untuk menyediakan antarmuka yang lebih mudah diakses, ramah pengguna, dan kolaboratif untuk berinteraksi dengan agen AI yang ada. Arsitektur baru ini akan dirancang secara modular untuk mendukung ekstensibilitas di masa depan, memungkinkan penambahan fungsionalitas baru ("extensions") atau integrasi dengan sistem eksternal seperti "MCP server".

## 2. Masalah Bisnis dan Peluang

### 2.1. Masalah Bisnis

*   **Aksesibilitas Terbatas:** Penggunaan CLI memerlukan pengetahuan teknis, menghalangi adopsi oleh tim non-teknis (misalnya, manajer proyek, analis) yang bisa mendapatkan manfaat dari kemampuan agen.
*   **Kurangnya Kolaborasi:** Sesi CLI bersifat individual. Sulit bagi tim untuk berkolaborasi dalam menyelesaikan masalah atau mengelola infrastruktur secara bersamaan menggunakan *tool* ini.
*   **Alur Kerja yang Terfragmentasi:** Pengguna harus beralih dari platform komunikasi (seperti Google Chat) ke terminal untuk menggunakan agen, yang mengganggu alur kerja.

### 2.2. Peluang

*   **Meningkatkan Produktivitas Tim:** Dengan membawa fungsionalitas agen ke dalam Google Chat, tim dapat menjalankan perintah, memeriksa status, dan mengelola sumber daya langsung dari platform kolaborasi mereka.
*   **Demokratisasi Akses:** Memungkinkan lebih banyak peran di dalam organisasi untuk memanfaatkan kemampuan AI untuk tugas-tugas operasional tanpa memerlukan akses shell atau pelatihan teknis yang mendalam.
*   **Visibilitas dan Transparansi:** Perintah dan hasil yang dieksekusi di dalam ruang chat dapat dilihat oleh semua anggota, meningkatkan transparansi dan berfungsi sebagai log operasional informal.

## 3. Tujuan dan Sasaran Proyek

*   **Tujuan 1: Transformasi Antarmuka:** Mengubah aplikasi dari CLI menjadi chatbot fungsional di Google Chat.
*   **Tujuan 2: Paritas Fungsionalitas:** Memastikan semua kemampuan inti yang ada di CLI (eksekusi perintah, *tools* waktu, *tools* GCP) tersedia melalui antarmuka chat.
*   **Tujuan 3: Arsitektur yang Dapat Diperluas:** Merancang sistem dengan fondasi modular yang memungkinkan penambahan *tools* dan integrasi pihak ketiga (MCP) di masa depan dengan mudah.
*   **Tujuan 4: Pengalaman Pengguna yang Mulus:** Memberikan pengalaman percakapan yang responsif dan intuitif bagi pengguna di Google Chat.

## 4. Ruang Lingkup Proyek

### 4.1. Dalam Ruang Lingkup (In-Scope)

*   Pengembangan layanan web (backend) menggunakan Python dan Flask untuk menangani webhook dari Google Chat.
*   Integrasi dengan Google Chat API untuk menerima pesan dan mengirim balasan.
*   Adaptasi logika `Agent` yang ada untuk memproses input dari chat, bukan dari `stdin`.
*   Dukungan untuk *tools* inti: `execute_command`, `get_current_time`, `list_gcp_projects`, `create_gcp_project`.
*   Integrasi bawaan dengan beberapa Mission Control Planes (MCPs) untuk fungsionalitas tingkat lanjut:
    *   Zen MCP Server (untuk workflow pengembangan perangkat lunak).
    *   Sequential Thinking (untuk pemecahan masalah).
    *   Playwright MCP (untuk otomasi browser).
    *   Markitdown (untuk konversi file ke Markdown).
*   Manajemen konteks percakapan dasar untuk menjaga alur dialog dalam satu sesi.
*   Containerisasi aplikasi menggunakan Docker untuk deployment di Google Cloud Run.
*   Konfigurasi otentikasi dasar untuk memverifikasi bahwa permintaan webhook berasal dari Google Chat.

### 4.2. Di Luar Ruang Lingkup (Out-of-Scope) untuk Versi 1.0

*   Implementasi penuh dari *tools* atau "extensions" baru. Hanya arsitektur untuk mendukungnya yang akan dibangun.
*   Integrasi penuh dengan "MCP server". Hanya antarmuka atau *tool* placeholder yang akan disiapkan.
*   Antarmuka pengguna tingkat lanjut di Google Chat (misalnya, Kartu, Dialog, Tombol Interaktif). Interaksi awal akan berbasis teks.
*   Sistem manajemen pengguna dan otorisasi yang kompleks. Izin akan dikelola di tingkat ruang chat Google.
*   Penyimpanan riwayat percakapan jangka panjang dalam database persisten.

## 5. Persyaratan Fungsional

| ID | Persyaratan | Deskripsi |
|---|---|---|
| FR-01 | Penerimaan Pesan | Bot harus dapat menerima dan mem-parsing pesan yang dikirim kepadanya di ruang Google Chat (baik dalam pesan langsung maupun saat di-mention). |
| FR-02 | Pemrosesan Bahasa Alami | Bot harus menggunakan model AI Gemini untuk memahami maksud dari pesan pengguna. |
| FR-03 | Eksekusi *Tools* | Bot harus dapat memicu dan mengeksekusi semua *tools* yang terintegrasi (perintah shell, waktu, GCP, MCPs, dll.) berdasarkan permintaan pengguna. |
| FR-04 | Pengiriman Balasan | Bot harus memformat dan mengirimkan hasil dari eksekusi *tool* atau respons percakapan kembali ke ruang Google Chat yang sama. |
| FR-05 | Penanganan Percakapan Dasar | Bot harus dapat menangani sapaan sederhana dan memberikan respons yang membantu jika tidak memahami permintaan pengguna. |
| FR-06 | Arsitektur *Tool* yang Ekstensibel | Sistem harus memiliki mekanisme yang jelas untuk mendaftarkan dan memanggil *tools* baru tanpa memerlukan perubahan signifikan pada kode inti. |

## 6. Persyaratan Non-Fungsional

| ID | Persyaratan | Deskripsi |
|---|---|---|
| NFR-01 | Kinerja | Waktu respons untuk sebagian besar permintaan (dari pesan diterima hingga balasan dikirim) harus di bawah 5 detik. |
| NFR-02 | Ketersediaan | Layanan bot harus memiliki ketersediaan tinggi (uptime > 99.9%), yang akan dicapai dengan deployment di Google Cloud Run. |
| NFR-03 | Skalabilitas | Aplikasi harus dapat menangani permintaan dari beberapa ruang chat dan pengguna secara bersamaan tanpa degradasi kinerja. |
| NFR-04 | Keamanan | Kunci API dan kredensial lainnya harus dikelola dengan aman (misalnya, melalui Secret Manager atau variabel lingkungan). Webhook harus diverifikasi untuk memastikan permintaan sah. |
| NFR-05 | Kemudahan Deployment | Aplikasi harus sepenuhnya ter-container-isasi (Docker) dan dapat di-deploy dengan proses yang terotomatisasi ke Google Cloud Run. |

## 7. Metrik Keberhasilan

*   **Adopsi:** Jumlah ruang chat aktif yang menggunakan bot dalam 30 hari pertama setelah peluncuran.
*   **Keterlibatan:** Jumlah total perintah atau *tools* yang berhasil dieksekusi per hari.
*   **Keandalan:** Tingkat keberhasilan pemrosesan pesan (jumlah respons sukses / jumlah total pesan yang diterima).
*   **Kepuasan Pengguna:** Umpan balik kualitatif yang dikumpulkan dari pengguna awal.
