# Testing

This document outlines the testing strategy and guidelines for the `infrabot-nlp` project.

## Table of Contents

- [Introduction](#introduction)
- [Types of Tests](#types-of-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [End-to-End (E2E) Tests](#end-to-end-e2e-tests)
- [Tools and Frameworks](#tools-and-frameworks)
- [Running Tests](#running-tests)
  - [Running Unit Tests](#running-unit-tests)
  - [Running Integration Tests](#running-integration-tests)
  - [Running All Tests](#running-all-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
  - [General Guidelines](#general-guidelines)
  - [Naming Conventions](#naming-conventions)
  - [Mocking](#mocking)
- [Continuous Integration (CI)](#continuous-integration-ci)
- [Reporting Bugs](#reporting-bugs)

## Introduction

The purpose of testing in this project is to ensure the reliability, correctness, and robustness of the application. This document provides guidance on how to write, run, and maintain tests.

## Types of Tests

We employ several types of tests to cover different aspects of the application:

### Unit Tests

- **Purpose**: To test individual components or functions in isolation.
- **Location**: Typically located in a `tests/unit` directory alongside the code they are testing or within the module itself.
- **Characteristics**: Fast, isolated, and mock external dependencies.

### Integration Tests

- **Purpose**: To test the interaction between multiple components or services. This includes testing interactions with external APIs (e.g., Google Gemini, OpenAI, GCP).
- **Location**: Typically located in a `tests/integration` directory.
- **Characteristics**: Slower than unit tests, may require external services to be available or mocked at a higher level.

### End-to-End (E2E) Tests

- **Purpose**: To test the entire application flow from the user's perspective, simulating real user scenarios. This involves running the CLI application with various inputs and verifying the output.
- **Location**: Typically located in a `tests/e2e` directory.
- **Characteristics**: Slowest type of test, requires the full application to be runnable.

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