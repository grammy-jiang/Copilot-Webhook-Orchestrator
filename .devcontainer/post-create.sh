#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install pre-commit
echo "🔨 Installing pre-commit..."
pip install pre-commit

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install --install-hooks

# Install additional Python development tools
echo "🐍 Installing Python development tools..."
pip install \
  black \
  ruff \
  isort \
  pyupgrade \
  mdformat \
  yamlfmt \
  toml-sort

# Configure git to trust the repository
echo "🔐 Configuring git..."
git config --global --add safe.directory /workspaces/agentic-dev-template

# Install shellcheck if not present
if ! command -v shellcheck &>/dev/null; then
  echo "📝 Installing shellcheck..."
  sudo apt-get update && sudo apt-get install -y shellcheck
fi

# Install shfmt
echo "📝 Installing shfmt..."
go install mvdan.cc/sh/v3/cmd/shfmt@latest || echo "⚠️  shfmt installation skipped (Go not available)"

# Set up git aliases for better workflow
echo "🎯 Setting up git aliases..."
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'

# Create a welcome message
echo "✅ Development environment setup complete!"
echo ""
echo "📝 Available tools:"
echo "  - pre-commit: Git hooks for code quality"
echo "  - black, ruff, isort: Python formatters and linters"
echo "  - mdformat: Markdown formatter"
echo "  - yamlfmt: YAML formatter"
echo "  - shellcheck, shfmt: Shell script linting and formatting"
echo "  - GitHub CLI (gh): GitHub command-line tool"
echo ""
echo "🔧 Quick start:"
echo "  - Run 'pre-commit run --all-files' to check all files"
echo "  - Run 'gh auth login' to authenticate with GitHub"
echo ""
echo "Happy coding! 🎉"
