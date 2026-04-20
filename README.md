# CSV Editor - AI-Powered CSV Processing via MCP

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![FastMCP](https://img.shields.io/badge/Built%20with-FastMCP-purple)](https://github.com/jlowin/fastmcp)
[![Pandas](https://img.shields.io/badge/Powered%20by-Pandas-150458)](https://pandas.pydata.org/)
[![smithery badge](https://smithery.ai/badge/@santoshray02/csv-editor)](https://smithery.ai/server/@santoshray02/csv-editor)

**Stateful CSV editing for AI assistants.** CSV Editor is an MCP server that gives Claude, ChatGPT, Cursor, Windsurf, and other MCP clients a full suite of CSV operations — with sessions, undo/redo, and auto-save built in. Most data MCPs are analyze-only; this one lets the AI *edit*.

<a href="https://glama.ai/mcp/servers/@santoshray02/csv-editor">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@santoshray02/csv-editor/badge" alt="CSV Editor MCP server" />
</a>

## 🆕 What's new in v2.0.0 (April 2026)

- **FastMCP 3.x** — migrated from FastMCP 2 to 3.2, aligning with MCP spec [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25).
- **Python 3.11+ required** (was 3.10+). Tested against 3.11 / 3.12 / 3.13 / 3.14.
- **`--transport sse` removed.** Use `--transport http` (Streamable HTTP) for remote deployments. SSE was deprecated by FastMCP 3.
- Dependency refresh: pydantic 2.13, pyarrow 23, httpx 0.28.
- New `CSV_EDITOR_CSV_HISTORY_DIR` env var for configuring the history directory.
- First-class CI test matrix on GitHub Actions.

Users who pinned `csv-editor>=1,<2` are unaffected and will continue to receive 1.x patches if needed. See [CHANGELOG.md](CHANGELOG.md) for the full list of breaking changes.

## 🎯 Why CSV Editor?

### The Problem
AI assistants struggle with complex data operations - they can read files but lack tools for filtering, transforming, analyzing, and validating CSV data efficiently.

### The Solution  
CSV Editor bridges this gap by providing AI assistants with 39 specialized tools for CSV operations, turning them into powerful data analysts that can:
- Clean messy datasets in seconds
- Perform complex statistical analysis
- Validate data quality automatically
- Transform data with natural language commands
- Track all changes with undo/redo capabilities

### Key differentiators vs. other CSV / tabular MCPs

| Capability | CSV Editor | DuckDB / Polars MCPs | Most pandas-based MCPs |
|---|---|---|---|
| **Stateful editing** (load → mutate → save) | ✅ | Read-only or single-shot | Partial |
| **Undo / redo with snapshots** | ✅ | ❌ | ❌ |
| **Multi-session isolation** | ✅ | Limited | Limited |
| **Auto-save with strategies** | ✅ (overwrite / backup / versioned / custom) | ❌ | ❌ |
| **Quality scoring & validation** | ✅ | SQL-only | Via separate tools |
| **File-size sweet spot** | <1 GB (pandas) | 50 GB+ (streaming SQL) | Small–medium |
| **Best for** | Edit-and-review workflows | Large-file analytics | Quick analysis |

**When to pick CSV Editor:** you want the AI to *make changes* to a CSV and iterate, not just answer questions about it. If your workload is read-only analytics on multi-GB files, a DuckDB-based MCP is likely a better fit; CSV Editor's DuckDB/Polars engine support is tracked on the [roadmap](#-roadmap).

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
<summary><b>Claude Desktop</b> (click to expand)</summary>

Add to your `claude_desktop_config.json`:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

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
<summary><b>Claude Code, Cursor, Windsurf, VS Code Copilot, Cline, Continue, Zed</b></summary>

Any MCP-capable client works with stdio transport. See [MCP_CONFIG.md](MCP_CONFIG.md) for per-client setup.
</details>

<details>
<summary><b>ChatGPT Connectors (remote HTTP)</b></summary>

ChatGPT Connectors require remote Streamable HTTP with OAuth, which is tracked on the [roadmap](#-roadmap) but not yet in v2.0.0. Use stdio-based clients (Claude Desktop, Claude Code, Cursor, etc.) in the meantime.
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

## 📚 Available Tools

<details>
<summary><b>Complete tool list (39 tools)</b></summary>

### Server info (2)
- `health_check` — health status + active session count
- `get_server_info` — capabilities, supported formats, limits

### I/O operations (7)
- `load_csv` — Load from file
- `load_csv_from_url` — Load from URL
- `load_csv_from_content` — Load from string
- `export_csv` — Export to various formats (csv, tsv, json, excel, parquet, html, markdown)
- `get_session_info` — Session details
- `list_sessions` — Active sessions
- `close_session` — Cleanup

### Data manipulation (10)
- `filter_rows` — Complex filtering
- `sort_data` — Multi-column sort
- `select_columns` — Column selection
- `rename_columns` — Rename columns
- `add_column` — Add computed columns
- `remove_columns` — Remove columns
- `update_column` — Update values
- `change_column_type` — Type conversion
- `fill_missing_values` — Handle nulls
- `remove_duplicates` — Deduplicate

### Analysis (7)
- `get_statistics` — Statistical summary
- `get_column_statistics` — Column stats
- `get_correlation_matrix` — Correlations
- `group_by_aggregate` — Group operations
- `get_value_counts` — Frequency counts
- `detect_outliers` — Find outliers (IQR, Z-score)
- `profile_data` — Data profiling

### Validation (3)
- `validate_schema` — Schema validation
- `check_data_quality` — Quality metrics + overall score
- `find_anomalies` — Anomaly detection

### Auto-save (4)
- `configure_auto_save` — Setup auto-save strategy
- `disable_auto_save` — Turn off auto-save
- `get_auto_save_status` — Check status
- `trigger_manual_save` — Force a save now

### History (6)
- `undo` — Step back one operation
- `redo` — Step forward after undo
- `get_history` — View operations log
- `restore_to_operation` — Time travel to a specific operation
- `clear_history` — Reset history
- `export_history` — Export operations log

</details>

## ⚙️ Configuration

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `CSV_MAX_FILE_SIZE` | `1024` (MB) | Maximum file size (megabytes) |
| `CSV_SESSION_TIMEOUT` | `60` (minutes) | Session timeout |
| `CSV_EDITOR_CSV_HISTORY_DIR` | `.csv_history` | Directory for persisted operation history |

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

### From PyPI (once v2.0.0 is live)
```bash
pip install csv-editor            # latest
pip install csv-editor==2.0.0     # pinned
# Or with uv:
uv tool install csv-editor
```

### From GitHub
```bash
# Latest main
pip install git+https://github.com/santoshray02/csv-editor.git

# Specific release
pip install git+https://github.com/santoshray02/csv-editor.git@v2.0.0

# Or with uv
uv pip install git+https://github.com/santoshray02/csv-editor.git@v2.0.0
```

</details>

## 🧪 Development

### Running tests
```bash
uv run pytest tests/ -v                  # Run tests
uv run pytest tests/ --cov=src/csv_editor # With coverage
uv run ruff check src/ tests/             # Lint
uv run black --check src/ tests/          # Format check
uv run mypy src/                          # Type check
```

CI runs the full pytest matrix on Python 3.11–3.14 for every push to main — see [.github/workflows/test.yml](.github/workflows/test.yml).

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
4. Run `uv run pytest tests/` and `uv run ruff check src/ tests/`
5. Submit a pull request

## 📈 Roadmap

Post-v2.0.0 priorities (see the [2026 relevance audit](specs/2026-04-19-fastmcp3-migration-design.md) for context):

- [ ] **pandas 3.0 / numpy 2.4** — Copy-on-Write migration, Arrow-backed default strings (follow-up to v2.0.0).
- [ ] **DuckDB + Polars engines** — swappable backends with DuckDB as the default for files >100 MB (closes the large-file gap).
- [ ] **MCP async Tasks + Resource Links** — non-blocking `load_csv` / `export_csv` / `profile_data` for GB files; paginated large results.
- [ ] **Remote HTTP + OAuth (CIMD)** — enables ChatGPT Connectors and VS Code Copilot remote usage.
- [ ] **Elicitation** — prompt for ambiguous CSV dialect / encoding / dtype at load time instead of failing.
- [ ] **Docs migration** — Docusaurus → MkDocs-Material with `mkdocstrings` for auto-generated API docs.

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/santoshray02/csv-editor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/santoshray02/csv-editor/discussions)
- **Documentation**: [Wiki](https://github.com/santoshray02/csv-editor/wiki)

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast Model Context Protocol
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [NumPy](https://numpy.org/) - Numerical computing

---

**Ready to supercharge your AI's data capabilities?** [Get started in 2 minutes →](#-quick-start-2-minutes)