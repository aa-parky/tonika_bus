# Contributing to Tonika

First off, thank you for considering contributing to Tonika! It’s people like you that make the open-source community such a great place. We welcome any and all contributions, from bug reports to new features, documentation, and more.

This is a personal project born from a love of music and a desire for simpler tools. As we grow, we want to keep the spirit of the project alive: **Music as Resistance**, built with **Goblin Laws** in mind.

## 🧌 The Goblin Way: Our Philosophy

Before you dive in, please take a moment to read our **[Goblin Laws](docs/goblin_laws.md)**. These are the core principles that guide our development. The most important ones for contributors are:

- **Law #7: No Fat Orcs:** Each module, function, or PR should do one thing well. Keep it lean and focused.
- **Law #37: Never Meddle in Another Goblin’s Guts:** All communication between modules **must** go through the `TonikaBus`. No direct calls, no sneaky state changes.
- **Law #8: All Goblins Are Boundary Guards:** If your code touches the outside world (hardware, files, network), it must immediately emit an event to the Bus.

## How Can I Contribute?

### 🐛 Reporting Bugs

If you find a bug, please open an issue on GitHub. A good bug report is one that can be reproduced. Please include:

- A clear and descriptive title.
- A detailed description of the problem.
- Steps to reproduce the bug.
- The expected behavior and what happened instead.
- Your environment (OS, Python version, `tonika_bus` version).

Use the **Bug Report** issue template to get started.

### ✨ Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, please open an issue to discuss it. This allows us to coordinate efforts and make sure your idea aligns with the project's vision.

Use the **Feature Request** issue template to provide context.

### 📝 Pull Requests

We welcome pull requests! Here’s how to submit one:

1.  **Fork the repository** and create your branch from `develop`.
2.  **Set up your development environment** (see below).
3.  **Make your changes.** Remember the Goblin Laws!
4.  **Add tests** for your changes. We aim for high coverage.
5.  **Update the documentation** if you’ve added or changed functionality.
6.  **Ensure all tests pass** and the linter is happy.
7.  **Submit your pull request** to the `develop` branch.

## 🛠️ Development Setup

Getting set up for local development is straightforward.

1.  **Clone your fork:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/tonika_bus.git
    cd tonika_bus
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install all dependencies:**

    This installs the core library in editable mode, plus all development and testing tools.

    ```bash
    pip install -e ".[all]"
    ```

## ✅ Running Tests and Checks

Before submitting a pull request, please run the full suite of local checks.

1.  **Run all tests with coverage:**

    ```bash
    pytest
    ```

2.  **Run the linter:**

    ```bash
    ruff check src/ tests/
    ```

3.  **Run the type checker:**

    ```bash
    mypy src/tonika_bus/core/
    ```

Our CI pipeline will run these checks automatically, but running them locally first will save you time.

## ✍️ Code Style

- We use **Black** for code formatting with a line length of 100 characters.
- We use **ruff** for linting and import sorting.
- We use **mypy** for static type checking.
- Docstrings should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#3.8-comments-and-docstrings).

## 📜 A Note on Licensing

By contributing, you agree that your contributions will be licensed under the **GPL-3.0 License** that covers the project. Feel free to contact the maintainers if that’s a concern.

Thank you for helping us build tools for musical resistance! Now go make some noise! 🎵

