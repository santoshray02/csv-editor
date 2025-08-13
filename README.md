# CSV Editor MCP Server

A powerful FastMCP server providing comprehensive CSV manipulation, analysis, and validation tools through the Model Context Protocol.

## Features

### 🚀 Core Capabilities
- **Session Management**: Multi-user support with isolated sessions and automatic cleanup
- **Multiple Data Sources**: Load CSV from files, URLs, or string content
- **Export Formats**: CSV, TSV, JSON, Excel, Parquet, HTML, Markdown
- **High Performance**: Efficient pandas-based operations with chunked processing for large files

### 📊 Data Manipulation
- **Filtering**: Complex condition-based filtering with AND/OR logic
- **Sorting**: Multi-column sorting with custom order
- **Column Operations**: Select, rename, add, remove columns
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

### 2. Configure with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Data Manipulation

| Tool | Description |
|------|-------------|
| `filter_rows` | Filter with complex conditions |
| `sort_data` | Sort by multiple columns |
| `select_columns` | Select specific columns |
| `rename_columns` | Rename columns |
| `add_column` | Add new column with values or formula |
| `remove_columns` | Remove columns |
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