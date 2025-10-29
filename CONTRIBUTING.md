# 🤝 Contributing to DeepDoc

We warmly welcome contributions to **DeepDoc**, the local AI-Powered Documentation Generator. Your input, whether it's code, documentation, bug reports, or feature suggestions, is invaluable to the success of this project.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## 💡 Ways to Contribute

There are many ways you can contribute to DeepDoc:

1.  **Report Bugs**: Help us identify and fix issues.
2.  **Suggest Features**: Propose new ideas to enhance DeepDoc's capabilities.
3.  **Improve Documentation**: Clarify existing guides or write new ones.
4.  **Submit Code**: Implement new features or fix existing bugs.

## 🐛 Reporting Bugs

A good bug report is crucial for a quick fix. Before submitting a new issue, please check the existing issues to see if the problem has already been reported.

To submit a bug report:

1.  **Use the "Bug Report" template** on the [GitHub Issues page](https://github.com/Alqudimi/DeepDoc/issues).
2.  **Describe the environment:** Specify your operating system, Python version, Ollama version, and the DeepDoc commit/version.
3.  **Provide steps to reproduce:** Clearly list the steps that lead to the bug.
4.  **Describe the expected vs. actual behavior.**
5.  **Include relevant logs or tracebacks.**

## ✨ Suggesting Enhancements

We are always looking for ways to make DeepDoc better.

To suggest a new feature:

1.  **Use the "Feature Request" template** on the [GitHub Issues page](https://github.com/Alqudimi/DeepDoc/issues).
2.  **Describe the problem** that the new feature would solve.
3.  **Describe the solution** or the feature you would like to see implemented.
4.  **Provide examples** of how the feature would be used.

## 💻 Code Contributions (Pull Requests)

We follow the standard GitHub flow for code contributions.

### Getting Started

1.  **Fork** the [DeepDoc repository](https://github.com/Alqudimi/DeepDoc).
2.  **Clone** your forked repository locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/DeepDoc.git
    cd DeepDoc
    ```
3.  **Install in Editable Mode** with development dependencies:
    ```bash
    pip install -e .[dev]
    ```
    *(Note: Assuming a `[dev]` extra is defined in `pyproject.toml` for testing/linting tools.)*
4.  **Create a new branch** for your feature or fix:
    ```bash
    git checkout -b feature/your-awesome-feature
    # or
    git checkout -b bugfix/issue-number
    ```

### Making Changes

*   **Follow the Code Style:** DeepDoc uses standard Python conventions (PEP 8). We recommend using a linter like `flake8` or `black`.
*   **Write Tests:** All new features or bug fixes must be accompanied by relevant unit or integration tests in the `tests/` directory.
*   **Run Tests:** Ensure all existing tests pass before committing:
    ```bash
    pytest
    ```

### Submitting the Pull Request (PR)

1.  **Commit your changes** with clear, descriptive commit messages.
    ```bash
    git commit -m "feat: Add support for new Ollama model parameter"
    ```
2.  **Push your branch** to your fork:
    ```bash
    git push origin feature/your-awesome-feature
    ```
3.  **Open a Pull Request** against the `main` branch of the original [Alqudimi/DeepDoc](https://github.com/Alqudimi/DeepDoc) repository.
4.  **Fill out the PR template** completely, describing your changes and linking to any relevant issues.

## 📝 Documentation Contributions

DeepDoc is about documentation, so we take it seriously! If you find an error, a typo, or a section that could be clearer in the `README.md`, `INSTALL.md`, `USAGE.md`, or any other documentation file:

*   Submit a Pull Request with your suggested changes.
*   Ensure your changes are clear, concise, and grammatically correct.

Thank you for helping to make DeepDoc a better tool for the community!
