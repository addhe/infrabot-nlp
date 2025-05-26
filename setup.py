from setuptools import setup, find_packages

setup(
    name="infrabot-nlp",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "google-generativeai",
        "openai",
        "anthropic",
        "python-dotenv",
        "google-cloud-core",
        "google-cloud-resource-manager",
        "google-adk>=0.1.0"
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.5",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "responses>=0.24.1",
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0"
        ]
    }
)
