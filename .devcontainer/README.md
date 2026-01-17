# Dev Container Configuration

This directory contains the configuration for developing this repository using:

- **GitHub Codespaces**: Cloud-based development environment
- **VS Code Dev Containers**: Local containerized development environment

## Quick Start

### GitHub Codespaces

1. Click the **Code** button on the repository
1. Select **Codespaces** tab
1. Click **Create codespace on main**
1. Wait for the environment to build (first time takes ~3-5 minutes)
1. Start coding!

### VS Code Dev Containers (Local)

**Prerequisites:**

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

**Steps:**

1. Open this repository in VS Code
1. Press `F1` and select **Dev Containers: Reopen in Container**
1. Wait for the container to build (first time takes ~3-5 minutes)
1. Start coding!

## What's Included

### Base Image

- Python 3.12 (Debian Bookworm)
- Git
- GitHub CLI
- Node.js LTS
- Zsh with Oh My Zsh

### Pre-installed Tools

- **pre-commit**: Git hooks for code quality
- **Python formatters/linters**: black, ruff, isort, pyupgrade
- **Markdown tools**: mdformat
- **YAML tools**: yamlfmt
- **TOML tools**: toml-sort
- **Shell tools**: shellcheck, shfmt

### VS Code Extensions

- GitHub Copilot & Chat
- GitHub Pull Requests
- Markdown support (linting, preview, Mermaid)
- Python support (Pylance, Ruff)
- EditorConfig
- YAML, TOML support
- Shell script support

## Post-Create Setup

The `post-create.sh` script automatically:

1. Upgrades pip
1. Installs pre-commit and its hooks
1. Installs all development tools
1. Configures git
1. Sets up helpful git aliases

## Customization

To customize your dev container:

1. Edit `.devcontainer/devcontainer.json` to:
   - Add VS Code extensions
   - Modify settings
   - Add additional features
1. Edit `.devcontainer/post-create.sh` to:
   - Install additional tools
   - Configure environment variables
   - Run custom setup scripts

## Troubleshooting

### Container won't start

- Ensure Docker Desktop is running
- Try rebuilding: `F1` → **Dev Containers: Rebuild Container**

### Pre-commit hooks fail

- Run `pre-commit run --all-files` to see detailed errors
- Run `pre-commit autoupdate` to update hook versions

### Permission issues

- The container runs as the `vscode` user
- Git config is mounted from your host system

## Resources

- [Dev Containers documentation](https://containers.dev/)
- [GitHub Codespaces documentation](https://docs.github.com/en/codespaces)
- [VS Code Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
