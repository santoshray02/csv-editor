# CSV Editor MCP Server - Comprehensive CSV data manipulation and analysis tool

This server provides powerful tools for working with CSV files through pandas-based operations:

## Core Capabilities:
• **Data I/O**: Load from files, URLs, or content; export to multiple formats (CSV, JSON, Excel, Parquet)
• **Data Transformation**: Filter, sort, group, aggregate, type conversion, missing value handling
• **Analytics**: Statistical analysis, correlation matrices, outlier detection, data profiling
• **Validation**: Schema validation, data quality checks, anomaly detection
• **History Management**: Undo/redo operations, persistent history, operation tracking
• **Auto-Save**: Configurable automatic saving with multiple strategies

## Getting Started:
1. Use `load_csv()` or `load_csv_from_content()` to load data into a session
2. Apply transformations like `filter_rows()`, `sort_data()`, `group_by_aggregate()`
3. Analyze with `get_statistics()`, `get_correlation_matrix()`, `profile_data()`
4. Validate data quality with `validate_schema()`, `check_data_quality()`
5. Export results with `export_csv()` to various formats

## Key Features:
• **Session-based**: Multiple independent data sessions with automatic cleanup
• **History tracking**: Full operation history with snapshots for undo/redo
• **Auto-save**: Configurable automatic backup strategies
• **Progress reporting**: Real-time feedback for long operations
• **Error handling**: Comprehensive error reporting and validation

Use `list_sessions()` to see active sessions and `get_session_info()` for session details.
All operations return structured results with success/error status and detailed information.