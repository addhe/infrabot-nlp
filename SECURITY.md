# Kebijakan Keamanan

Keamanan proyek ini sangat kami perhatikan. Kami menghargai upaya Anda untuk mengungkapkan temuan Anda secara bertanggung jawab.

## Melaporkan Kerentanan Keamanan

Jika Anda menemukan kerentanan keamanan dalam proyek ini, harap laporkan kepada kami sesegera mungkin. Kami meminta Anda untuk tidak mengungkapkan kerentanan tersebut secara publik sampai kami memiliki kesempatan untuk menanganinya.

Silakan kirim temuan Anda ke `security@infrabot-nlp.dev`.

Saat melaporkan kerentanan, sertakan detail berikut:

*   Deskripsi yang jelas tentang kerentanan tersebut.
*   Langkah-langkah untuk mereproduksi kerentanan.
*   Versi perangkat lunak yang terpengaruh.
*   Dampak potensial dari kerentanan tersebut.
*   Saran mitigasi, jika ada.

Kami akan mengonfirmasi penerimaan laporan kerentanan Anda dalam waktu 24 jam dan akan bekerja sama dengan Anda untuk memahami dan memvalidasi masalahnya. Kami berupaya untuk menangani semua kerentanan keamanan yang valid tepat waktu.

## Kebijakan Pengungkapan

Setelah kerentanan ditangani, kami dapat mengungkap detail kerentanan tersebut kepada publik. Kami akan berkoordinasi dengan pelapor mengenai waktu dan isi pengungkapan. Kami juga dapat memilih untuk tidak mengungkapkan kerentanan tertentu tergantung pada situasinya.

## Praktik Keamanan Terbaik untuk Pengguna

*   **Kunci API**: Aplikasi ini memerlukan kunci API untuk berbagai layanan AI.
    *   **Jangan pernah melakukan commit kunci API Anda ke repositori apa pun.**
    *   Gunakan variabel lingkungan atau file `.env` (yang seharusnya diabaikan oleh git) untuk menyimpan kunci Anda.
    *   Saat menggunakan Docker, teruskan kunci API Anda sebagai variabel lingkungan ke container.
    *   Berhati-hatilah saat berbagi log atau tangkapan layar yang mungkin berisi kunci API Anda.
*   **Dependensi**: Perbarui dependensi lokal Anda secara teratur dengan menjalankan `pip install -r requirements.txt --upgrade`.
*   **Lingkungan**: Jalankan aplikasi ini di lingkungan yang tepercaya. Berhati-hatilah dengan perintah yang Anda minta untuk dieksekusi oleh AI, terutama jika melibatkan modifikasi sistem atau akses ke data sensitif.
*   **Pembersihan Input**: Meskipun aplikasi dapat mencoba menangani berbagai input, perhatikan prompt yang Anda berikan ke model AI, terutama jika dibuat dari sumber yang tidak tepercaya.

## Ruang Lingkup

Kebijakan keamanan ini berlaku untuk proyek `infrabot-nlp` dan komponen intinya. Kebijakan ini tidak berlaku untuk:

*   Kerentanan dalam dependensi pihak ketiga (harap laporkan ke proyek masing-masing).
*   Keamanan model AI yang mendasari (Gemini, GPT, Claude) itu sendiri (harap laporkan ke Google, OpenAI, atau Anthropic, masing-masing).
*   Keamanan Google Cloud Platform (GCP) (harap laporkan ke Google Cloud).

## Kontak

Untuk pertanyaan atau masalah keamanan yang bukan laporan kerentanan, silakan hubungi `[EMAIL_PROYEK_ATAU_PEMELIHARA]`.

Kami menghargai kontribusi para peneliti keamanan dan komunitas yang lebih luas dalam membantu kami memelihara proyek yang aman.