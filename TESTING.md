# Panduan Pengujian

Dokumen ini menguraikan strategi dan pedoman pengujian untuk proyek `infrabot-nlp`.

## Daftar Isi

- [Pendahuluan](#pendahuluan)
- [Jenis-Jenis Pengujian](#jenis-jenis-pengujian)
  - [Pengujian Unit](#pengujian-unit)
  - [Pengujian Integrasi](#pengujian-integrasi)
  - [Pengujian End-to-End (E2E)](#pengujian-end-to-end-e2e)
- [Alat dan Kerangka Kerja](#alat-dan-kerangka-kerja)
- [Menjalankan Pengujian](#menjalankan-pengujian)
  - [Menjalankan Pengujian Unit](#menjalankan-pengujian-unit)
  - [Menjalankan Pengujian Integrasi](#menjalankan-pengujian-integrasi)
  - [Menjalankan Semua Pengujian](#menjalankan-semua-pengujian)
- [Cakupan Pengujian](#cakupan-pengujian)
- [Menulis Pengujian](#menulis-pengujian)
  - [Panduan Umum](#panduan-umum)
  - [Konvensi Penamaan](#konvensi-penamaan)
  - [Mocking](#mocking)
- [Integrasi Berkelanjutan (CI)](#integrasi-berkelanjutan-ci)
- [Melaporkan Masalah](#melaporkan-masalah)

## Pendahuluan

Tujuan pengujian dalam proyek ini adalah untuk memastikan keandalan, kebenaran, dan ketangguhan aplikasi. Dokumen ini memberikan panduan tentang cara menulis, menjalankan, dan memelihara pengujian.

## Jenis-Jenis Pengujian

Kami menggunakan beberapa jenis pengujian untuk mencakup berbagai aspek aplikasi:

### Pengujian Unit

- **Tujuan**: Menguji komponen atau fungsi individual secara terisolasi.
- **Lokasi**: Biasanya terletak di direktori `tests/unit` di samping kode yang diuji atau di dalam modul itu sendiri.
- **Karakteristik**: Cepat, terisolasi, dan menggunakan mock untuk dependensi eksternal.

### Pengujian Integrasi

- **Tujuan**: Menguji interaksi antara beberapa komponen atau layanan. Termasuk pengujian interaksi dengan API eksternal (misalnya, Google Gemini, OpenAI, GCP).
- **Lokasi**: Biasanya terletak di direktori `tests/integration`.
- **Karakteristik**: Lebih lambat dibanding pengujian unit, mungkin memerlukan layanan eksternal yang tersedia atau dimock pada tingkat yang lebih tinggi.

### Pengujian End-to-End (E2E)

- **Tujuan**: Menguji alur aplikasi secara keseluruhan dari perspektif pengguna, mensimulasikan skenario pengguna nyata. Ini melibatkan menjalankan aplikasi CLI dengan berbagai masukan dan memverifikasi keluarannya.
- **Lokasi**: Biasanya terletak di direktori `tests/e2e`.
- **Karakteristik**: Jenis pengujian yang paling lambat, membutuhkan aplikasi penuh yang dapat dijalankan.

## Tools and Frameworks

Our testing stack includes:

- `pytest` (latest version) as the primary testing framework
- `pytest-cov` for code coverage reporting
- `pytest-asyncio` for testing async code
- `pytest-mock` for mocking
- `responses` for mocking HTTP requests

## Requirements

- Python 3.13 or later
- `pytest` 8.0.0 or later
- All dependencies listed in `requirements-dev.txt`

## Running Tests

### Setting Up the Test Environment

```bash
# Create and activate a virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Unit Tests

```bash
# Example:
# python -m unittest discover -s tests/unit
# pytest tests/unit
```

### Running Integration Tests

```bash
# Example:
# python -m unittest discover -s tests/integration
# pytest tests/integration
```

### Running All Tests

```bash
# Example:
# python -m unittest discover
# pytest
```

## Test Coverage

We aim for a high level of test coverage. Reports can be generated using [Coverage Tool].

```bash
# Example:
# coverage run -m pytest
# coverage report -m
# coverage html
```

Strive to cover all critical paths and business logic.

## Writing Tests

### General Guidelines

- Tests should be clear, concise, and easy to understand.
- Each test should focus on a single piece of functionality.
- Tests should be independent and runnable in any order.
- Avoid testing implementation details; focus on behavior.
- Use descriptive names for test functions and classes.
- Clean up any resources created during a test (e.g., temporary files, database entries).

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test<ModuleName>` or `Test<ClassName>`
- Test methods: `test_<description_of_behavior>()`

### Mocking

- Use mocking libraries to isolate components and avoid dependencies on external services for unit tests.
- Clearly indicate what is being mocked and why.

## Continuous Integration (CI)

All tests should be run automatically as part of the CI pipeline on every push and pull request. This helps to catch regressions early.

*(Specify CI provider and configuration details if applicable, e.g., GitHub Actions, GitLab CI)*

## Reporting Bugs

If a test fails or a bug is discovered:

1.  Create an issue in the project's issue tracker.
2.  Provide detailed steps to reproduce the bug.
3.  Include the expected behavior and the actual behavior.
4.  If possible, write a failing test that reproduces the bug before fixing it (Test-Driven Development).

# Testing Guide

This document outlines the testing strategy and procedures for the Infrabot-NLP project.

## Test-Driven Development (TDD)

We follow a strict TDD approach:

1. Write a failing test
2. Write minimal code to make the test pass
3. Refactor while keeping tests green

## Setting Up Test Environment

```bash
# Create and activate virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run specific test file
pytest tests/unit/my_cli_agent/test_agent.py

# Run tests matching pattern
pytest -k "test_should_process_command"

# Run tests for specific component
pytest tests/unit/my_cli_agent/tools/
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Agent tests
   - Provider tests
   - Tool tests

2. **Integration Tests** (`tests/integration/`)
   - API integration
   - Tool chaining
   - End-to-end workflows

## Writing Tests

### Test File Structure

```python
"""Module docstring explaining the test purpose."""
import pytest
from unittest.mock import Mock, patch

class TestMyComponent:
    @pytest.fixture
    def my_fixture(self):
        # Setup
        yield setup_result
        # Teardown

    def test_should_describe_expected_behavior(self):
        # Arrange
        input_data = "test"
        
        # Act
        result = process(input_data)
        
        # Assert
        assert result.success is True
```

### Mocking External Services

For tests involving external services (API calls, file system, etc.), always use mocking:

```python
@patch('my_cli_agent.providers.openai.OpenAI')
def test_should_call_openai_api(mock_openai):
    mock_openai.return_value.chat.completions.create.return_value = {
        'choices': [{'message': {'content': 'test'}}]
    }
    # Test implementation
```

## Coverage Requirements

- Overall coverage: minimum 80%
- Critical paths: 100%
- New features: must include tests
- Bug fixes: must include regression tests

## Continuous Integration

Tests are automatically run on:
- Every pull request
- Main branch commits
- Release tags

## Common Test Patterns

1. **Error Handling Tests**
```python
def test_should_handle_api_error(self):
    with pytest.raises(APIError) as exc_info:
        # Test implementation
    assert "API Error" in str(exc_info.value)
```

2. **Parameterized Tests**
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2")
])
def test_should_handle_various_inputs(self, input, expected):
    assert process(input) == expected
```

## Test Documentation

Every test should:
- Have a clear docstring explaining the test purpose
- Follow the Arrange-Act-Assert pattern
- Use descriptive test names that explain the behavior
- Include comments for complex test setups