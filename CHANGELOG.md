# Catatan Perubahan

Semua perubahan penting pada proyek ini akan didokumentasikan dalam file ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
dan proyek ini mengikuti [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
- GCP project listing now shows project status (e.g., [ACTIVE], [DELETE_REQUESTED])
- GCP project deletion now gives clear feedback if a project is not active or already scheduled for deletion
- Batch deletion of GCP projects via ADK agent
- Improved error handling and user feedback for GCP operations

## [0.1.0] - 2025-05-25

### Ditambahkan
- Versi pertama aplikasi.
- Dukungan untuk model Gemini, GPT, dan Claude melalui implementasi API langsung.
- Dukungan untuk integrasi Gemini yang ditingkatkan melalui ADK Google.
- Alat untuk eksekusi perintah shell, pengecekan waktu, dan manajemen proyek GCP.
- Peningkatan dokumentasi dan cakupan pengujian.
- Verifikasi kompatibilitas macOS.