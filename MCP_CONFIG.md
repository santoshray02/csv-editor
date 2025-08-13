# MCP Configuration Guide for CSV Editor

This guide provides configuration examples for integrating the CSV Editor MCP server with various AI assistant platforms.

## Table of Contents
- [Claude Desktop](#claude-desktop)
- [Continue (VS Code)](#continue-vs-code)
- [Cline](#cline)
- [Windsurf](#windsurf)
- [Zed Editor](#zed-editor)
- [Generic MCP Client](#generic-mcp-client)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Claude Desktop

### macOS Configuration
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "csv-editor"
      ],
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60",
        "CSV_MAX_SESSIONS": "10"
      }
    }
  }
}
```

### Windows Configuration
Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "csv-editor"
      ],
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60",
        "CSV_MAX_SESSIONS": "10"
      }
    }
  }
}
```

### Linux Configuration
Location: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "csv-editor"
      ],
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60",
        "CSV_MAX_SESSIONS": "10"
      }
    }
  }
}
```

### Using Python Directly (Alternative)
If you prefer using Python directly instead of uv:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "python",
      "args": [
        "-m",
        "csv_editor.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/csv-mcp-server/src",
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60"
      }
    }
  }
}
```

## Continue (VS Code)

### Configuration
Location: `~/.continue/config.json`

```json
{
  "models": [
    {
      "title": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "YOUR_API_KEY"
    }
  ],
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "csv-editor"
      ],
      "cwd": "/path/to/csv-mcp-server",
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60",
        "CSV_MAX_SESSIONS": "10"
      }
    }
  },
  "customCommands": [
    {
      "name": "csv-analyze",
      "prompt": "Use the CSV Editor MCP server to analyze the selected CSV file",
      "description": "Analyze CSV data"
    },
    {
      "name": "csv-clean",
      "prompt": "Use the CSV Editor MCP server to clean and validate the CSV data",
      "description": "Clean CSV data"
    }
  ]
}
```

## Cline

### Configuration
Location: VS Code Settings (`.vscode/settings.json` or global settings)

```json
{
  "cline.mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "csv-editor"
      ],
      "cwd": "/path/to/csv-mcp-server",
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60",
        "CSV_MAX_SESSIONS": "10",
        "CSV_LOG_LEVEL": "INFO"
      }
    }
  },
  "cline.customInstructions": "When working with CSV files, use the csv-editor MCP server for data operations, analysis, and transformations."
}
```

### Alternative: Cline Config File
Location: `~/.cline/config.json`

```json
{
  "mcpServers": [
    {
      "name": "csv-editor",
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/path/to/csv-mcp-server",
      "enabled": true,
      "alwaysAllow": [
        "load_csv",
        "get_statistics",
        "export_csv"
      ],
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60"
      }
    }
  ]
}
```

## Windsurf

### Configuration
Location: `~/.windsurf/config.json` (or in VS Code settings if using Windsurf extension)

```json
{
  "mcp": {
    "servers": [
      {
        "name": "csv-editor",
        "command": "uv",
        "args": ["tool", "run", "csv-editor"],
        "cwd": "/path/to/csv-mcp-server",
        "env": {
          "CSV_MAX_FILE_SIZE": "1024",
          "CSV_SESSION_TIMEOUT": "60",
          "CSV_MAX_SESSIONS": "10"
        },
        "capabilities": {
          "tools": true,
          "resources": true,
          "prompts": true
        }
      }
    ]
  }
}
```

### Alternative: Windsurf VS Code Extension Settings
If using Windsurf as a VS Code extension, add to `.vscode/settings.json`:

```json
{
  "windsurf.mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "cwd": "/path/to/csv-mcp-server",
      "env": {
        "CSV_MAX_FILE_SIZE": "1024",
        "CSV_SESSION_TIMEOUT": "60"
      },
      "autoStart": true,
      "restartOnFailure": true
    }
  },
  "windsurf.enableMcp": true
}
```

## Zed Editor

### Configuration
Location: `~/.config/zed/settings.json`

```json
{
  "assistant": {
    "default_model": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "mcp": {
      "servers": {
        "csv-editor": {
          "command": "uv",
          "args": [
            "tool",
            "run",
            "csv-editor"
          ],
          "cwd": "/path/to/csv-mcp-server",
          "env": {
            "CSV_MAX_FILE_SIZE": "1024",
            "CSV_SESSION_TIMEOUT": "60",
            "CSV_MAX_SESSIONS": "10"
          }
        }
      }
    }
  },
  "language_models": {
    "anthropic": {
      "api_key": "YOUR_API_KEY"
    }
  }
}
```

## Generic MCP Client

### Using FastMCP Client Library

```python
from fastmcp import Client

config = {
    "mcpServers": {
        "csv-editor": {
            "command": "uv",
            "args": ["tool", "run", "csv-editor"],
            "cwd": "/path/to/csv-mcp-server",
            "env": {
                "CSV_MAX_FILE_SIZE": "1024",
                "CSV_SESSION_TIMEOUT": "60"
            }
        }
    }
}

# Initialize client
client = Client(config)

async def use_csv_editor():
    async with client:
        # Load a CSV file
        result = await client.call_tool(
            "csv-editor_load_csv",
            {
                "file_path": "/path/to/data.csv",
                "encoding": "utf-8"
            }
        )
        
        session_id = result["session_id"]
        
        # Get statistics
        stats = await client.call_tool(
            "csv-editor_get_statistics",
            {"session_id": session_id}
        )
        
        print(stats)
```

### Using MCP SDK Directly

```python
import mcp
from mcp.client import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def run_csv_editor():
    server_params = StdioServerParameters(
        command="uv",
        args=["tool", "run", "csv-editor"],
        cwd="/path/to/csv-mcp-server",
        env={
            "CSV_MAX_FILE_SIZE": "1024",
            "CSV_SESSION_TIMEOUT": "60"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Call a tool
            result = await session.call_tool(
                "load_csv",
                arguments={
                    "file_path": "/path/to/data.csv"
                }
            )
            print("Result:", result)
```

## Environment Variables

All configurations support the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CSV_MAX_FILE_SIZE` | `1024` | Maximum file size in MB |
| `CSV_SESSION_TIMEOUT` | `60` | Session timeout in minutes |
| `CSV_MAX_SESSIONS` | `10` | Maximum concurrent sessions |
| `CSV_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CSV_TEMP_DIR` | System temp | Directory for temporary files |
| `CSV_ENABLE_PROFILING` | `false` | Enable performance profiling |
| `CSV_CACHE_SIZE` | `100` | Maximum cache size in MB |

## Installation Methods

### Method 1: Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/santoshray02/csv-mcp-server.git
cd csv-mcp-server
uv pip install -e .
```

### Method 2: Using pip
```bash
# Clone and install
git clone https://github.com/santoshray02/csv-mcp-server.git
cd csv-mcp-server
pip install -e .
```

### Method 3: Using pipx (Global Installation)
```bash
pipx install git+https://github.com/santoshray02/csv-mcp-server.git
```

## Verification

After configuration, verify the server is working:

### 1. Test Direct Execution
```bash
# Using uv
uv tool run csv-editor --help

# Or using Python
python -m csv_editor.server --help
```

### 2. Test with MCP Inspector
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector uv tool run csv-editor
```

### 3. Check in Your Client
- **Claude Desktop**: Look for "csv-editor" in the MCP servers list
- **Continue**: Check the "MCP" tab in the Continue panel
- **Cline**: Verify in the Cline settings or status bar
- **Windsurf**: Check the Windsurf panel or status bar for MCP connection
- **Zed**: Check the assistant panel for available tools

## Troubleshooting

### Common Issues

1. **Server not starting**
   - Check the command path is correct
   - Verify Python/uv is in PATH
   - Check file permissions

2. **Tools not appearing**
   - Restart the client application
   - Check the configuration file syntax
   - Review client application logs

3. **Session timeout issues**
   - Increase `CSV_SESSION_TIMEOUT` value
   - Check system resources

4. **File size limitations**
   - Adjust `CSV_MAX_FILE_SIZE` environment variable
   - Consider chunking large files

### Debug Mode

Enable debug logging by setting:
```json
{
  "env": {
    "CSV_LOG_LEVEL": "DEBUG"
  }
}
```

### Log Locations

- **Claude Desktop**: `~/Library/Logs/Claude/` (macOS), `%APPDATA%\Claude\logs\` (Windows)
- **Continue**: VS Code Output panel → Continue
- **Cline**: VS Code Output panel → Cline
- **Windsurf**: `~/.windsurf/logs/` or VS Code Output panel → Windsurf
- **Zed**: `~/.local/state/zed/logs/` (Linux/macOS)

## Security Considerations

1. **File Access**: The server has access to the file system. Configure appropriate permissions.
2. **Network Access**: URL loading is enabled. Consider firewall rules if needed.
3. **Resource Limits**: Set appropriate limits via environment variables.
4. **Sensitive Data**: Be cautious when processing files containing sensitive information.

## Support

For issues or questions:
- GitHub Issues: https://github.com/santoshray02/csv-mcp-server/issues
- Documentation: https://github.com/santoshray02/csv-mcp-server#readme