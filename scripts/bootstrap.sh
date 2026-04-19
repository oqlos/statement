#!/bin/bash
# Bootstrap script — ensures venv exists and all deps installed

set -e

VENV_DIR="${PWD}/.venv"
PYTHON="${VENV_DIR}/bin/python"
PIP="${VENV_DIR}/bin/pip"

echo "🔧 Bootstrapping sumd development environment..."

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Verify venv works
if [ ! -f "$PYTHON" ]; then
    echo "❌ Failed to create venv"
    exit 1
fi

echo "✅ venv OK: $PYTHON"

# Upgrade pip
"$PIP" install --upgrade pip

# Install project in editable mode with dev dependencies
echo "📥 Installing dependencies..."
"$PIP" install -e ".[dev]"

# Verify critical tools are available
echo "🔍 Verifying tools..."

for tool in pytest ruff pyqual; do
    if ! "$PYTHON" -m "$tool" --version &>/dev/null; then
        echo "❌ $tool not available"
        exit 1
    fi
    echo "✅ $tool OK"
done

# Verify Taskfile tasks work
echo "🔍 Verifying Taskfile tasks..."
if ! task --dry &>/dev/null; then
    echo "❌ Taskfile syntax error"
    exit 1
fi
echo "✅ Taskfile OK"

# Test SUMD generation
if ! "$PYTHON" -m sumd.cli scan . --dry-run &>/dev/null; then
    echo "❌ SUMD generation failed"
    exit 1
fi
echo "✅ SUMD generation OK"

# Create .env if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
fi

echo ""
echo "🎉 Bootstrap complete!"
echo "   Run: task quality   # Run quality pipeline"
echo "   Run: task sumd      # Generate SUMD.md"
echo "   Run: task check     # Full pre-commit check"
