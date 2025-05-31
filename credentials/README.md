# Cara Mengatur Service Account Key GCP untuk Infrabot-NLP

## Langkah 1: Membuat Service Account di Google Cloud Console
1. Login ke [Google Cloud Console](https://console.cloud.google.com/)
2. Pilih project Anda atau buat project baru
3. Buka menu IAM & Admin > Service Accounts
4. Klik "Create Service Account"
5. Isi nama dan deskripsi service account
6. Tambahkan peran yang sesuai (minimal roles/viewer untuk melihat projects)
   - Untuk melihat projects: roles/viewer atau roles/browser
   - Untuk membuat/menghapus projects: roles/resourcemanager.projectCreator dan roles/resourcemanager.projectDeleter
7. Klik "Continue" dan "Done"

## Langkah 2: Membuat Service Account Key
1. Klik service account yang baru dibuat
2. Pilih tab "Keys"
3. Klik "Add Key" > "Create new key"
4. Pilih format JSON
5. Klik "Create" untuk mengunduh file key JSON

## Langkah 3: Menyimpan Service Account Key
1. Simpan file JSON yang diunduh ke direktori `credentials/` dengan nama `gcp-service-account-key.json`
2. File ini berisi informasi sensitif, jangan bagikan atau commit ke repository

## Langkah 4: Menggunakan Service Account Key
Service account key akan digunakan secara otomatis saat menjalankan aplikasi melalui environment variable GOOGLE_APPLICATION_CREDENTIALS yang sudah dikonfigurasi.

## Keamanan
- Jangan pernah memasukkan service account key ke dalam repository Git
- File .gitignore sudah dikonfigurasi untuk mengabaikan semua file di direktori credentials/ kecuali contoh
- Gunakan service account dengan prinsip least privilege (hak akses minimal yang diperlukan)
- Rotasi (perbarui) service account key secara berkala
