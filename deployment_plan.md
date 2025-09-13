# Deployment Plan & Risk Management: Infrabot NLP for Google Chat

**Versi Dokumen:** 1.0
**Tanggal:** 13 September 2025
**Referensi:** TDD v1.0, Test Plan v1.0

---

## 1. Pendahuluan

Dokumen ini menguraikan rencana strategis untuk deployment Infrabot Google Chat Bot ke lingkungan produksi. Ini mencakup strategi peluncuran, langkah-langkah pra-deployment, proses deployment itu sendiri, dan rencana pasca-deployment.

Bagian kedua dari dokumen ini berfokus pada manajemen risiko, mengidentifikasi potensi masalah yang dapat memengaruhi proyek dan mendefinisikan strategi mitigasi serta rencana kontingensi.

## 2. Strategi Deployment

### 2.1. Model Peluncuran (Rollout Strategy)

Akan digunakan model peluncuran bertahap untuk meminimalkan dampak dan mengumpulkan umpan balik secara terkontrol.

1.  **Fase 1: Internal Alpha (Tim Inti)**
    *   **Pengguna:** Tim developer dan produk inti.
    *   **Tujuan:** Memverifikasi fungsionalitas inti di lingkungan produksi dan mengidentifikasi bug kritis.
    *   **Durasi:** 1 minggu.

2.  **Fase 2: Team Beta (Tim Teknis yang Diperluas)**
    *   **Pengguna:** Tim DevOps dan beberapa engineer dari tim lain yang relevan.
    *   **Tujuan:** Menguji bot dalam skenario penggunaan dunia nyata dan mengumpulkan umpan balik tentang kegunaan dan kinerja.
    *   **Durasi:** 2 minggu.

3.  **Fase 3: General Availability (GA)**
    *   **Pengguna:** Tersedia untuk semua tim yang ditargetkan di dalam organisasi.
    *   **Tujuan:** Peluncuran penuh.

### 2.2. Strategi Lingkungan

| Lingkungan | Tujuan | Platform | Data |
|---|---|---|---|
| **Staging** | Pengujian E2E, verifikasi build | Proyek GCP terpisah, Cloud Run | Data non-produksi, terisolasi |
| **Produksi** | Layanan live untuk pengguna | Proyek GCP produksi, Cloud Run | Data live |

## 3. Checklist Pra-Deployment

Sebelum deployment ke produksi dapat dimulai, item-item berikut harus diselesaikan dan diverifikasi:

- [ ] **Kode Lengkap:** Semua fitur untuk v1.0 telah diimplementasikan.
- [ ] **Pengujian Lulus:** Semua kasus uji Unit dan Integrasi dalam `test_plan.md` berhasil (100% pass rate).
- [ ] **Pengujian E2E Lulus:** Semua kasus uji E2E di lingkungan Staging berhasil.
- [ ] **Konfigurasi Final:**
    - [ ] Semua variabel lingkungan (misalnya, `GCP_PROJECT`) telah didefinisikan.
    - [ ] Semua rahasia (misalnya, `GOOGLE_API_KEY`) telah dibuat di Google Secret Manager.
    - [ ] Service Account untuk Cloud Run memiliki izin IAM yang benar (Cloud Run Invoker, Secret Manager Secret Accessor, dll.).
- [ ] **Infrastruktur Siap:**
    - [ ] Proyek GCP Produksi telah dibuat.
    - [ ] Layanan Cloud Run telah dibuat (tetapi mungkin belum ada revisi yang di-deploy).
    - [ ] API yang diperlukan (Cloud Run, Artifact Registry, Secret Manager) telah diaktifkan.
- [ ] **Rencana Rollback Siap:** Rencana rollback (lihat bagian 6) telah didokumentasikan dan dipahami oleh tim.

## 4. Proses Deployment (Langkah-langkah)

1.  **Langkah 1: Bangun dan Unggah Image Docker**
    *   Gunakan Google Cloud Build untuk membangun image Docker dari cabang `main`.
    *   Cloud Build akan secara otomatis memberi tag pada image (misalnya, dengan hash commit) dan mengunggahnya ke Google Artifact Registry.

2.  **Langkah 2: Deploy ke Staging**
    *   Buat revisi baru di layanan Cloud Run Staging menggunakan image yang baru diunggah.
    *   Arahkan 100% traffic ke revisi baru.

3.  **Langkah 3: Verifikasi di Staging**
    *   Jalankan serangkaian "smoke tests" manual (subset dari kasus uji E2E) terhadap lingkungan Staging.
    *   Periksa log di Cloud Logging untuk setiap kesalahan startup.

4.  **Langkah 4: Deploy ke Produksi**
    *   Setelah verifikasi Staging berhasil, deploy revisi yang sama ke layanan Cloud Run Produksi.
    *   Arahkan 100% traffic ke revisi baru.

5.  **Langkah 5: Verifikasi di Produksi**
    *   Jalankan "smoke tests" manual di ruang chat produksi yang terkontrol.
    *   Tim deployment harus secara aktif memantau log dan metrik (tingkat kesalahan, latensi) di Cloud Monitoring selama 30 menit pertama setelah deployment.

## 5. Rencana Pasca-Deployment

*   **Monitoring:** Pantau dasbor Cloud Monitoring untuk anomali apa pun.
*   **Pengumpulan Umpan Balik:** Gunakan ruang Google Chat khusus (`#infrabot-feedback`) bagi pengguna untuk melaporkan masalah atau memberikan saran.
*   **Proses Pelaporan Bug:** Bug akan dilaporkan sebagai *issues* di repositori Git proyek.

## 6. Rencana Rollback

*   **Pemicu Rollback:**
    *   Tingkat kesalahan server (5xx) melebihi 5% selama 5 menit.
    *   Laporan bug kritis dari pengguna Alpha/Beta yang memengaruhi fungsionalitas inti.
    *   Layanan tidak merespons (crash loop).
*   **Prosedur Rollback:**
    1.  Buka layanan Cloud Run di Google Cloud Console.
    2.  Pilih tab "Revisions".
    3.  Pilih revisi stabil terakhir yang diketahui.
    4.  Klik "Manage Traffic" dan arahkan 100% traffic ke revisi lama tersebut.
    *   **Waktu Estimasi:** < 2 menit.

## 7. Manajemen Risiko

| ID | Deskripsi Risiko | Kemungkinan | Dampak | Strategi Mitigasi | Rencana Kontingensi |
|---|---|---|---|---|---|
| **R-01** | **Keamanan:** Kerentanan dalam *tool* `execute_command` dieksploitasi. | Rendah | Tinggi | - Tinjauan keamanan kode. <br>- Dokumentasi yang jelas tentang risiko *tool* ini. <br>- Menjalankan Cloud Run dengan *service account* berizin paling rendah (*least privilege*). | - Segera nonaktifkan *tool* `execute_command` dengan men-deploy revisi baru yang menghapusnya dari daftar *tool*. <br>- Lakukan analisis post-mortem. |
| **R-02** | **Ketergantungan:** API LLM (Gemini) mengalami pemadaman atau latensi tinggi. | Sedang | Tinggi | - Implementasikan *timeout* yang wajar untuk panggilan API. <br>- Kembalikan pesan kesalahan yang jelas kepada pengguna jika API gagal. | - Komunikasikan status pemadaman kepada pengguna. <br>- Jika pemadaman berlangsung lama, aktifkan "mode pemeliharaan" di mana bot hanya merespons dengan pesan status. |
| **R-03** | **Operasional:** Deployment gagal atau menyebabkan regresi kritis. | Sedang | Sedang | - Wajibkan verifikasi di lingkungan Staging sebelum ke Produksi. <br>- Otomatisasi proses build dan deploy menggunakan Cloud Build untuk mengurangi kesalahan manusia. | - Laksanakan Rencana Rollback (Bagian 6) untuk segera kembali ke versi stabil. |
| **R-04** | **Operasional:** Konfigurasi yang salah (misalnya, kunci API) di-deploy ke produksi. | Sedang | Tinggi | - Simpan semua rahasia di Google Secret Manager. <br>- Lakukan verifikasi "smoke test" segera setelah deployment. | - Perbaiki konfigurasi di Secret Manager. <br>- Mulai ulang (re-deploy) revisi Cloud Run untuk mengambil rahasia yang diperbarui. |
| **R-05** | **Produk:** Adopsi pengguna rendah atau umpan balik negatif. | Sedang | Sedang | - Libatkan pengguna target sejak awal (fase Beta). <br>- Buat dokumentasi pengguna yang jelas dan mudah diakses. <br>- Sediakan saluran umpan balik yang mudah. | - Analisis umpan balik untuk mengidentifikasi area perbaikan. <br>- Prioritaskan fitur atau perbaikan UX dalam sprint berikutnya. |
| **R-06** | **Kinerja:** Bot merespons terlalu lambat di bawah beban normal. | Rendah | Sedang | - Gunakan instance `Agent` tunggal yang diinisialisasi saat startup. <br>- Pilih model LLM yang dioptimalkan untuk kecepatan (misalnya, Gemini Flash). | - Gunakan Cloud Profiler untuk mengidentifikasi *bottleneck* dalam kode. <br>- Tingkatkan batas CPU/memori pada layanan Cloud Run. |
