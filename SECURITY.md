# Security Policy

The security of this project is taken seriously. We appreciate your efforts to responsibly disclose your findings.

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it to us as soon as possible. We request that you do not disclose the vulnerability publicly until we have had a chance to address it.

Please email your findings to `security@infrabot-nlp.dev`.

When reporting a vulnerability, please include the following details:

*   A clear description of the vulnerability.
*   Steps to reproduce the vulnerability.
*   The affected version(s) of the software.
*   Any potential impact of the vulnerability.
*   Any suggested mitigations, if you have any.

We will acknowledge receipt of your vulnerability report within 24 hours and will work with you to understand and validate the issue. We aim to address all valid security vulnerabilities in a timely manner.

## Disclosure Policy

Once a vulnerability has been addressed, we may disclose the vulnerability details publicly. We will coordinate with the reporter on the timing and content of the disclosure. We may also choose not to disclose certain vulnerabilities depending on the circumstances.

## Security Best Practices for Users

*   **API Keys**: This application requires API keys for various AI services.
    *   **Never commit your API keys to any repository.**
    *   Use environment variables or a `.env` file (which should be gitignored) to store your keys.
    *   When using Docker, pass your API keys as environment variables to the container.
    *   Be careful when sharing logs or screenshots that might contain your API keys.
*   **Dependencies**: Keep your local dependencies up to date by regularly running `pip install -r requirements.txt --upgrade`.
*   **Environment**: Run this application in a trusted environment. Be cautious about the commands you ask the AI to execute, especially if they involve system modifications or access to sensitive data.
*   **Input Sanitization**: While the application may attempt to handle various inputs, be mindful of the prompts you provide to the AI models, especially if they are constructed from untrusted sources.

## Scope

This security policy applies to the `infrabot-nlp` project and its core components. It does not apply to:

*   Vulnerabilities in third-party dependencies (please report those to the respective projects).
*   The security of the underlying AI models (Gemini, GPT, Claude) themselves (please report those to Google, OpenAI, or Anthropic, respectively).
*   The security of the Google Cloud Platform (GCP) (please report those to Google Cloud).

## Contact

For any security-related questions or concerns that are not vulnerability reports, please contact `[PROJECT_EMAIL_OR_MAINTAINER_EMAIL]`.

We value the contributions of security researchers and the broader community in helping us maintain a secure project.