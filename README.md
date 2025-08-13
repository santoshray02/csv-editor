# CSV Editor MCP Server

A powerful FastMCP server providing comprehensive CSV manipulation, analysis, and validation tools through the Model Context Protocol.

## Features

### 🚀 Core Capabilities
- **Session Management**: Multi-user support with isolated sessions and automatic cleanup
- **Auto-Save**: Automatic and configurable data persistence with multiple save strategies
- **History & Undo/Redo**: Complete operation history with persistent storage and time-travel capabilities
- **Multiple Data Sources**: Load CSV from files, URLs, or string content
- **Export Formats**: CSV, TSV, JSON, Excel, Parquet, HTML, Markdown
- **High Performance**: Efficient pandas-based operations with chunked processing for large files

### 📊 Data Manipulation
- **Filtering**: Complex condition-based filtering with AND/OR logic
- **Sorting**: Multi-column sorting with custom order
- **Column Operations**: Select, rename, add, remove, update columns
- **Type Conversion**: Smart data type changes with error handling
- **Data Cleaning**: Handle missing values, remove duplicates

### 📈 Analytics & Insights
- **Statistical Analysis**: Comprehensive statistics with percentiles, skewness, kurtosis
- **Correlation Analysis**: Pearson, Spearman, and Kendall correlation matrices
- **Aggregations**: Group-by operations with multiple aggregation functions
- **Outlier Detection**: IQR and Z-score based outlier identification
- **Data Profiling**: Complete data profile with quality metrics

### ✅ Data Validation
- **Schema Validation**: Validate against custom schema definitions
- **Quality Checks**: Automated data quality scoring with recommendations
- **Anomaly Detection**: Multi-method anomaly detection (statistical, pattern, missing data)

## Installation

### Prerequisites
- Python 3.8+ (3.11+ recommended)
- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package manager (recommended)
- Or pip/conda as alternatives

### Quick Start

For detailed MCP client configuration, see [MCP_CONFIG.md](MCP_CONFIG.md).

### Install with uv (Recommended - Fastest)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or with pip: pip install uv

# Clone the repository
git clone https://github.com/santoshray02/csv-editor.git
cd csv-editor

# Create virtual environment and install dependencies (one command!)
uv sync

# Or install with all optional dependencies
uv sync --all-extras

# Run the server
uv run csv-mcp-server
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/santoshray02/csv-editor.git
cd csv-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Or with all extras
pip install -e ".[all]"
```

### Install from PyPI (coming soon)

```bash
# With uv (fastest)
uv pip install csv-editor

# With pip
pip install csv-editor
```

## Quick Start

### 1. Start the Server

```bash
# With uv (recommended)
uv run server  # Uses alias from uv.toml

# Or directly
uv run python -m csv_editor.server

# Run with HTTP transport
uv run csv-mcp-server --transport http --port 8000

# Run with SSE transport for real-time updates
uv run csv-mcp-server --transport sse --port 8000

# Without uv
python -m csv_editor.server
```

### 2. Configure Your MCP Client

See [MCP_CONFIG.md](MCP_CONFIG.md) for detailed configuration instructions for:
- Claude Desktop (macOS, Windows, Linux)
- Continue (VS Code extension)
- Cline
- Windsurf
- Zed Editor
- Generic MCP clients

#### Quick Example - Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "python",
      "args": ["-m", "src.csv_editor.server"],
      "env": {
        "CSV_MAX_FILE_SIZE": "1073741824",
        "CSV_SESSION_TIMEOUT": "3600",
        "CSV_CHUNK_SIZE": "10000"
      }
    }
  }
}
```

### 3. Basic Usage Example

```python
# Load a CSV file
session = await load_csv(
    file_path="/path/to/data.csv",
    encoding="utf-8",
    delimiter=","
)

# Get statistics
stats = await get_statistics(
    session_id=session["session_id"],
    columns=["sales", "quantity"]
)

# Filter data
filtered = await filter_rows(
    session_id=session["session_id"],
    conditions=[
        {"column": "sales", "operator": ">", "value": 1000},
        {"column": "region", "operator": "in", "value": ["North", "South"]}
    ],
    mode="and"
)

# Export results
await export_csv(
    session_id=session["session_id"],
    file_path="/path/to/output.json",
    format="json"
)
```

## History & Undo/Redo

The CSV Editor maintains a complete history of all operations with the ability to undo, redo, and restore to any previous state.

### History Features
- **Persistent Storage**: History survives session restarts (JSON or Pickle format)
- **Undo/Redo**: Step backward and forward through operations
- **Time Travel**: Jump to any specific operation in history
- **Snapshots**: Automatic data snapshots for quick restoration
- **Export History**: Save operation history for audit or analysis

### History Example

```python
# Load CSV with history enabled
session = await load_csv("/path/to/data.csv")

# Perform operations (automatically tracked)
await filter_rows(session_id, conditions=[...])
await update_column(session_id, column="price", operation="multiply", value=1.1)
await add_column(session_id, name="discount", value=0.2)

# Undo last operation
await undo(session_id)  # Removes discount column

# Redo the operation
await redo(session_id)  # Re-adds discount column

# View history
history = await get_history(session_id, limit=10)

# Restore to specific operation
await restore_to_operation(session_id, operation_id="...")

# Export history for audit
await export_history(session_id, "/path/to/history.json")
```

## Auto-Save Feature

The CSV Editor includes a powerful auto-save feature that automatically preserves your work. **Auto-save is enabled by default** and saves your data after each operation.

### Default Configuration
- **Enabled**: Yes (automatic saving is ON by default)
- **Mode**: After Operation (saves after each modification)
- **Strategy**: Overwrite (updates the original file)

### Auto-Save Modes
- **After Operation**: Save after each data modification (DEFAULT)
- **Periodic**: Save at regular intervals
- **Hybrid**: Combine after-operation and periodic saving
- **Disabled**: Turn off automatic saving

### Save Strategies
- **Overwrite**: Replace the original file (DEFAULT)
- **Backup**: Create timestamped backup files
- **Versioned**: Maintain numbered versions (v0001, v0002, etc.)
- **Custom**: Save to a specified path

### Modifying Auto-Save Configuration

Since auto-save is enabled by default with overwrite strategy, you might want to change it:

```python
# Change to backup strategy instead of overwriting
await configure_auto_save(
    session_id=session["session_id"],
    strategy="backup",  # Create backups instead of overwriting
    backup_dir="/path/to/backups",
    max_backups=10  # Keep last 10 backups
)

# Or use periodic saving
await configure_auto_save(
    session_id=session["session_id"],
    mode="periodic",  # Save every N seconds instead of after each operation
    interval_seconds=300  # Save every 5 minutes
)

# Or disable auto-save if not needed
await disable_auto_save(session_id)

# Check current auto-save configuration
status = await get_auto_save_status(session_id)
```

## Available Tools

### Data I/O Operations

| Tool | Description |
|------|-------------|
| `load_csv` | Load CSV file from local filesystem |
| `load_csv_from_url` | Load CSV from HTTP/HTTPS URL |
| `load_csv_from_content` | Load CSV from string content |
| `export_csv` | Export to various formats (CSV, JSON, Excel, etc.) |
| `get_session_info` | Get current session information |
| `list_sessions` | List all active sessions |
| `close_session` | Close and cleanup session |

### Auto-Save Operations

| Tool | Description |
|------|-------------|
| `configure_auto_save` | Configure auto-save settings for a session |
| `disable_auto_save` | Disable auto-save for a session |
| `get_auto_save_status` | Get current auto-save status |
| `trigger_manual_save` | Manually trigger a save |

### History Operations

| Tool | Description |
|------|-------------|
| `undo` | Undo the last operation |
| `redo` | Redo a previously undone operation |
| `get_history` | Get operation history with statistics |
| `restore_to_operation` | Restore to a specific operation point |
| `clear_history` | Clear all operation history |
| `export_history` | Export history to JSON or CSV file |

### Data Manipulation

| Tool | Description |
|------|-------------|
| `filter_rows` | Filter with complex conditions |
| `sort_data` | Sort by multiple columns |
| `select_columns` | Select specific columns |
| `rename_columns` | Rename columns |
| `add_column` | Add new column with values or formula |
| `remove_columns` | Remove columns |
| `update_column` | Update column values with operations (replace, extract, split, etc.) |
| `change_column_type` | Convert column data types |
| `fill_missing_values` | Handle missing data |
| `remove_duplicates` | Remove duplicate rows |

### Data Analysis

| Tool | Description |
|------|-------------|
| `get_statistics` | Statistical summary |
| `get_column_statistics` | Detailed column stats |
| `get_correlation_matrix` | Correlation analysis |
| `group_by_aggregate` | Group and aggregate |
| `get_value_counts` | Frequency counts |
| `detect_outliers` | Find outliers |
| `profile_data` | Comprehensive profiling |

### Data Validation

| Tool | Description |
|------|-------------|
| `validate_schema` | Validate against schema |
| `check_data_quality` | Quality assessment |
| `find_anomalies` | Detect anomalies |

## Advanced Features

### Filter Operators

The `filter_rows` tool supports various operators:
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- String: `contains`, `starts_with`, `ends_with`
- Membership: `in`, `not_in`
- Null checks: `is_null`, `not_null`

### Missing Value Strategies

The `fill_missing_values` tool supports:
- `drop` - Remove rows with missing values
- `fill` - Fill with specific value
- `forward` - Forward fill
- `backward` - Backward fill
- `mean` - Fill with column mean
- `median` - Fill with column median
- `mode` - Fill with most frequent value

### Export Formats

- **CSV/TSV**: Standard delimited formats
- **JSON**: JSON array or records format
- **Excel**: .xlsx format with formatting
- **Parquet**: Efficient columnar storage
- **HTML**: Formatted HTML table
- **Markdown**: Markdown table format

## Resources

The server provides MCP resources accessible via URIs:

- `csv://{session_id}/data` - Get session data
- `csv://{session_id}/schema` - Get data schema
- `sessions://active` - List active sessions

## Prompts

Pre-defined prompts for common tasks:

- `analyze_csv_prompt` - Generate analysis prompt
- `data_cleaning_prompt` - Generate cleaning suggestions

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CSV_MAX_FILE_SIZE` | Maximum file size in bytes | 1GB |
| `CSV_SESSION_TIMEOUT` | Session timeout in seconds | 3600 |
| `CSV_CHUNK_SIZE` | Rows per chunk for large files | 10000 |
| `LOG_LEVEL` | Logging level | INFO |

### Performance Tuning

For large datasets:
```bash
export CSV_CHUNK_SIZE=50000  # Larger chunks
export CSV_MAX_FILE_SIZE=5368709120  # 5GB limit
```

## Development

### Project Structure

```
csv-mcp-server/
├── src/
│   └── csv_editor/
│       ├── server.py          # Main server
│       ├── models/            # Data models
│       ├── tools/             # Tool implementations
│       ├── resources/         # Resource definitions
│       ├── prompts/           # Prompt templates
│       └── utils/             # Utilities
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── pyproject.toml             # Project configuration
├── uv.lock                    # Dependency lock file
└── README.md                  # Documentation
```

### Running Tests

```bash
# With uv (fastest - no separate install needed!)
uv run test
uv run test-cov  # With coverage

# Run all quality checks
uv run all-checks  # Runs formatting, linting, type checking, and tests

# Individual commands
uv run fmt        # Format code with Black
uv run lint       # Lint with Ruff
uv run type-check # Type check with MyPy

# Without uv
pip install -e ".[test]"
pytest
pytest --cov=src/csv_editor --cov-report=html
```

### Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## Examples

### Data Cleaning Pipeline

```python
# Load data
session = await load_csv(file_path="sales_data.csv")
sid = session["session_id"]

# Remove duplicates
await remove_duplicates(session_id=sid)

# Fill missing values
await fill_missing_values(
    session_id=sid,
    strategy="mean",
    columns=["price", "quantity"]
)

# Convert types
await change_column_type(
    session_id=sid,
    column="date",
    dtype="datetime"
)

# Validate quality
quality = await check_data_quality(session_id=sid)
print(f"Data quality score: {quality['quality_results']['overall_score']}")
```

### Statistical Analysis

```python
# Get correlations
corr = await get_correlation_matrix(
    session_id=sid,
    method="pearson",
    min_correlation=0.5
)

# Detect outliers
outliers = await detect_outliers(
    session_id=sid,
    method="iqr",
    threshold=1.5
)

# Profile data
profile = await profile_data(
    session_id=sid,
    include_correlations=True,
    include_outliers=True
)
```

## Roadmap

- [ ] SQL query interface for complex operations
- [ ] Streaming support for very large files
- [ ] Machine learning data preparation tools
- [ ] Advanced visualization exports
- [ ] Data versioning and rollback
- [ ] Collaborative editing features
- [ ] REST API wrapper for non-MCP clients

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/santoshray02/csv-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/santoshray02/csv-mcp-server/discussions)
- **Documentation**: [Wiki](https://github.com/santoshray02/csv-mcp-server/wiki)

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast Model Context Protocol implementation
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [NumPy](https://numpy.org/) - Numerical computing

## Citation

If you use this tool in your research or project, please cite:

```bibtex
@software{csv_mcp_server,
  title = {CSV Editor MCP Server},
  author = {Santosh Ray},
  year = {2024},
  url = {https://github.com/santoshray02/csv-mcp-server}
}
```