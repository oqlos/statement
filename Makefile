# Makefile for sumd
# Provides convenient commands for development, testing, and deployment

.PHONY: help install install-dev test clean publish publish-confirm publish-test version

# Default target
help:
	@echo "🚀 SUMD Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install sumd in development mode"
	@echo "  install-dev      Install sumd with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test             Run tests"
	@echo "  lint             Run linting"
	@echo "  format           Format code"
	@echo "  clean            Clean temporary files"
	@echo ""
	@echo "Release:"
	@echo "  publish          Build package for PyPI (dry-run)"
	@echo "  publish-confirm  Upload to PyPI"
	@echo "  publish-test     Upload to TestPyPI"
	@echo "  version          Show current version"
	@echo ""

# Installation
install:
	@echo "📦 Installing sumd..."
	@if command -v uv > /dev/null 2>&1; then \
		uv pip install -e .; \
	else \
		pip install -e .; \
	fi
	@echo "✅ Installation completed!"

install-dev:
	@echo "📦 Installing sumd with dev dependencies..."
	@if command -v uv > /dev/null 2>&1; then \
		uv pip install -e ".[dev]"; \
	else \
		pip install -e ".[dev]"; \
	fi
	@echo "✅ Dev installation completed!"

# Testing
test:
	@echo "🧪 Running tests..."
	.venv/bin/python -m pytest tests/ -v --tb=short

test-cov:
	@echo "🧪 Running tests with coverage..."
	.venv/bin/python -m pytest tests/ -v --cov=sumd --cov-report=term-missing --cov-report=json

# Code quality
lint:
	@echo "🔍 Running linting with ruff..."
	.venv/bin/python -m ruff check sumd/
	.venv/bin/python -m ruff check tests/

format:
	@echo "📝 Formatting code with ruff..."
	.venv/bin/python -m ruff format sumd/
	.venv/bin/python -m ruff format tests/

# Utilities
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ coverage.json
	@echo "✅ Clean completed!"

# Release helpers
publish:
	@echo "📦 Publishing to PyPI..."
	@command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build)
	rm -rf dist/ build/ *.egg-info/
	.venv/bin/python -m build
	.venv/bin/twine check dist/*
	@echo "⚡ Ready to upload. Run: make publish-confirm to upload to PyPI"

publish-confirm:
	@echo "🚀 Uploading to PyPI..."
	.venv/bin/twine upload dist/*

publish-test:
	@echo "📦 Publishing to TestPyPI..."
	@command -v .venv/bin/twine > /dev/null 2>&1 || (.venv/bin/pip install --upgrade twine build)
	rm -rf dist/ build/ *.egg-info/
	.venv/bin/python -m build
	.venv/bin/twine upload --repository testpypi dist/*

version:
	@echo "📦 Version information..."
	@cat VERSION
	@.venv/bin/python -c "from importlib.metadata import version; print(f'Installed version: {version(\"sumd\")}')"
