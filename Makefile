# Makefile for Tonika Bus
# Goblin-approved shortcuts for development, testing, and releases

.PHONY: help install install-dev test test-cov test-unit test-integration lint format typecheck check clean docs release-check changelog-sync changelog-preview release-labels update-readme

# Default target - show help
help:
	@echo "🧌 Tonika Bus - Available commands:"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install           Install core package"
	@echo "  make install-dev       Install with dev dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              Run all tests"
	@echo "  make test-cov          Run tests with coverage report"
	@echo "  make test-unit         Run only unit tests (fast)"
	@echo "  make test-integration  Run only integration tests"
	@echo ""
	@echo "✨ Code Quality:"
	@echo "  make lint              Run ruff linter"
	@echo "  make format            Format code with black"
	@echo "  make typecheck         Run mypy type checker"
	@echo "  make check             Run all quality checks"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make docs              Build Sphinx documentation"
	@echo "  make docs-serve        Build and serve docs locally"
	@echo "  make update-readme     Update README.md with stats"
	@echo ""
	@echo "🚀 Release Management:"
	@echo "  make changelog-sync    Sync GitHub draft → CHANGELOG.md"
	@echo "  make changelog-preview View draft releases"
	@echo "  make release-check     Pre-release checklist"
	@echo "  make release-labels    Create GitHub labels"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean             Remove build artifacts"

# ============================================================================
# Installation
# ============================================================================

install:
	@echo "📦 Installing tonika-bus..."
	pip install -e .

install-dev:
	@echo "📦 Installing tonika-bus with dev dependencies..."
	pip install -e ".[all]"

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "🧪 Running all tests..."
	pytest

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=tonika_bus --cov-report=term-missing --cov-report=html --cov-report=xml -v

test-unit:
	@echo "🧪 Running unit tests (fast)..."
	pytest -m unit -v

test-integration:
	@echo "🧪 Running integration tests..."
	pytest -m integration -v

# ============================================================================
# Code Quality
# ============================================================================

lint:
	@echo "✨ Running linter (ruff)..."
	ruff check src/ tests/

format:
	@echo "✨ Formatting code (black)..."
	black src/ tests/

typecheck:
	@echo "✨ Running type checker (mypy)..."
	mypy src/tonika_bus/core/ --ignore-missing-imports

check: lint typecheck test
	@echo "✅ All checks passed!"

# ============================================================================
# Documentation
# ============================================================================

docs:
	@echo "📚 Building Sphinx documentation..."
	cd docs && $(MAKE) html

docs-serve: docs
	@echo "📚 Serving documentation at http://localhost:8000"
	@cd docs/_build/html && python -m http.server 8000

update-readme:
	@echo "📝 Updating README.md with current stats..."
	python update_readme_stats.py

# ============================================================================
# Release Management
# ============================================================================

changelog-sync:
	@echo "📝 Syncing CHANGELOG from GitHub draft release..."
	@python scripts/sync_changelog.py

changelog-preview:
	@echo "📋 Preview of draft releases..."
	@echo "Visit: https://github.com/aa-parky/tonika_bus/releases"
	@echo ""
	@command -v gh >/dev/null 2>&1 && gh release list --limit 5 || echo "💡 Install GitHub CLI for inline preview: brew install gh"

release-check:
	@echo "🔍 Pre-release checklist..."
	@echo ""
	@echo "📊 Current Status:"
	@echo "  Version in pyproject.toml: $(grep '^version =' pyproject.toml | cut -d'\"' -f2)"
	@echo "  Latest git tag: $(git describe --tags --abbrev=0 2>/dev/null || echo 'none')"
	@echo "  Current branch: $(git branch --show-current)"
	@echo ""
	@echo "✅ Pre-release Checklist:"
	@echo "  [ ] All tests pass: make test"
	@echo "  [ ] Linting clean: make lint"
	@echo "  [ ] Type checking: make typecheck"
	@echo "  [ ] Documentation updated"
	@echo "  [ ] README.md updated: make update-readme"
	@echo "  [ ] CHANGELOG.md synced: make changelog-sync"
	@echo "  [ ] Version bumped in pyproject.toml"
	@echo "  [ ] Draft release reviewed on GitHub"
	@echo "  [ ] All PRs properly labeled"
	@echo ""
	@echo "🚀 Ready to release? Run:"
	@echo "   1. git commit -am 'Release vX.Y.Z'"
	@echo "   2. git tag vX.Y.Z"
	@echo "   3. git push && git push --tags"
	@echo "   4. Publish draft release on GitHub"
	@echo "   5. Upload to PyPI (if applicable)"

release-labels:
	@echo "🏷️  Creating GitHub labels for Release Drafter..."
	@command -v gh >/dev/null 2>&1 || (echo "❌ GitHub CLI not installed. Install with: brew install gh" && exit 1)
	@echo "Creating labels..."
	@gh label create bug --color d73a4a --description "Something isn't working" --force
	@gh label create feature --color a2eeef --description "New feature or request" --force
	@gh label create enhancement --color a2eeef --description "Enhancement to existing feature" --force
	@gh label create documentation --color 0075ca --description "Improvements or additions to documentation" --force
	@gh label create test --color d4c5f9 --description "Testing improvements" --force
	@gh label create chore --color fef2c0 --description "Maintenance and chores" --force
	@gh label create ci --color 00ff00 --description "CI/CD related" --force
	@gh label create dependencies --color 0366d6 --description "Dependency updates" --force
	@gh label create security --color ee0701 --description "Security fixes" --force
	@gh label create breaking --color b60205 --description "Breaking change (major version)" --force
	@gh label create major --color b60205 --description "Major version bump" --force
	@gh label create minor --color fbca04 --description "Minor version bump" --force
	@gh label create patch --color c2e0c6 --description "Patch version bump" --force
	@gh label create skip-changelog --color cccccc --description "Skip this PR in the changelog" --force
	@echo "✅ Labels created successfully!"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ htmlcov/ .coverage coverage.xml
	@echo "✅ Cleanup complete!"