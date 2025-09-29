# Product Requirements Document: Infrabot NLP for Google Chat

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Status:** Draf

---

## 1. Pendahuluan

Dokumen ini merinci persyaratan produk untuk **Infrabot**, sebuah chatbot yang terintegrasi dengan Google Chat. Infrabot adalah evolusi dari *tool* Infrabot NLP CLI yang sudah ada, yang dirancang untuk memindahkan fungsionalitasnya ke dalam platform kolaboratif yang banyak digunakan. Produk ini akan memungkinkan tim teknis dan non-teknis untuk berinteraksi dengan infrastruktur dan layanan cloud melalui antarmuka percakapan yang intuitif, langsung di dalam Google Chat.

## 2. Visi dan Tujuan Produk

**Visi:** Menjadi asisten operasional cerdas yang terintegrasi secara mulus ke dalam alur kerja kolaboratif tim, memungkinkan manajemen infrastruktur yang efisien, transparan, dan dapat diakses oleh semua orang.

**Tujuan:**

*   **Aksesibilitas:** Menyediakan antarmuka yang mudah digunakan (percakapan) untuk semua fungsionalitas yang sebelumnya hanya tersedia di CLI.
*   **Efisiensi:** Mengurangi waktu yang dibutuhkan pengguna untuk beralih konteks antara platform komunikasi dan terminal, sehingga mempercepat tugas-tugas operasional.
*   **Kolaborasi:** Memungkinkan tim untuk secara kolektif melihat dan bertindak berdasarkan informasi infrastruktur secara *real-time* di dalam ruang Google Chat.
*   **Ekstensibilitas:** Membangun platform yang solid sehingga fungsionalitas baru, yang disebut "Extensions" atau "Tools", dapat ditambahkan dengan mudah di masa depan.

## 3. Target Pengguna (User Personas)

*   **Persona Utama: "Devon", DevOps Engineer**
    *   **Kebutuhan:** Perlu menjalankan perintah ad-hoc (misalnya, `kubectl`, `gcloud`, `ls`) dengan cepat untuk memeriksa status atau melakukan tindakan perbaikan. Seringkali kebutuhan ini muncul saat berdiskusi dengan tim di Google Chat.
    *   **Frustrasi:** Harus menghentikan percakapan, membuka terminal, menjalankan perintah, lalu menyalin-tempel hasilnya kembali ke chat.

*   **Persona Sekunder: "Priya", Project Manager**
    *   **Kebutuhan:** Perlu mendapatkan informasi status tingkat tinggi (misalnya, "Daftar semua proyek GCP di lingkungan dev") tanpa harus bertanya kepada seorang engineer.
    *   **Frustrasi:** Merasa bergantung pada ketersediaan tim teknis untuk mendapatkan informasi yang sebenarnya bisa diotomatisasi.

*   **Persona Utama: "Tessa", Team Lead**
    *   **Kebutuhan:** Membutuhkan visibilitas atas tindakan operasional yang dilakukan oleh timnya untuk memastikan kepatuhan dan untuk tujuan audit.
    *   **Frustrasi:** Sulit melacak siapa melakukan apa ketika tindakan dilakukan di terminal lokal masing-masing anggota tim.

## 4. User Stories

| ID | Sebagai (Persona) | Saya Ingin (Tindakan) | Sehingga Saya Dapat (Manfaat) | Prioritas |
|---|---|---|---|---|
| US-01 | Devon, DevOps Engineer | `@mention` Infrabot di chat dan memintanya menjalankan perintah shell seperti `ls -l /tmp` | Dengan cepat memeriksa file di server tanpa meninggalkan Google Chat. | Tinggi |
| US-02 | Devon, DevOps Engineer | Meminta Infrabot untuk membuat proyek GCP baru | Memulai proses penyediaan sumber daya baru saat sedang merencanakan dengan tim. | Tinggi |
| US-03 | Priya, Project Manager | Bertanya kepada Infrabot, "ada berapa proyek di staging?" | Mendapatkan data cepat untuk laporan status proyek. | Tinggi |
| US-04 | Tessa, Team Lead | Melihat semua interaksi dengan Infrabot di ruang chat tim | Memiliki jejak audit informal tentang perubahan atau pemeriksaan yang dilakukan. | Tinggi |
| US-05 | Devon, DevOps Engineer | Bertanya kepada Infrabot, "jam berapa sekarang di London?" | Mengoordinasikan jadwal rilis dengan tim di zona waktu yang berbeda. | Sedang |
| US-06 | Pengguna Baru | Mendapat pesan bantuan saat pertama kali berinteraksi atau saat memberikan perintah yang tidak valid | Memahami cara menggunakan bot dengan cepat. | Sedang |
| US-07 | Devon, DevOps Engineer | Meminta Infrabot untuk melakukan code review pada pull request | Mendapatkan analisis kualitas kode otomatis sebelum me-merge. | Tinggi |
| US-08 | Priya, Project Manager | Meminta Infrabot untuk "pecah proyek X menjadi beberapa task" | Mendapatkan draf rencana proyek yang terstruktur. | Sedang |
| US-09 | Devon, DevOps Engineer | Meminta Infrabot untuk "buka situs x dan cari tombol login" | Mengotomatisasi tugas-tugas berbasis web yang repetitif. | Tinggi |
| US-10 | Tessa, Team Lead | Meminta Infrabot untuk "baca dokumen PDF ini dan ringkas isinya" | Dengan cepat memahami isi dokumen tanpa membukanya. | Sedang |

## 5. Fitur dan Persyaratan Fungsional

### 5.1. Integrasi Google Chat
*   **F-01:** Bot harus terdaftar sebagai aplikasi di Google Workspace dan dapat ditambahkan ke ruang chat.
*   **F-02:** Bot harus dieksekusi melalui layanan web yang terekspos di URL publik (HTTPS) untuk berfungsi sebagai webhook.
*   **F-03:** Layanan web harus dapat menerima dan mem-parsing event `MESSAGE` dalam format JSON dari Google Chat API.
*   **F-04:** Layanan web harus dapat memverifikasi token otentikasi dari Google Chat untuk memastikan permintaan itu sah.
*   **F-05:** Bot harus dapat mengirim balasan berbasis teks ke ruang chat tempat pesan asli diterima.

### 5.2. Logika Inti Agen
*   **F-06:** Pesan teks dari pengguna harus diteruskan ke logika `Agent` untuk diproses.
*   **F-07:** `Agent` harus menggunakan model Gemini untuk memahami maksud pengguna dan menentukan apakah sebuah *tool* perlu dipanggil.
*   **F-08:** `Agent` harus mendukung semua *tools* yang ada:
    *   `execute_command`: Menjalankan perintah shell.
    *   `get_current_time`: Mendapatkan waktu saat ini.
    *   `list_gcp_projects`: Mendaftar proyek GCP.
    *   `create_gcp_project`: Membuat proyek GCP.
    *   `call_mcp_server`: Mendelegasikan tugas kompleks (code review, debug, planning) ke Zen MCP Server.
    *   `call_sequential_thinking_server`: Memecahkan masalah yang memerlukan penalaran langkah-demi-langkah.
    *   `convert_file_to_markdown`: Mengonversi file lokal (PDF, DOCX, dll.) ke format Markdown.
    *   `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`: Mengontrol browser web untuk otomasi.
*   **F-09:** Hasil (sukses atau gagal) dari eksekusi *tool* harus ditangkap dan diformat menjadi string yang ramah-baca.
*   **F-10:** Jika tidak ada *tool* yang cocok, `Agent` harus memberikan respons percakapan umum.

### 5.3. Pengalaman Pengguna (UX)
*   **UX-01:** Interaksi untuk v1.0 akan sepenuhnya berbasis teks. Pengguna akan `@mention` bot diikuti dengan permintaan mereka.
*   **UX-02:** Bot harus memberikan respons konfirmasi saat memulai tugas yang berjalan lama (misalnya, "OK, sedang membuat proyek GCP...").
*   **UX-03:** Pesan kesalahan harus jelas dan, jika memungkinkan, memberikan saran (misalnya, "Perintah tidak dikenali. Coba 'bantuan' untuk melihat apa yang bisa saya lakukan.").

## 6. Arsitektur dan Persyaratan Non-Fungsional

*   **NFR-01 (Platform):** Aplikasi akan di-container-isasi menggunakan Docker dan di-deploy di Google Cloud Run untuk skalabilitas dan kemudahan pengelolaan.
*   **NFR-02 (Kinerja):** Waktu pemrosesan dari pesan diterima hingga balasan dikirim harus kurang dari 5 detik untuk permintaan umum.
*   **NFR-03 (Keamanan):** Semua kunci API, token, dan kredensial harus disimpan dengan aman menggunakan Google Secret Manager atau variabel lingkungan yang di-inject saat runtime. Tidak boleh ada *hardcoding* kredensial di dalam kode.
*   **NFR-04 (State Management):** Untuk v1.0, setiap pesan akan diperlakukan sebagai transaksi *stateless*. Konteks percakapan yang lebih kompleks (mengingat pesan sebelumnya) tidak termasuk dalam ruang lingkup awal.

## 7. Rencana Rilis dan Masa Depan (Roadmap)

### Versi 1.0 (Rilis Awal)
*   Fungsionalitas yang dijelaskan dalam dokumen ini.
*   Interaksi berbasis teks saja.
*   Dukungan untuk semua *tools* CLI yang ada.
*   Deployment di Google Cloud Run.

### Versi 1.1 (Rilis Berikutnya)
*   **Google Chat Cards:** Memperkenalkan komponen UI yang lebih kaya (tombol, formulir) untuk interaksi yang lebih terstruktur.
*   **Manajemen Konteks Dasar:** Kemampuan untuk mengingat 2-3 pesan terakhir dalam sebuah percakapan untuk dialog yang lebih alami.
*   **Notifikasi Proaktif:** Kemampuan bot untuk mengirim pesan ke sebuah ruang chat berdasarkan pemicu eksternal (misalnya, dari sistem monitoring).

### Versi 2.0 (Jangka Panjang)
*   **Sistem Ekstensi Penuh:** Memformalkan cara "Extensions" dapat dikembangkan dan ditambahkan oleh pihak ketiga atau tim lain.
*   **Integrasi MCP Server:** Implementasi penuh dari *tool* untuk berkomunikasi dengan MCP server.
*   **Manajemen State Persisten:** Menggunakan database seperti Firestore atau Redis untuk menyimpan riwayat percakapan dan preferensi pengguna.

## 8. Metrik Keberhasilan
*   **Aktivasi:** Jumlah ruang chat yang menginstal bot.
*   **Retensi:** Persentase pengguna aktif mingguan.
*   **Tingkat Keberhasilan Tugas:** Persentase permintaan yang menghasilkan eksekusi *tool* yang sukses.
*   **Waktu Respons Rata-rata:** Metrik kinerja untuk memastikan pengalaman pengguna yang cepat.
