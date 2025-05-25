# Coding Style Guide / Pedoman Gaya Penulisan Kode

This document outlines the coding style guidelines for the Gemini-ChatGPT CLI project. These guidelines
follow Python PEP 8 standards with project-specific adaptations, targeting Python 3.13+ features.

Dokumen ini menjelaskan pedoman gaya penulisan kode untuk proyek Gemini-ChatGPT CLI. Pedoman ini
mengikuti standar Python PEP 8 dengan penyesuaian khusus untuk proyek ini, menargetkan fitur Python 3.13+.

## General Principles / Prinsip Umum

- Code readability is paramount / Keterbacaan kode sangat penting
- Maintain consistency throughout the codebase / Konsistensi dalam seluruh codebase harus dipertahankan
- Code should be easily understood and maintained by others / Kode harus mudah dipahami dan dipelihara oleh orang lain
- Leverage Python 3.13+ features when beneficial / Manfaatkan fitur Python 3.13+ bila bermanfaat

## Konvensi Penamaan

- **Nama Modul**: Gunakan nama pendek, huruf kecil semua. Contoh: `agent.py`, `tools.py`.
- **Nama Kelas**: Gunakan CapWords (PascalCase). Contoh: `Agent`, `ToolResult`.
- **Nama Fungsi**: Gunakan snake_case. Contoh: `get_current_time()`, `list_gcp_projects()`.
- **Nama Variabel**: Gunakan snake_case. Contoh: `api_key`, `project_list`.
- **Konstanta**: Gunakan huruf besar semua dengan underscore. Contoh: `MAX_RETRY`, `API_TIMEOUT`.

## Format Kode

### Indentasi dan Spasi

- Gunakan 4 spasi untuk indentasi, bukan tab.
- Gunakan spasi di sekitar operator. Contoh: `x = 1 + 2`.
- Tidak ada spasi di dalam tanda kurung. Contoh: `func(arg1, arg2)`.
- Tambahkan spasi setelah koma. Contoh: `[1, 2, 3]`.
- Tidak ada spasi sebelum koma. Contoh: `dict(key1=val1, key2=val2)`.

### Panjang Baris

- **Maksimal 100 karakter per baris**.
- Jika baris terlalu panjang, pecah dengan menggunakan tanda lanjutan baris (`\`) atau tanda kurung.

```python
# Contoh pemecahan baris yang baik
result = some_function_with_long_name(
    parameter1, parameter2, parameter3,
    parameter4, parameter5
)

# Atau menggunakan operator
total = (value1 + value2 + value3 +
         value4 + value5 + value6)
```

### Impor

- Impor harus dikelompokkan dalam urutan berikut:
  1. Modul standar Python
  2. Modul pihak ketiga terkait
  3. Modul lokal aplikasi
- Setiap kelompok harus dipisahkan oleh satu baris kosong.
- Impor harus berada di awal file, setelah komentar modul dan docstring.

```python
# Contoh pengurutan impor yang baik
import os
import sys
import datetime

import google.auth
import google.generativeai as genai

from .tools import get_current_time, execute_command
```

## Dokumentasi

### Docstrings

- Semua modul, kelas, dan fungsi publik harus memiliki docstring.
- Gunakan format docstring Google style.
- Docstring harus menjelaskan apa yang dilakukan, parameter input, dan nilai return.

```python
def list_gcp_projects(env: str) -> ToolResult:
    """Lists Google Cloud Platform (GCP) projects for a specified environment.
    
    Args:
        env (str): The environment to list projects for (dev/stg/prod)
        
    Returns:
        ToolResult: Contains the list of projects or error information
    """
```

### Komentar

- Komentar harus menjelaskan "mengapa", bukan "apa" atau "bagaimana".
- Komentar harus ditulis dalam bahasa yang jelas dan ringkas.
- Hindari komentar yang tidak perlu yang hanya mengulangi kode.

## Penanganan Error

- Gunakan blok try-except untuk menangani error.
- Tangkap exception spesifik daripada semua exception.
- Berikan pesan error yang informatif.

```python
try:
    result = api_function()
except ApiError as e:
    print(f"API error occurred: {e}")
    # Fallback logic
except ConnectionError as e:
    print(f"Connection failed: {e}")
    # Fallback logic
```

## Pengujian

- Setiap fungsi utama harus memiliki unit test.
- Test harus mencakup kasus normal dan edge case.
- Gunakan mock untuk menguji komponen yang bergantung pada layanan eksternal.

## Linting dan Formatting

- Gunakan tools berikut untuk memastikan kode mengikuti pedoman:
  - `black` untuk formatting otomatis
  - `flake8` untuk linting
  - `mypy` untuk type checking

## Versioning

- Ikuti [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).
- Update versi dalam file `__version__.py` atau `setup.py`.

---

Pedoman ini dibuat untuk memastikan kualitas dan konsistensi kode dalam proyek Gemini-ChatGPT CLI.
Semua kontributor diharapkan untuk mengikuti pedoman ini.
