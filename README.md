# CSV Editor - AI-Powered CSV Processing via MCP

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![FastMCP](https://img.shields.io/badge/Built%20with-FastMCP-purple)](https://github.com/jlowin/fastmcp)
[![Pandas](https://img.shields.io/badge/Powered%20by-Pandas-150458)](https://pandas.pydata.org/)
[![smithery badge](https://smithery.ai/badge/@santoshray02/csv-editor)](https://smithery.ai/server/@santoshray02/csv-editor)

**Transform how AI assistants work with CSV data.** CSV Editor is a high-performance MCP server that gives Claude, ChatGPT, and other AI assistants powerful data manipulation capabilities through simple commands.

<a href="https://glama.ai/mcp/servers/@santoshray02/csv-editor">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@santoshray02/csv-editor/badge" alt="CSV Editor MCP server" />
</a>

## 🎯 Why CSV Editor?

### The Problem
AI assistants struggle with complex data operations - they can read files but lack tools for filtering, transforming, analyzing, and validating CSV data efficiently.

### The Solution  
CSV Editor bridges this gap by providing AI assistants with 40+ specialized tools for CSV operations, turning them into powerful data analysts that can:
- Clean messy datasets in seconds
- Perform complex statistical analysis
- Validate data quality automatically
- Transform data with natural language commands
- Track all changes with undo/redo capabilities

### Key Differentiators
| Feature | CSV Editor | Traditional Tools |
|---------|-----------|------------------|
| **AI Integration** | Native MCP protocol | Manual operations |
| **Auto-Save** | Automatic with strategies | Manual save required |
| **History Tracking** | Full undo/redo with snapshots | Limited or none |
| **Session Management** | Multi-user isolated sessions | Single user |
| **Data Validation** | Built-in quality scoring | Separate tools needed |
| **Performance** | Handles GB+ files with chunking | Memory limitations |

## ⚡ Quick Demo

```python
# Your AI assistant can now do this:
"Load the sales data and remove duplicates"
"Filter for Q4 2024 transactions over $10,000"  
"Calculate correlation between price and quantity"
"Fill missing values with the median"
"Export as Excel with the analysis"

# All with automatic history tracking and undo capability!
```

## 🚀 Quick Start (2 minutes)

### Installing via Smithery

To install csv-editor for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@santoshray02/csv-editor):

```bash
npx -y @smithery/cli install @santoshray02/csv-editor --client claude
```

### Fastest Installation (Recommended)

```bash
# Install uv if needed (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and run
git clone https://github.com/santoshray02/csv-editor.git
cd csv-editor
uv sync
uv run csv-editor
```

### Configure Your AI Assistant

<details>
<summary><b>Claude Desktop</b> (Click to expand)</summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "csv-editor": {
      "command": "uv",
      "args": ["tool", "run", "csv-editor"],
      "env": {
        "CSV_MAX_FILE_SIZE": "1073741824"
      }
    }
  }
}
```
</details>

<details>
<summary><b>Other Clients</b> (Continue, Cline, Windsurf, Zed)</summary>

See [MCP_CONFIG.md](MCP_CONFIG.md) for detailed configuration.

</details>

## 💡 Real-World Use Cases

### 📊 Data Analyst Workflow
```python
# Morning: Load yesterday's data
session = load_csv("daily_sales.csv")

# Clean: Remove duplicates and fix types
remove_duplicates(session_id)
change_column_type("date", "datetime")
fill_missing_values(strategy="median", columns=["revenue"])

# Analyze: Get insights
get_statistics(columns=["revenue", "quantity"])
detect_outliers(method="iqr", threshold=1.5)
get_correlation_matrix(min_correlation=0.5)

# Report: Export cleaned data
export_csv(format="excel", file_path="clean_sales.xlsx")
```

### 🏭 ETL Pipeline
```python
# Extract from multiple sources
load_csv_from_url("https://api.example.com/data.csv")

# Transform with complex operations
filter_rows(conditions=[
    {"column": "status", "operator": "==", "value": "active"},
    {"column": "amount", "operator": ">", "value": 1000}
])
add_column(name="quarter", formula="Q{(month-1)//3 + 1}")
group_by_aggregate(group_by=["quarter"], aggregations={
    "amount": ["sum", "mean"],
    "customer_id": "count"
})

# Load to different formats
export_csv(format="parquet")  # For data warehouse
export_csv(format="json")     # For API
```

### 🔍 Data Quality Assurance
```python
# Validate incoming data
validate_schema(schema={
    "customer_id": {"type": "integer", "required": True},
    "email": {"type": "string", "pattern": r"^[^@]+@[^@]+\.[^@]+$"},
    "age": {"type": "integer", "min": 0, "max": 120}
})

# Quality scoring
quality_report = check_data_quality()
# Returns: overall_score, missing_data%, duplicates, outliers

# Anomaly detection
anomalies = find_anomalies(methods=["statistical", "pattern"])
```

## 🎨 Core Features

### Data Operations
- **Load & Export**: CSV, JSON, Excel, Parquet, HTML, Markdown
- **Transform**: Filter, sort, group, pivot, join
- **Clean**: Remove duplicates, handle missing values, fix types
- **Calculate**: Add computed columns, aggregations

### Analysis Tools  
- **Statistics**: Descriptive stats, correlations, distributions
- **Outliers**: IQR, Z-score, custom thresholds
- **Profiling**: Complete data quality reports
- **Validation**: Schema checking, quality scoring

### Productivity Features
- **Auto-Save**: Never lose work with configurable strategies
- **History**: Full undo/redo with operation tracking
- **Sessions**: Multi-user support with isolation
- **Performance**: Stream processing for large files

### Advanced Compatibility
- **Null Value Support**: Full support for JSON `null` → Python `None` → pandas `NaN`
- **Claude Code Compatible**: Handles JSON string serialization automatically
- **Type Safety**: Improved type annotations with `CellValue`, `RowData`, `FilterCondition`
- **Modular Architecture**: Organized tool modules for better maintainability

## 📚 Available Tools

<details>
<summary><b>Complete Tool List</b> (40+ tools)</summary>

### I/O Operations
- `load_csv` - Load from file
- `load_csv_from_url` - Load from URL
- `load_csv_from_content` - Load from string
- `export_csv` - Export to various formats
- `get_session_info` - Session details
- `list_sessions` - Active sessions
- `close_session` - Cleanup

### Data Manipulation
- `filter_rows` - Complex filtering
- `sort_data` - Multi-column sort
- `select_columns` - Column selection
- `rename_columns` - Rename columns
- `add_column` - Add computed columns
- `remove_columns` - Remove columns
- `update_column` - Update values
- `change_column_type` - Type conversion
- `fill_missing_values` - Handle nulls
- `remove_duplicates` - Deduplicate

### Analysis
- `get_statistics` - Statistical summary
- `get_column_statistics` - Column stats
- `get_correlation_matrix` - Correlations
- `group_by_aggregate` - Group operations
- `get_value_counts` - Frequency counts
- `detect_outliers` - Find outliers
- `profile_data` - Data profiling

### Validation
- `validate_schema` - Schema validation
- `check_data_quality` - Quality metrics
- `find_anomalies` - Anomaly detection

### Auto-Save & History
- `configure_auto_save` - Setup auto-save
- `get_auto_save_status` - Check status
- `undo` / `redo` - Navigate history
- `get_history` - View operations
- `restore_to_operation` - Time travel

</details>

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CSV_MAX_FILE_SIZE` | 1GB | Maximum file size |
| `CSV_SESSION_TIMEOUT` | 3600s | Session timeout |
| `CSV_CHUNK_SIZE` | 10000 | Processing chunk size |
| `CSV_AUTO_SAVE` | true | Enable auto-save |

### Auto-Save Strategies

CSV Editor automatically saves your work with configurable strategies:

- **Overwrite** (default) - Update original file
- **Backup** - Create timestamped backups
- **Versioned** - Maintain version history
- **Custom** - Save to specified location

```python
# Configure auto-save
configure_auto_save(
    strategy="backup",
    backup_dir="/backups",
    max_backups=10
)
```

## 🛠️ Advanced Installation Options

<details>
<summary><b>Alternative Installation Methods</b></summary>

### Using pip
```bash
git clone https://github.com/santoshray02/csv-editor.git
cd csv-editor
pip install -e .
```

### Using pipx (Global)
```bash
pipx install git+https://github.com/santoshray02/csv-editor.git
```

### From GitHub (Recommended)
```bash
# Install latest version
pip install git+https://github.com/santoshray02/csv-editor.git

# Or using uv
uv pip install git+https://github.com/santoshray02/csv-editor.git

# Install specific version
pip install git+https://github.com/santoshray02/csv-editor.git@v1.0.1
```

</details>

## 🧪 Development

### Running Tests
```bash
uv run test           # Run tests
uv run test-cov       # With coverage
uv run all-checks     # Format, lint, type-check, test
```

### Project Structure
```
csv-editor/
├── src/csv_editor/   # Core implementation
│   ├── tools/        # MCP tool implementations
│   ├── models/       # Data models
│   └── server.py     # MCP server
├── tests/            # Test suite
├── examples/         # Usage examples
└── docs/            # Documentation
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run `uv run all-checks`
5. Submit a pull request

## 📈 Roadmap

- [ ] SQL query interface
- [ ] Real-time collaboration
- [ ] Advanced visualizations
- [ ] Machine learning integrations
- [ ] Cloud storage support
- [ ] Performance optimizations for 10GB+ files

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/santoshray02/csv-editor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/santoshray02/csv-editor/discussions)
- **Documentation**: [Wiki](https://github.com/santoshray02/csv-editor/wiki)

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

## 💎 Advanced Features

### Null Value Handling
Full support for null values across all operations:

```python
# Insert rows with null values
insert_row(session_id, -1, {
    "name": "John Doe", 
    "email": null,           # JSON null becomes Python None
    "phone": null,
    "notes": "Contact pending"
})

# Update cells to null
set_cell_value(session_id, 0, "email", null)

# Filter for null values  
filter_rows(session_id, [{"column": "email", "operator": "is_null"}])
```

### Claude Code Compatibility
Automatically handles Claude Code's JSON string serialization:

```javascript
// Claude Code sends this:
{
  "data": "{\"Company\": \"Acme\", \"Contact\": null, \"Status\": \"Active\"}"
}

// CSV Editor automatically parses it to:
{
  "data": {"Company": "Acme", "Contact": null, "Status": "Active"}
}
```

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast Model Context Protocol
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [NumPy](https://numpy.org/) - Numerical computing

---

**Ready to supercharge your AI's data capabilities?** [Get started in 2 minutes →](#-quick-start-2-minutes)