# CSV Editor - Research & Implementation Documentation

## ✅ Implementation Status: COMPLETED!

**This comprehensive research document guided the successful implementation of a production-ready CSV editor MCP server using FastMCP.**

### 🎯 Implementation Summary
- **30+ Tools Implemented**: All planned CSV operations completed
- **Modern Stack**: Using uv (ultra-fast package manager), Ruff, Black, MyPy
- **Full Type Safety**: 100% type hints with Pydantic validation
- **Production Ready**: Error handling, logging, session management
- **Latest Dependencies**: FastMCP 2.11.3+, Pandas 2.2.3+, NumPy 2.1.3+

### 📦 Technology Decisions
- **Package Manager**: **uv** chosen over pip/poetry/hatch (10-100x faster)
- **Build Backend**: Hatchling (for packaging only, not environment management)
- **Linting**: Ruff (replaces flake8, isort, pylint - all in one)
- **Formatting**: Black
- **Type Checking**: MyPy with strict mode

---

## Original Research & Planning

This document contains the comprehensive research that guided the implementation. The server provides CSV manipulation capabilities through a standardized Model Context Protocol interface, enabling AI assistants to perform complex data operations.

## Documentation & Resources

### FastMCP Documentation
- **Official Website**: [https://gofastmcp.com](https://gofastmcp.com)
- **Getting Started Guide**: [https://gofastmcp.com/getting-started](https://gofastmcp.com/getting-started)
- **Concepts Overview**: [https://gofastmcp.com/concepts](https://gofastmcp.com/concepts)
  - Tools: [https://gofastmcp.com/concepts/tools](https://gofastmcp.com/concepts/tools)
  - Resources: [https://gofastmcp.com/concepts/resources](https://gofastmcp.com/concepts/resources)
  - Context: [https://gofastmcp.com/concepts/context](https://gofastmcp.com/concepts/context)
  - Prompts: [https://gofastmcp.com/concepts/prompts](https://gofastmcp.com/concepts/prompts)
- **Tutorials**: [https://gofastmcp.com/tutorials](https://gofastmcp.com/tutorials)
  - Your First Server: [https://gofastmcp.com/tutorials/your-first-server](https://gofastmcp.com/tutorials/your-first-server)
- **API Reference**: [https://gofastmcp.com/reference](https://gofastmcp.com/reference)

### GitHub Resources
- **FastMCP Repository**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Examples Directory**: [https://github.com/jlowin/fastmcp/tree/main/examples](https://github.com/jlowin/fastmcp/tree/main/examples)
- **Issues & Discussions**: [https://github.com/jlowin/fastmcp/issues](https://github.com/jlowin/fastmcp/issues)

### MCP Protocol Documentation
- **Model Context Protocol Spec**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **MCP Python SDK**: [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **MCP TypeScript SDK**: [https://github.com/modelcontextprotocol/typescript-sdk](https://github.com/modelcontextprotocol/typescript-sdk)

### Supporting Libraries Documentation
- **Pandas Documentation**: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)
  - CSV Reading: [https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
  - DataFrame Operations: [https://pandas.pydata.org/docs/reference/frame.html](https://pandas.pydata.org/docs/reference/frame.html)
- **NumPy Documentation**: [https://numpy.org/doc/stable/](https://numpy.org/doc/stable/)
- **Python Type Hints**: [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)
- **Pydantic for Validation**: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)

### Deployment & Infrastructure
- **Docker Documentation**: [https://docs.docker.com/](https://docs.docker.com/)
- **Redis Documentation**: [https://redis.io/documentation](https://redis.io/documentation)
- **FastAPI (for HTTP transport)**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **SSE (Server-Sent Events)**: [https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### Testing Resources
- **Pytest Documentation**: [https://docs.pytest.org/](https://docs.pytest.org/)
- **Pytest-asyncio**: [https://pytest-asyncio.readthedocs.io/](https://pytest-asyncio.readthedocs.io/)
- **Coverage.py**: [https://coverage.readthedocs.io/](https://coverage.readthedocs.io/)

### AI Integration Guides
- **Claude Desktop Integration**: [https://claude.ai/docs/desktop-integration](https://claude.ai/docs/desktop-integration)
- **OpenAI Function Calling**: [https://platform.openai.com/docs/guides/function-calling](https://platform.openai.com/docs/guides/function-calling)
- **LangChain MCP Integration**: [https://python.langchain.com/docs/integrations/tools/mcp](https://python.langchain.com/docs/integrations/tools/mcp)

### Best Practices & Patterns
- **CSV File Best Practices**: [https://www.w3.org/TR/tabular-data-primer/](https://www.w3.org/TR/tabular-data-primer/)
- **REST API Design**: [https://restfulapi.net/](https://restfulapi.net/)
- **Python Async Best Practices**: [https://docs.python.org/3/library/asyncio-task.html](https://docs.python.org/3/library/asyncio-task.html)
- **Error Handling in Python**: [https://docs.python.org/3/tutorial/errors.html](https://docs.python.org/3/tutorial/errors.html)

### Community & Support
- **FastMCP Discord**: Check GitHub repository for invite link
- **MCP Community Forum**: [https://community.modelcontextprotocol.io](https://community.modelcontextprotocol.io)
- **Stack Overflow Tags**: `fastmcp`, `model-context-protocol`, `mcp-server`

### Video Tutorials & Courses
- **FastMCP YouTube Channel**: Search "FastMCP tutorials" on YouTube
- **MCP Introduction Videos**: Available on the official MCP website
- **Python Async Programming**: [Real Python Async IO Tutorial](https://realpython.com/async-io-python/)

### Reference Implementations & Examples
- **FastMCP Examples**: [https://github.com/jlowin/fastmcp/tree/main/examples](https://github.com/jlowin/fastmcp/tree/main/examples)
  - Simple Echo Server: `examples/echo.py`
  - File Operations: `examples/get_file.py`
  - Complex Inputs: `examples/complex_inputs.py`
  - Sampling Example: `examples/sampling.py`
- **MCP Server Examples**: [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- **Community MCP Servers**: [https://github.com/topics/mcp-server](https://github.com/topics/mcp-server)

### Data Processing Libraries
- **Polars (Alternative to Pandas)**: [https://pola.rs/](https://pola.rs/)
- **DuckDB for SQL on CSV**: [https://duckdb.org/docs/data/csv](https://duckdb.org/docs/data/csv)
- **PyArrow for Parquet**: [https://arrow.apache.org/docs/python/](https://arrow.apache.org/docs/python/)
- **Dask for Large Datasets**: [https://docs.dask.org/](https://docs.dask.org/)

### Performance & Optimization
- **Memory Profiling with memory_profiler**: [https://pypi.org/project/memory-profiler/](https://pypi.org/project/memory-profiler/)
- **Line Profiler**: [https://github.com/pyutils/line_profiler](https://github.com/pyutils/line_profiler)
- **Pandas Performance Tips**: [https://pandas.pydata.org/docs/user_guide/enhancingperf.html](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)

### Security Resources
- **OWASP CSV Injection**: [https://owasp.org/www-community/attacks/CSV_Injection](https://owasp.org/www-community/attacks/CSV_Injection)
- **Python Security Best Practices**: [https://python.readthedocs.io/en/latest/library/security_warnings.html](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- **Input Validation Guide**: [https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

### Monitoring & Logging
- **Structured Logging with structlog**: [https://www.structlog.org/](https://www.structlog.org/)
- **OpenTelemetry Python**: [https://opentelemetry.io/docs/languages/python/](https://opentelemetry.io/docs/languages/python/)
- **Prometheus Python Client**: [https://github.com/prometheus/client_python](https://github.com/prometheus/client_python)

### Related Tools & Projects
- **Jupyter Notebooks**: [https://jupyter.org/documentation](https://jupyter.org/documentation)
- **Streamlit for Data Apps**: [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Apache Superset**: [https://superset.apache.org/](https://superset.apache.org/)
- **Metabase**: [https://www.metabase.com/docs/](https://www.metabase.com/docs/)

## 1. Architecture Overview

### 1.1 Core Technologies
- **FastMCP v2.0**: Primary framework for MCP server implementation
- **Pandas**: Data manipulation and CSV processing
- **NumPy**: Numerical operations and statistics
- **Python 3.9+**: Runtime environment
- **Type Hints**: Full typing for automatic validation

### 1.2 Design Principles
- **Stateless Operations**: Each tool call is independent
- **Session Management**: Support for multi-user concurrent sessions
- **Error Recovery**: Graceful handling of malformed data
- **Performance**: Efficient processing of large CSV files (up to 1GB)
- **Extensibility**: Plugin architecture for custom operations

## 2. Core Components

### 2.1 MCP Server Structure
```
csv-editor/
├── src/
│   ├── __init__.py
│   ├── server.py           # Main MCP server definition
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── data_operations.py    # CRUD operations
│   │   ├── transformations.py    # Data transformation tools
│   │   ├── analytics.py          # Statistical analysis
│   │   ├── validation.py         # Data validation tools
│   │   └── io_operations.py      # Import/Export tools
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── csv_resources.py      # CSV data resources
│   │   └── schema_resources.py   # Schema definitions
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── data_prompts.py       # Reusable prompts
│   ├── models/
│   │   ├── __init__.py
│   │   ├── csv_session.py        # Session management
│   │   └── data_models.py        # Data type definitions
│   └── utils/
│       ├── __init__.py
│       ├── validators.py         # Input validation
│       ├── converters.py         # Type conversion
│       └── cache_manager.py      # Caching logic
├── tests/
├── examples/
├── requirements.txt
└── README.md
```

### 2.2 Session Management Architecture
- **Session Store**: Redis or in-memory dictionary
- **Session ID**: UUID-based unique identifiers
- **Session Data**: DataFrame state, metadata, history
- **TTL Management**: Configurable session expiration
- **Cleanup**: Automatic garbage collection

## 3. Tool Categories and Implementation

### 3.1 Data Loading and I/O Operations

#### 3.1.1 Core Loading Tools
```python
@mcp.tool
async def load_csv(
    file_path: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load CSV file with automatic type inference"""
    
@mcp.tool
async def load_csv_from_url(
    url: str,
    session_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load CSV from HTTP/HTTPS URL"""

@mcp.tool
async def load_csv_from_content(
    content: str,
    delimiter: str = ",",
    session_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load CSV from string content"""
```

#### 3.1.2 Export Tools
```python
@mcp.tool
async def export_csv(
    session_id: str,
    file_path: Optional[str] = None,
    format: Literal["csv", "tsv", "excel", "json", "parquet"] = "csv",
    ctx: Context = None
) -> Dict[str, Any]:
    """Export data to various formats"""

@mcp.tool
async def get_download_link(
    session_id: str,
    format: str = "csv",
    ctx: Context = None
) -> str:
    """Generate temporary download link"""
```

### 3.2 Data Manipulation Tools

#### 3.2.1 Filtering and Selection
```python
@mcp.tool
async def filter_rows(
    session_id: str,
    conditions: List[Dict[str, Any]],
    logical_operator: Literal["AND", "OR"] = "AND",
    ctx: Context = None
) -> Dict[str, Any]:
    """Advanced filtering with multiple conditions"""

@mcp.tool
async def select_columns(
    session_id: str,
    columns: List[str],
    exclude: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """Select or exclude specific columns"""

@mcp.tool
async def query_data(
    session_id: str,
    sql_query: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Execute SQL-like queries on CSV data"""
```

#### 3.2.2 Sorting and Ordering
```python
@mcp.tool
async def sort_data(
    session_id: str,
    columns: List[str],
    ascending: List[bool] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Multi-column sorting"""

@mcp.tool
async def rank_data(
    session_id: str,
    column: str,
    method: Literal["average", "min", "max", "first", "dense"] = "average",
    ctx: Context = None
) -> Dict[str, Any]:
    """Add ranking column"""
```

### 3.3 Data Transformation Tools

#### 3.3.1 Column Operations
```python
@mcp.tool
async def add_calculated_column(
    session_id: str,
    column_name: str,
    expression: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Add column with calculated values"""

@mcp.tool
async def rename_columns(
    session_id: str,
    column_mapping: Dict[str, str],
    ctx: Context = None
) -> Dict[str, Any]:
    """Rename multiple columns"""

@mcp.tool
async def change_column_type(
    session_id: str,
    column: str,
    dtype: Literal["int", "float", "string", "datetime", "boolean"],
    ctx: Context = None
) -> Dict[str, Any]:
    """Convert column data type"""
```

#### 3.3.2 Data Cleaning
```python
@mcp.tool
async def handle_missing_values(
    session_id: str,
    strategy: Literal["drop", "fill", "interpolate", "forward_fill", "backward_fill"],
    columns: Optional[List[str]] = None,
    fill_value: Any = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Handle missing values with various strategies"""

@mcp.tool
async def remove_duplicates(
    session_id: str,
    columns: Optional[List[str]] = None,
    keep: Literal["first", "last", "none"] = "first",
    ctx: Context = None
) -> Dict[str, Any]:
    """Remove duplicate rows"""

@mcp.tool
async def trim_whitespace(
    session_id: str,
    columns: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Remove leading/trailing whitespace"""
```

### 3.4 Data Analysis Tools

#### 3.4.1 Statistical Analysis
```python
@mcp.tool
async def get_statistics(
    session_id: str,
    columns: Optional[List[str]] = None,
    include_percentiles: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """Comprehensive statistical summary"""

@mcp.tool
async def correlation_analysis(
    session_id: str,
    columns: Optional[List[str]] = None,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    ctx: Context = None
) -> Dict[str, Any]:
    """Calculate correlation matrix"""

@mcp.tool
async def group_statistics(
    session_id: str,
    group_by: List[str],
    aggregations: Dict[str, List[str]],
    ctx: Context = None
) -> Dict[str, Any]:
    """Group-by aggregations"""
```

#### 3.4.2 Data Profiling
```python
@mcp.tool
async def profile_data(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Complete data profiling report"""

@mcp.tool
async def detect_outliers(
    session_id: str,
    columns: List[str],
    method: Literal["iqr", "zscore", "isolation_forest"] = "iqr",
    ctx: Context = None
) -> Dict[str, Any]:
    """Detect statistical outliers"""
```

### 3.5 Data Validation Tools

```python
@mcp.tool
async def validate_schema(
    session_id: str,
    schema: Dict[str, Any],
    ctx: Context = None
) -> Dict[str, Any]:
    """Validate data against schema"""

@mcp.tool
async def check_data_quality(
    session_id: str,
    rules: List[Dict[str, Any]],
    ctx: Context = None
) -> Dict[str, Any]:
    """Apply data quality rules"""

@mcp.tool
async def find_anomalies(
    session_id: str,
    columns: List[str],
    ctx: Context = None
) -> Dict[str, Any]:
    """Detect data anomalies"""
```

### 3.6 Advanced Operations

```python
@mcp.tool
async def merge_datasets(
    left_session: str,
    right_session: str,
    on: Union[str, List[str]],
    how: Literal["inner", "left", "right", "outer"] = "inner",
    ctx: Context = None
) -> Dict[str, Any]:
    """Merge two CSV datasets"""

@mcp.tool
async def pivot_table(
    session_id: str,
    index: List[str],
    columns: List[str],
    values: str,
    aggfunc: str = "mean",
    ctx: Context = None
) -> Dict[str, Any]:
    """Create pivot table"""

@mcp.tool
async def unpivot_data(
    session_id: str,
    id_vars: List[str],
    value_vars: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Unpivot/melt data"""
```

## 4. Resource Implementation

### 4.1 Dynamic CSV Resources
```python
@mcp.resource("csv://{session_id}/data")
async def get_csv_data(session_id: str, ctx: Context) -> Dict[str, Any]:
    """Get current CSV data as resource"""

@mcp.resource("csv://{session_id}/schema")
async def get_csv_schema(session_id: str, ctx: Context) -> Dict[str, Any]:
    """Get CSV schema information"""

@mcp.resource("csv://{session_id}/preview")
async def get_data_preview(session_id: str, ctx: Context) -> Dict[str, Any]:
    """Get data preview (first 100 rows)"""
```

### 4.2 Metadata Resources
```python
@mcp.resource("sessions://active")
async def list_active_sessions(ctx: Context) -> List[Dict[str, Any]]:
    """List all active CSV sessions"""

@mcp.resource("operations://history/{session_id}")
async def get_operation_history(session_id: str, ctx: Context) -> List[Dict[str, Any]]:
    """Get operation history for session"""
```

## 5. Prompt Templates

```python
@mcp.prompt
def analyze_csv_prompt(
    session_id: str,
    analysis_type: Literal["summary", "quality", "insights"]
) -> str:
    """Generate analysis prompt for CSV data"""

@mcp.prompt
def suggest_transformations_prompt(
    session_id: str,
    goal: str
) -> str:
    """Suggest data transformations based on goal"""

@mcp.prompt
def data_cleaning_prompt(
    session_id: str,
    issues: List[str]
) -> str:
    """Generate data cleaning recommendations"""
```

## 6. Context Integration

### 6.1 Progress Reporting
```python
async def process_large_csv(file_path: str, ctx: Context):
    await ctx.report_progress(0, "Starting CSV processing...")
    
    # Load data in chunks
    total_chunks = calculate_chunks(file_path)
    for i, chunk in enumerate(read_csv_chunks(file_path)):
        await ctx.report_progress(
            (i + 1) / total_chunks,
            f"Processing chunk {i + 1} of {total_chunks}"
        )
        process_chunk(chunk)
    
    await ctx.report_progress(1.0, "Processing complete!")
```

### 6.2 Logging Integration
```python
async def validate_data(session_id: str, ctx: Context):
    await ctx.info(f"Starting validation for session {session_id}")
    
    try:
        results = perform_validation(session_id)
        await ctx.info(f"Validation complete: {len(results)} issues found")
        return results
    except Exception as e:
        await ctx.error(f"Validation failed: {str(e)}")
        raise
```

### 6.3 LLM Sampling for Intelligence
```python
async def smart_data_analysis(session_id: str, ctx: Context):
    data_summary = get_data_summary(session_id)
    
    analysis = await ctx.sample(
        f"Analyze this dataset and suggest improvements:\n{data_summary}",
        max_tokens=500
    )
    
    return {
        "analysis": analysis.text,
        "suggestions": parse_suggestions(analysis.text)
    }
```

## 7. Error Handling Strategy

### 7.1 Error Categories
- **Input Validation Errors**: Invalid parameters, missing required fields
- **Data Format Errors**: Malformed CSV, encoding issues
- **Processing Errors**: Memory overflow, computation failures
- **Session Errors**: Invalid session ID, expired sessions
- **Resource Errors**: File not found, network issues

### 7.2 Error Response Format
```python
{
    "success": False,
    "error": {
        "type": "ValidationError",
        "message": "Column 'price' contains non-numeric values",
        "details": {
            "column": "price",
            "invalid_rows": [23, 45, 67],
            "suggestion": "Use change_column_type tool to convert to numeric"
        }
    },
    "session_id": "uuid-here",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 8. Performance Optimization

### 8.1 Chunked Processing
- Process large files in configurable chunks (default: 10,000 rows)
- Stream processing for files > 100MB
- Lazy loading for initial preview

### 8.2 Caching Strategy
- Cache frequently accessed columns
- Memoize statistical computations
- Store intermediate results for complex operations

### 8.3 Memory Management
- Automatic garbage collection for expired sessions
- Column-wise operations for memory efficiency
- Data type optimization (downcast numerics)

## 9. Security Considerations

### 9.1 Input Validation
- Sanitize file paths (prevent directory traversal)
- Validate SQL queries (prevent injection)
- Limit expression evaluation to safe operations

### 9.2 Resource Limits
- Maximum file size: 1GB (configurable)
- Maximum session duration: 1 hour (configurable)
- Maximum concurrent sessions: 100 (configurable)

### 9.3 Data Privacy
- Optional data anonymization tools
- Session isolation
- Secure temporary file handling

## 10. Testing Strategy

### 10.1 Unit Tests
- Test each tool in isolation
- Mock context and session management
- Validate error handling

### 10.2 Integration Tests
- Test tool combinations
- Session lifecycle testing
- Resource access patterns

### 10.3 Performance Tests
- Large file handling (100MB, 500MB, 1GB)
- Concurrent session stress testing
- Memory leak detection

### 10.4 Test Data
- Various CSV formats (standard, TSV, pipe-delimited)
- Different encodings (UTF-8, Latin-1, etc.)
- Edge cases (empty files, single column, special characters)

## 11. Deployment Configuration

### 11.1 Transport Options
```python
# STDIO (for local development)
mcp.run()

# HTTP Streaming
mcp.run(transport="http", host="0.0.0.0", port=8000)

# Server-Sent Events
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### 11.2 Environment Variables
```bash
CSV_MCP_MAX_FILE_SIZE=1073741824  # 1GB in bytes
CSV_MCP_SESSION_TIMEOUT=3600      # 1 hour in seconds
CSV_MCP_CACHE_SIZE=104857600      # 100MB cache
CSV_MCP_CHUNK_SIZE=10000          # Rows per chunk
CSV_MCP_LOG_LEVEL=INFO
```

### 11.3 MCP Servers Repository Integration
```markdown
# For submission to https://github.com/modelcontextprotocol/servers

## Repository Structure
csv-editor/
├── README.md              # Comprehensive documentation
├── pyproject.toml         # Python package configuration  
├── LICENSE               # MIT License
├── src/
│   └── csv_editor/
│       ├── __init__.py
│       ├── server.py     # Main FastMCP server
│       └── tools/        # Tool implementations
└── tests/

## Installation
pip install csv-editor

## Claude Desktop Configuration
Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "csv-editor": {
      "command": "python",
      "args": ["-m", "csv_editor.server"]
    }
  }
}
```

## 12. Client Integration Examples

### 12.1 Python Client
```python
from fastmcp import FastMCPClient

async with FastMCPClient("http://localhost:8000") as client:
    # Load CSV
    result = await client.call_tool("load_csv", {
        "file_path": "/data/sales.csv"
    })
    session_id = result["session_id"]
    
    # Filter data
    await client.call_tool("filter_rows", {
        "session_id": session_id,
        "conditions": [{"column": "sales", "operator": ">", "value": 1000}]
    })
    
    # Get statistics
    stats = await client.call_tool("get_statistics", {
        "session_id": session_id
    })
```

### 12.2 CLI Usage
```bash
# Start server
fastmcp run src.server

# Or with custom config
fastmcp run src.server --transport http --port 8000
```

## 13. Monitoring and Observability

### 13.1 Metrics
- Request latency per tool
- Session count and duration
- Memory usage per session
- Cache hit rates
- Error rates by category

### 13.2 Logging
- Structured JSON logging
- Correlation IDs for request tracking
- Sensitive data masking
- Log aggregation support

### 13.3 Health Checks
```python
@mcp.tool
async def health_check(ctx: Context) -> Dict[str, Any]:
    """System health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "active_sessions": get_session_count(),
        "memory_usage_mb": get_memory_usage(),
        "uptime_seconds": get_uptime()
    }
```

## 14. Documentation Requirements

### 14.1 API Documentation
- OpenAPI/Swagger specification
- Tool parameter descriptions
- Example requests and responses
- Error code reference

### 14.2 User Guide
- Quick start tutorial
- Common use cases
- Best practices
- Troubleshooting guide

### 14.3 Developer Documentation
- Architecture overview
- Extension points
- Contributing guidelines
- Plugin development guide

## 15. Future Enhancements

### 15.1 Phase 2 Features
- Machine learning integration (auto-ML features)
- Real-time collaboration support
- Streaming data support
- Database connectivity (direct SQL queries)
- Advanced visualizations

### 15.2 Phase 3 Features
- Distributed processing (Dask/Ray integration)
- Custom function registration
- Webhook notifications
- Data versioning
- Automated data quality monitoring

## 16. Implementation Timeline

### Week 1-2: Foundation
- Set up project structure
- Implement core session management
- Basic I/O operations
- Initial testing framework

### Week 3-4: Core Tools
- Data manipulation tools
- Transformation tools
- Basic analysis tools
- Error handling

### Week 5-6: Advanced Features
- Advanced analysis tools
- Validation tools
- Resource implementation
- Prompt templates

### Week 7-8: Integration & Testing
- Context integration
- Comprehensive testing
- Performance optimization
- Documentation

### Week 9-10: Production Ready
- Deployment configurations
- Monitoring setup
- Security hardening
- Final testing and release

## 17. Success Metrics

- **Performance**: Process 1GB file in < 30 seconds
- **Reliability**: 99.9% uptime
- **Scalability**: Support 100 concurrent sessions
- **Usability**: 90% of operations require single tool call
- **Compatibility**: Work with 95% of real-world CSV files

## 18. MCP Servers Repository Integration

### 18.1 Publishing to modelcontextprotocol/servers

#### Repository Structure Requirements
```
csv-editor/
├── README.md                 # Comprehensive documentation
├── pyproject.toml           # Python package configuration
├── LICENSE                  # MIT License (required)
├── src/
│   └── csv_editor/
│       ├── __init__.py
│       ├── server.py       # Main FastMCP server
│       ├── tools.py        # Tool implementations
│       ├── resources.py    # Resource definitions
│       └── prompts.py      # Prompt templates
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   └── test_integration.py
└── examples/
    ├── basic_usage.py
    └── sample_data.csv
```

#### pyproject.toml Template
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "csv-editor"
version = "1.0.0"
description = "A Model Context Protocol server for CSV operations"
readme = "README.md"
license = "MIT"
authors = [
    { name = "Your Name", email = "email@example.com" }
]
requires-python = ">=3.9"
dependencies = [
    "fastmcp>=2.0.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]

[project.urls]
"Homepage" = "https://github.com/santoshray02/csv-editor"
"Issues" = "https://github.com/santoshray02/csv-editor/issues"
```

#### README.md Requirements
```markdown
# CSV Editor MCP Server

A FastMCP server providing comprehensive CSV manipulation tools.

## Installation

### Using pip
pip install csv-editor

### Using uv (recommended)
uv add csv-editor

## Configuration

### Claude Desktop
Add to ~/Library/Application Support/Claude/claude_desktop_config.json:
{
  "mcpServers": {
    "csv-editor": {
      "command": "python",
      "args": ["-m", "csv_editor.server"]
    }
  }
}

### Other MCP Clients
{
  "mcp": {
    "servers": {
      "csv-editor": {
        "command": "python",
        "args": ["-m", "csv_editor.server"]
      }
    }
  }
}

## Available Tools

[List all tools with descriptions]

## Usage Examples

[Provide clear examples of common use cases]

## License
MIT
```

### 18.2 Submission Process

1. **Prepare Repository**:
   - Ensure all required files are present
   - Run tests and verify functionality
   - Test with Claude Desktop

2. **Fork and Clone**:
   ```bash
   gh repo fork modelcontextprotocol/servers
   git clone https://github.com/santoshray02/servers
   cd servers
   ```

3. **Add Your Server**:
   - Create directory: `src/csv-editor/`
   - Add all server files
   - Update root README.md in alphabetical order

4. **Submit PR**:
   ```bash
   git add .
   git commit -m "Add CSV Editor MCP server"
   git push origin main
   gh pr create --title "Add CSV Editor MCP server" \
     --body "Adds comprehensive CSV manipulation server using FastMCP"
   ```

### 18.3 Quality Checklist

- [ ] **Documentation**
  - [ ] Clear README with examples
  - [ ] All tools documented
  - [ ] Configuration examples for multiple clients
  
- [ ] **Code Quality**
  - [ ] Type hints on all functions
  - [ ] Docstrings for tools
  - [ ] Error handling
  - [ ] No hardcoded paths
  
- [ ] **Testing**
  - [ ] Unit tests for core functionality
  - [ ] Integration tests
  - [ ] Tested with Claude Desktop
  
- [ ] **Package**
  - [ ] Installable via pip
  - [ ] Dependencies properly specified
  - [ ] Version numbering follows semver

- [ ] **Security**
  - [ ] Input validation
  - [ ] Path traversal prevention
  - [ ] No credential exposure

## 19. Conclusion

This generic CSV Editor MCP Server will provide a robust, scalable, and intelligent interface for CSV data manipulation through the Model Context Protocol. By leveraging FastMCP v2.0's capabilities and following best practices, we'll create a production-ready tool that can be integrated with any MCP-compatible AI assistant or application.

The modular architecture ensures easy maintenance and extension, while the comprehensive tool set covers all common CSV operations and beyond. With proper testing, documentation, and deployment strategies, this server will serve as a reliable foundation for AI-powered data processing workflows.