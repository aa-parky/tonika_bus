# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD pipeline with GitHub Actions for automated testing across Python 3.11, 3.12, and 3.13.
- Coveralls integration for test coverage reporting and history.
- `CONTRIBUTING.md` with detailed guidelines for new contributors.
- `CHANGELOG.md` to track notable changes between versions.
- `.coveragerc` file to standardize coverage configuration.

### Changed
- The `test` job in the CI workflow now uploads coverage reports to Coveralls.
- The `pyproject.toml` file is now used by the CI to install dependencies.

### Fixed
- Corrected 5 `mypy` type-checking errors in `src/tonika_bus/core/bus.py`.

## [0.2.0] - 2025-10-05

### Added
- Initial public release of `tonika_bus`.
- Core components: `TonikaBus` (singleton event broker), `TonikaModule` (base class), and `TonikaEvent` (data structure).
- Comprehensive test suite with 111 tests and 99% code coverage.
- Extensive documentation including a detailed `README.md`, `docs/tonika_bus_readme.md`, and the philosophical `docs/goblin-laws.md`.
- Four example modules demonstrating core concepts like pub/sub, request/response, and module dependencies.
- `pyproject.toml` for modern, PEP 517-compliant packaging and tool configuration (ruff, mypy, pytest, black).
- Project licensed under GPL-3.0.

