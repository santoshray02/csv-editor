---
sidebar_position: 2
title: Installation
---

# Installation Guide

Get CSV Editor up and running in just 2 minutes! This guide covers all installation methods and client configurations.

## Prerequisites

- **Python 3.8+** (3.11+ recommended for best performance)
- **Operating System**: Windows, macOS, or Linux
- **Package Manager**: uv (recommended), pip, or conda

## Quick Install (Recommended)

### Using uv (Fastest)

[uv](https://github.com/astral-sh/uv) is an ultra-fast Python package manager that makes installation simple:

```bash
# Install uv (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Clone and install CSV Editor
git clone https://github.com/santoshray02/csv-editor.git
cd csv-editor
uv sync

# Run the server
uv run csv-editor
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/santoshray02/csv-editor.git
cd csv-editor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the server
python -m csv_editor.server
```

## Client Configuration

### Claude Desktop

Configure Claude Desktop to use CSV Editor as an MCP server.

#### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/path/to/csv-editor",
      "env": {
        "CSV_MAX_FILE_SIZE": "1073741824",
        "CSV_SESSION_TIMEOUT": "3600"
      }
    }
  }
}
```

#### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "C:\\path\\to\\csv-editor",
      "env": {
        "CSV_MAX_FILE_SIZE": "1073741824",
        "CSV_SESSION_TIMEOUT": "3600"
      }
    }
  }
}
```

#### Linux
Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/home/user/csv-editor",
      "env": {
        "CSV_MAX_FILE_SIZE": "1073741824",
        "CSV_SESSION_TIMEOUT": "3600"
      }
    }
  }
}
```

### VS Code Extensions

#### Continue
Edit `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/path/to/csv-editor"
    }
  }
}
```

#### Cline
Add to VS Code settings (`settings.json`):

```json
{
  "cline.mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/path/to/csv-editor"
    }
  }
}
```

### Other Clients

For detailed configuration of other clients (Windsurf, Zed, etc.), see [MCP_CONFIG.md](https://github.com/santoshray02/csv-editor/blob/main/MCP_CONFIG.md).

## Advanced Installation

### Install with All Features

```bash
# With uv
uv sync --all-extras

# With pip
pip install -e ".[all]"
```

### Install for Development

```bash
# With uv
uv sync --all-extras
uv run pre-commit install

# With pip
pip install -e ".[dev]"
pre-commit install
```

### Global Installation with pipx

```bash
pipx install git+https://github.com/santoshray02/csv-editor.git
```

## Environment Variables

Configure CSV Editor behavior with these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CSV_MAX_FILE_SIZE` | 1GB | Maximum file size in bytes |
| `CSV_SESSION_TIMEOUT` | 3600 | Session timeout in seconds |
| `CSV_CHUNK_SIZE` | 10000 | Rows per processing chunk |
| `CSV_AUTO_SAVE` | true | Enable auto-save by default |
| `CSV_LOG_LEVEL` | INFO | Logging level |

## Verification

### Test the Installation

```bash
# Check if server starts
uv run csv-editor --help

# Run with verbose output
CSV_LOG_LEVEL=DEBUG uv run csv-editor
```

### Test with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector uv tool run csv-editor
```

### Verify in Your Client

1. **Claude Desktop**: Look for "csv-editor" in the MCP servers list
2. **VS Code**: Check the extension's MCP panel
3. **Command Line**: Run a test command

## Troubleshooting

### Common Issues

#### Server not starting
- Check Python version: `python --version` (must be 3.8+)
- Verify installation: `uv run csv-editor --version`
- Check logs: `CSV_LOG_LEVEL=DEBUG uv run csv-editor`

#### Client can't connect
- Verify the path in your configuration is correct
- Ensure the server is running
- Check firewall settings for local connections

#### Permission errors
- On macOS/Linux: Check file permissions
- On Windows: Run as administrator if needed

### Getting Help

- [GitHub Issues](https://github.com/santoshray02/csv-editor/issues)
- [GitHub Discussions](https://github.com/santoshray02/csv-editor/discussions)
- [Documentation](https://csv-editor-docs.vercel.app)

## Next Steps

Now that CSV Editor is installed, continue to:
- [Quick Start Tutorial](./tutorials/quickstart) - Learn the basics
- [API Reference](./api/overview) - Explore all available tools
- [Examples](./examples) - See real-world use cases