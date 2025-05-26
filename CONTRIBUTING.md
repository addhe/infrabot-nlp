# Berkontribusi ke Infrabot-NLP

Pertama-tama, terima kasih telah mempertimbangkan untuk berkontribusi pada Infrabot-NLP! Orang-orang seperti Andalah yang membuat Infrabot-NLP menjadi alat yang hebat.

Dokumen ini memberikan pedoman untuk berkontribusi pada proyek ini. Harap baca dengan cermat untuk memastikan kontribusi Anda dapat diintegrasikan dengan lancar.

## Bagaimana Saya Bisa Berkontribusi?

Ada banyak cara Anda dapat berkontribusi pada Infrabot-NLP:

*   **Melaporkan Bug:** Jika Anda menemukan bug, laporkan dengan membuka issue. Sertakan detail sebanyak mungkin, seperti langkah-langkah untuk mereproduksi, perilaku yang diharapkan, dan perilaku aktual.
*   **Mengusulkan Peningkatan:** Jika Anda memiliki ide untuk fitur baru atau peningkatan untuk fitur yang sudah ada, silakan buka issue untuk mendiskusikannya.
*   **Menulis Kode:** Jika Anda ingin berkontribusi kode, harap ikuti panduan di bawah ini.
*   **Memperbaiki Dokumentasi:** Dokumentasi yang baik sangat penting. Jika Anda menemukan area untuk perbaikan atau konten baru untuk ditambahkan, beri tahu kami atau kirimkan pull request.
*   **Menjawab Pertanyaan:** Bantu pengguna lain dengan menjawab pertanyaan di pelacak issue atau forum komunitas lainnya.

## Memulai

1.  **Fork Repositori:** Mulailah dengan melakukan fork pada repositori utama Infrabot-NLP ke akun GitHub Anda.
2.  **Clone Fork Anda:** Clone repositori hasil fork ke komputer lokal Anda:
    ```bash
    git clone https://github.com/NAMA_PENGGUNA_ANDA/infrabot-nlp.git
    cd infrabot-nlp
    ```
3.  **Buat Lingkungan Virtual:** Disarankan untuk bekerja di lingkungan virtual:
    ```bash
    # Pastikan Anda memiliki Python 3.13 atau yang lebih baru terinstal
    python3.13 -m venv venv
    source venv/bin/activate  # Di Windows, gunakan `venv\Scripts\activate`
    ```
4.  **Pasang Dependensi:** Pasang dependensi proyek:
    ```bash
    # Pasang dependensi inti
    pip install -r requirements.txt
    # Pasang dependensi pengembangan
    pip install -r requirements-dev.txt
    pip install -r requirements.txt
    ```
5.  **Buat Cabang Baru:** Buat cabang baru untuk perubahan Anda. Gunakan nama yang deskriptif:
    ```bash
    git checkout -b nama-fitur-anda
    ```

## Melakukan Perubahan

*   **Gaya Pengkodean:** Harap ikuti pedoman gaya pengkodean yang diuraikan dalam `CODING_STYLE.md`.
*   **Pesan Commit:** Tulis pesan commit yang jelas dan ringkas. Ikuti format commit konvensional jika memungkinkan (misalnya, `feat: menambahkan alat GCP baru`, `fix: memperbaiki masalah parsing waktu`).
*   **Pengujian:** Jika Anda menambahkan fitur baru, sertakan pengujian unit. Jika Anda memperbaiki bug, tambahkan pengujian yang mencakup bug tersebut.
*   **Dokumentasi:** Perbarui dokumentasi yang relevan jika perubahan Anda memengaruhi perilaku yang terlihat pengguna atau arsitektur proyek.

## Submitting a Pull Request

1.  **Push Your Changes:** Push your changes to your forked repository:
    ```bash
    git push origin your-feature-name
    ```
2.  **Open a Pull Request:** Go to the original Infrabot-NLP repository on GitHub and open a pull request from your branch to the `main` branch.
3.  **Describe Your Changes:** Provide a clear description of the changes you've made in the pull request. Explain the problem you're solving or the feature you're adding. Link to any relevant issues.
4.  **Code Review:** Your pull request will be reviewed by the maintainers. Be prepared to address any feedback or make further changes.
5.  **Merging:** Once your pull request is approved, it will be merged into the main codebase.

## Code of Conduct

This project and everyone participating in it is governed by a Code of Conduct (to be added). By participating, you are expected to uphold this code. Please report unacceptable behavior.

## Questions?

If you have any questions, feel free to open an issue or reach out to the maintainers.

Thank you for your contribution!