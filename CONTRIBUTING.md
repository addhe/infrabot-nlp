# Contributing to Infrabot-NLP

First off, thank you for considering contributing to Infrabot-NLP! It's people like you that make Infrabot-NLP such a great tool.

This document provides guidelines for contributing to this project. Please read it carefully to ensure that your contributions can be integrated smoothly.

## How Can I Contribute?

There are many ways you can contribute to Infrabot-NLP:

*   **Reporting Bugs:** If you find a bug, please report it by opening an issue. Include as much detail as possible, such as steps to reproduce, expected behavior, and actual behavior.
*   **Suggesting Enhancements:** If you have an idea for a new feature or an improvement to an existing one, please open an issue to discuss it.
*   **Writing Code:** If you'd like to contribute code, please follow the guidelines below.
*   **Improving Documentation:** Good documentation is crucial. If you find areas for improvement or new content to add, please let us know or submit a pull request.
*   **Answering Questions:** Help other users by answering questions in the issue tracker or other community forums.

## Getting Started

1.  **Fork the Repository:** Start by forking the main Infrabot-NLP repository to your GitHub account.
2.  **Clone Your Fork:** Clone your forked repository to your local machine:
    ```bash
    git clone https://github.com/YOUR_USERNAME/infrabot-nlp.git
    cd infrabot-nlp
    ```
3.  **Create a Virtual Environment:** It's recommended to work in a virtual environment:
    ```bash
    # Make sure you have Python 3.13 or later installed
    python3.13 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
4.  **Install Dependencies:** Install the project dependencies:
    ```bash
    # Install core dependencies
    pip install -r requirements.txt
    # Install development dependencies
    pip install -r requirements-dev.txt
    pip install -r requirements.txt
    ```
5.  **Create a Branch:** Create a new branch for your changes. Use a descriptive name:
    ```bash
    git checkout -b your-feature-name
    ```

## Making Changes

*   **Coding Style:** Please follow the coding style guidelines outlined in `CODING_STYLE.md`.
*   **Commit Messages:** Write clear and concise commit messages. Follow the conventional commit format if possible (e.g., `feat: add new GCP tool`, `fix: resolve issue with time parsing`).
*   **Tests:** If you add new features, please include unit tests. If you fix a bug, add a test that covers the bug.
*   **Documentation:** Update any relevant documentation if your changes affect user-facing behavior or the project's architecture.

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