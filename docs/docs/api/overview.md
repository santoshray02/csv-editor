---
sidebar_position: 1
title: API Overview
---

# API Reference Overview

CSV Editor provides a comprehensive set of tools for CSV manipulation through the Model Context Protocol (MCP). This reference documents all available tools, their parameters, and usage examples.

## Tool Categories

### 📁 I/O Operations
Tools for loading and exporting CSV data in various formats.

- [load_csv](./io/load-csv) - Load CSV from file
- [load_csv_from_url](./io/load-url) - Load CSV from URL
- [load_csv_from_content](./io/load-content) - Load CSV from string
- [export_csv](./io/export) - Export to various formats
- [get_session_info](./io/session-info) - Get session details
- [list_sessions](./io/list-sessions) - List active sessions
- [close_session](./io/close-session) - Close a session

### 🔧 Data Manipulation
Tools for transforming and modifying CSV data.

- [filter_rows](./manipulation/filter) - Filter with conditions
- [sort_data](./manipulation/sort) - Sort by columns
- [select_columns](./manipulation/select) - Select specific columns
- [rename_columns](./manipulation/rename) - Rename columns
- [add_column](./manipulation/add-column) - Add new columns
- [remove_columns](./manipulation/remove) - Remove columns
- [update_column](./manipulation/update) - Update column values
- [change_column_type](./manipulation/change-type) - Convert data types
- [fill_missing_values](./manipulation/fill-missing) - Handle nulls
- [remove_duplicates](./manipulation/remove-duplicates) - Deduplicate

### 📊 Analysis
Tools for statistical analysis and data exploration.

- [get_statistics](./analysis/statistics) - Statistical summary
- [get_column_statistics](./analysis/column-stats) - Column statistics
- [get_correlation_matrix](./analysis/correlation) - Correlation analysis
- [group_by_aggregate](./analysis/group-by) - Group operations
- [get_value_counts](./analysis/value-counts) - Frequency counts
- [detect_outliers](./analysis/outliers) - Find outliers
- [profile_data](./analysis/profile) - Data profiling

### ✅ Validation
Tools for data quality and validation.

- [validate_schema](./validation/schema) - Schema validation
- [check_data_quality](./validation/quality) - Quality metrics
- [find_anomalies](./validation/anomalies) - Anomaly detection

### 💾 Auto-Save & History
Tools for persistence and version control.

- [configure_auto_save](./persistence/auto-save) - Configure auto-save
- [get_auto_save_status](./persistence/auto-save-status) - Check status
- [trigger_manual_save](./persistence/manual-save) - Manual save
- [undo](./persistence/undo) - Undo last operation
- [redo](./persistence/redo) - Redo operation
- [get_history](./persistence/history) - View history
- [restore_to_operation](./persistence/restore) - Time travel

## Common Patterns

### Session Management

All operations require a session ID obtained from loading data:

```python
# Load data and get session ID
result = await load_csv(file_path="/path/to/data.csv")
session_id = result["session_id"]

# Use session ID in subsequent operations
await filter_rows(session_id=session_id, conditions=[...])
await export_csv(session_id=session_id, format="excel")
```

### Error Handling

All tools return consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ValueError",
  "details": "Additional context"
}
```

### Response Format

Successful operations return:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed",
  "metadata": {
    "rows_affected": 100,
    "execution_time": 0.123
  }
}
```

## Data Types

### Supported Column Types
- `string` - Text data
- `integer` - Whole numbers
- `float` - Decimal numbers
- `datetime` - Date and time
- `boolean` - True/False values
- `category` - Categorical data

### Export Formats
- `csv` - Comma-separated values
- `tsv` - Tab-separated values
- `json` - JSON array or records
- `excel` - Excel spreadsheet (.xlsx)
- `parquet` - Apache Parquet format
- `html` - HTML table
- `markdown` - Markdown table

## Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal to | `{"column": "status", "operator": "==", "value": "active"}` |
| `!=` | Not equal to | `{"column": "status", "operator": "!=", "value": "inactive"}` |
| `>` | Greater than | `{"column": "amount", "operator": ">", "value": 1000}` |
| `<` | Less than | `{"column": "age", "operator": "<", "value": 18}` |
| `>=` | Greater than or equal | `{"column": "score", "operator": ">=", "value": 80}` |
| `<=` | Less than or equal | `{"column": "price", "operator": "<=", "value": 100}` |
| `contains` | Contains substring | `{"column": "name", "operator": "contains", "value": "John"}` |
| `starts_with` | Starts with | `{"column": "email", "operator": "starts_with", "value": "admin"}` |
| `ends_with` | Ends with | `{"column": "file", "operator": "ends_with", "value": ".csv"}` |
| `in` | In list | `{"column": "category", "operator": "in", "value": ["A", "B"]}` |
| `not_in` | Not in list | `{"column": "status", "operator": "not_in", "value": ["deleted"]}` |
| `is_null` | Is null | `{"column": "email", "operator": "is_null"}` |
| `not_null` | Is not null | `{"column": "phone", "operator": "not_null"}` |

## Aggregation Functions

Available aggregation functions for `group_by_aggregate`:

- `sum` - Sum of values
- `mean` - Average value
- `median` - Median value
- `min` - Minimum value
- `max` - Maximum value
- `count` - Count of non-null values
- `std` - Standard deviation
- `var` - Variance
- `first` - First value
- `last` - Last value

## Best Practices

1. **Always close sessions** when done to free resources
2. **Use chunking** for large files (>100MB)
3. **Enable auto-save** for important data
4. **Validate data** before processing
5. **Use appropriate data types** for better performance
6. **Handle errors gracefully** in your client code

## Rate Limits

- Maximum file size: 1GB (configurable)
- Maximum concurrent sessions: 10 per user
- Session timeout: 1 hour (configurable)
- Maximum rows per operation: 10 million

## Next Steps

- Explore specific tool documentation in each category
- See [Examples](../examples) for real-world use cases
- Check [Tutorials](../tutorials/quickstart) for step-by-step guides