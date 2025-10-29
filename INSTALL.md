# 🛠️ DeepDoc Installation Guide

This guide provides step-by-step instructions for installing and setting up **DeepDoc**, the local AI-powered documentation generator.

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![Ollama Required](https://img.shields.io/badge/Ollama-Required-000000?style=for-the-badge&logo=ollama)](https://ollama.ai)

</div>

## 📋 Prerequisites

Before proceeding with the installation, please ensure your system meets the following requirements:

| Requirement | Status | Check Command | Download/Install Link |
| :--- | :--- | :--- | :--- |
| **Python** (3.11 or higher) | ✅ Required | `python3 --version` | [Official Python Website](https://www.python.org/downloads/) |
| **Ollama** | ✅ Required | `ollama --version` | [Official Ollama Website](https://ollama.ai) |
| **Git** | 💡 Recommended | `git --version` | [Official Git Website](https://git-scm.com/downloads) |

### 1. Python Environment

Ensure you are using a supported version of Python. It is highly recommended to use a **virtual environment** for dependency management to avoid conflicts with system-wide packages.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (Linux/macOS)
source venv/bin/activate

# Activate the virtual environment (Windows)
# .\venv\Scripts\activate
```

### 2. Ollama Setup

DeepDoc relies on **Ollama** for local Large Language Model (LLM) inference.

1.  **Install Ollama** by following the instructions on the [Ollama website](https://ollama.ai).
2.  **Start the Ollama server** in a separate terminal session:
    ```bash
    ollama serve
    ```
    The server should be accessible at `http://localhost:11434`.
3.  **Pull a model** for initial use. We recommend a fast, general-purpose model like `llama3.2` or a code-optimized model like `codellama`:
    ```bash
    ollama pull llama3.2
    ```

---

## ⬇️ Installation Steps

### Step 1: Clone the Repository

Use `git` to clone the DeepDoc repository from GitHub to your local machine:

```bash
# Clone the official repository
git clone https://github.com/Alqudimi/DeepDoc.git

# Navigate into the project directory
cd DeepDoc
```

### Step 2: Install Dependencies

We recommend installing DeepDoc in **editable mode** using `pip`. This allows you to run the tool directly and makes the `docgen` command available globally within your active virtual environment.

#### **Method A: Editable Install (Recommended)**

```bash
# Ensure your virtual environment is active
pip install -e .
```

This command reads the project's dependencies from `pyproject.toml` and installs them, making the package instantly available.

#### **Method B: Manual Dependency Install**

If you prefer not to install the package in editable mode, you can install the core dependencies manually:

```bash
pip install langchain langchain-community langgraph langchain-ollama \
    gitignore-parser pyyaml rich pathspec requests
```

---

## ✅ Verification & Usage

### 1. Verify Installation

After installation, verify that the command-line interface is accessible:

```bash
# Test the CLI using the entry point
python main.py --help

# Or, if installed in editable mode (Method A)
docgen --help
```

You should see the help message listing the available commands (`init`, `generate`).

### 2. Initialize Configuration (Optional)

To customize DeepDoc's behavior, initialize the configuration file:

```bash
python main.py init
# This creates a customizable 'config.yaml' file
```

### 3. Generate Documentation

You are now ready to generate documentation for your project!

```bash
# Generate documentation for the current directory
python main.py generate

# Generate documentation for a specific project path
python main.py generate /path/to/my/codebase
```

---

## ⚠️ Troubleshooting

| Issue | Solution | Command Examples |
| :--- | :--- | :--- |
| **`python: command not found`** | Your system may use `python3` instead of `python`. | `python3 main.py --help` |
| **`Cannot connect to Ollama`** | Ensure the Ollama server is running and accessible. | `ollama serve` or `curl http://localhost:11434` |
| **`ModuleNotFoundError`** | Dependencies were not installed correctly. Re-run the installation command. | `pip install -e .` |
| **Permission Errors** | Use a **virtual environment** (recommended) or use `sudo` (not recommended). | `source venv/bin/activate` |

For further assistance, please refer to the main [README.md](README.md) or open an issue on the [GitHub Repository](https://github.com/Alqudimi/DeepDoc/issues).
