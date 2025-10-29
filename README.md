<div align="center">

# <img src="assists/images/logo.png" alt="DeepDoc Logo" width="150"/>

# DeepDoc: The Local AI-Powered Documentation Generator

[![GitHub Repository](https://img.shields.io/badge/GitHub-Alqudimi%2FDeepDoc-blue?style=for-the-badge&logo=github)](https://github.com/Alqudimi/DeepDoc)
[![License](https://img.shields.io/github/license/Alqudimi/DeepDoc?style=for-the-badge&color=success)](https://github.com/Alqudimi/DeepDoc/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![Ollama Required](https://img.shields.io/badge/Ollama-Required-000000?style=for-the-badge&logo=ollama)](https://ollama.ai)
[![Docker Build](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://docs.docker.com/get-started/)

</div>

---

**DeepDoc** is a powerful, local-first Command Line Interface (CLI) tool and **FastAPI service** designed to generate **comprehensive, publication-ready Markdown documentation** for any codebase. Leveraging the power of **Ollama**, **LangChain**, and **LangGraph**, DeepDoc ensures your project documentation is always accurate, detailed, and up-to-date, all while keeping your code secure on your local machine.

## 🚀 Key Features & SEO Highlights

DeepDoc is engineered for efficiency and security, offering a suite of features that make documentation a seamless part of your development workflow.

| Category | Feature | Description | SEO Keywords |
| :--- | :--- | :--- | :--- |
| **Local-First AI** | 🧠 **Offline Documentation Generation** | Utilizes **Ollama** for completely offline, on-premise documentation. Your code never leaves your machine. | `Local AI`, `Offline Documentation`, `Ollama`, `Secure Documentation` |
| **Deployment** | 🐳 **Docker & API Support** | Includes `Dockerfile` and `docker-compose.yml` for easy containerization and deployment as a **FastAPI** service. | `FastAPI`, `Docker`, `Containerized AI`, `Documentation API` |
| **Code Analysis** | 🔍 **Intelligent Project Scanner** | Recursively scans directories, respects `.gitignore`, and accurately detects programming languages, frameworks, and dependencies. | `Codebase Analysis`, `Project Scanner`, `Git Ignore Support`, `Dependency Analysis` |
| **Output Quality** | 📚 **Comprehensive Output Suite** | Generates a full suite of documents: `README.md`, `SUMMARY.md`, `ARCHITECTURE.md`, `API.md`, and `CONTRIBUTING.md`. | `Auto-generate README`, `API Reference Generation`, `Architecture Documentation` |
| **Extensibility** | ⚙️ **Highly Customizable Workflow** | Configure tone, verbosity, LLM model, and file filtering via a simple `config.yaml`. Orchestrated by a robust **LangGraph** workflow. | `LangChain Workflow`, `LangGraph`, `Customizable LLM`, `YAML Configuration` |
| **Developer Experience** | 🎨 **Rich CLI & Interactive Docs** | Features a beautiful, rich terminal UI with progress bars and colorful output. Generated Markdown includes interactive elements like collapsible sections and Mermaid diagrams. | `CLI Tool`, `Rich Terminal UI`, `Mermaid Diagrams`, `Interactive Markdown` |

## ⚙️ Prerequisites

Before you can unleash the power of DeepDoc, ensure the following are installed and running on your system:

1.  **Python 3.12+**: The core language environment. **(Updated from 3.11)**
    ```bash
    python3 --version
    # Must be 3.12 or higher
    ```
2.  **Ollama**: The local LLM runtime.
    *   Install from the official [Ollama website](https://ollama.ai).
    *   Ensure the Ollama server is running: `ollama serve`
    *   Pull a model for use (e.g., `llama3.2` or `codellama`):
        ```bash
        ollama pull llama3.2
        ```
3.  **Docker (Optional)**: Required for running the containerized API service.

## ⬇️ Installation

For detailed, step-by-step installation instructions, please refer to the dedicated [INSTALL.md](INSTALL.md) file.

**Quick Install (Recommended):**

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Alqudimi/DeepDoc.git
    cd DeepDoc
    ```
2.  **Install Dependencies in Editable Mode:**
    ```bash
    pip install -e .
    ```
    This method installs DeepDoc as a package, making the `docgen` command available globally.

### Docker Deployment

To run DeepDoc as a containerized API service:

1.  **Build the Docker image:**
    ```bash
    docker-compose build
    ```
2.  **Run the service:**
    ```bash
    docker-compose up
    ```
    The API will be available at `http://localhost:5000`. Refer to the [API_README.md](API_README.md) for endpoint details.

## 💡 Usage Guide

DeepDoc provides a simple, intuitive command-line interface. For a comprehensive guide, see [USAGE.md](USAGE.md).

### 1. Initialize Configuration (Optional)

Generate a `config.yaml` file to customize the documentation process, including LLM model choice, style, and file filtering.

```bash
python main.py init
# A config.yaml file is created in your current directory
```

### 2. Generate Documentation

Run the `generate` command to analyze your project and produce the documentation files in the specified output directory (default: `docs/`).

| Command | Description | Example |
| :--- | :--- | :--- |
| **Current Directory** | Generates docs for the directory where the command is run. | `python main.py generate` |
| **Specific Path** | Generates docs for a target project path. | `python main.py generate /path/to/your/project` |
| **Custom Config** | Use a configuration file other than the default `config.yaml`. | `python main.py generate -c custom-config.yaml` |
| **Specify Model** | Override the default Ollama model set in the config. | `python main.py generate -m codellama` |
| **Overwrite** | Force overwrite of existing documentation files. | `python main.py generate --overwrite` |

## 🏗️ Project Structure & Generated Output

The project now includes both a CLI and a robust API component.

```
DeepDoc/
├── src/
│   ├── api/                   # 🐳 FastAPI service for documentation generation
│   │   ├── main.py            # API entry point (runs on Uvicorn)
│   │   ├── routes/            # API endpoints (analyze, config, docs, status)
│   │   └── services/          # Core documentation service logic
│   └── docgen/                # 💻 Core CLI logic
│       ├── core/              # Configuration, Scanner, LLM Client, LangGraph Workflow
│       ├── analyzers/         # Code and Dependency Analyzers
│       └── generators/        # Documentation Writers
├── tests/
│   └── api/                   # Unit and integration tests for the API
├── docs/                      # Default output directory for generated documentation
├── main.py                    # CLI entry point
├── pyproject.toml             # Project metadata and dependencies (Python 3.12+)
├── Dockerfile                 # Docker build file for the API service
├── docker-compose.yml         # Docker orchestration for easy setup
├── API_README.md              # Documentation for the API service
├── USAGE.md                   # Detailed usage guide for the CLI
└── README.md                  # This file
```

## 🛡️ Privacy and Security

DeepDoc is built with a strong commitment to privacy and security:

*   **100% Local Processing**: All code analysis and documentation generation occur exclusively on your local machine or within your private Docker container.
*   **No External APIs**: Your codebase is never transmitted to any external service or cloud API.
*   **Offline Operation**: Once the Ollama model is downloaded, the tool can run completely offline.

## 🤝 Contributing to DeepDoc

We welcome contributions from the community! Whether it's adding new features, improving the prompt engineering, or enhancing the code analysis capabilities, your input is valuable.

1.  **Fork** the [DeepDoc repository](https://github.com/Alqudimi/DeepDoc).
2.  **Clone** your fork.
3.  Create a new **feature branch**.
4.  Make your changes and ensure tests pass.
5.  **Commit** your work and **push** to your fork.
6.  Open a **Pull Request** to the `main` branch of the original repository.

## 📄 License

This project is licensed under the [MIT License](https://github.com/Alqudimi/DeepDoc/blob/main/LICENSE).

## 🧑‍💻 Developer & Repository

| Detail | Value |
| :--- | :--- |
| **Developer** | Abdulaziz Alqudimi |
| **Email** | [eng7mi@gmail.com](mailto:eng7mi@gmail.com) |
| **Repository** | [https://github.com/Alqudimi/DeepDoc](https://github.com/Alqudimi/DeepDoc) |

---

<div align="center">

**DeepDoc: Document Smarter, Not Harder. Built with ❤️ for the developer community.**

</div>
