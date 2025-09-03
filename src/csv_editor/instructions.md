# CSV Editor MCP Server - Comprehensive CSV data manipulation and analysis tool

This server provides powerful tools for working with CSV files through pandas-based operations, optimized for AI accessibility with precise coordinate-based data manipulation.

## Coordinate System (AI-Friendly Indexing)
**🎯 Zero-based indexing** for maximum precision:
- **Rows**: 0 to N-1 (where N = total rows)
- **Columns**: Use column names (strings) OR 0-based indices (integers)
- **Cells**: Address as (row_index, column) - e.g., (0, "name") or (2, 1)

### Example Data Structure:
```
    Column indices:  0      1      2
                   name   age   city
Row 0:             John   30    NYC      <- get_cell_value(session, 0, "name") → "John"
Row 1:             Jane   25    LA       <- get_cell_value(session, 1, 1) → 25  
Row 2:             Bob    35    Chicago  <- get_row_data(session, 2) → {"name": "Bob", "age": 35, "city": "Chicago"}
```

## Core Capabilities:

### 🔍 **Cell-Level Access** (AI Optimized):
• `get_cell_value(session_id, row_index, column)` - Get specific cell value with coordinates
• `set_cell_value(session_id, row_index, column, value)` - Update specific cell with tracking (**supports null values**)
• `get_row_data(session_id, row_index, columns=None)` - Get full or partial row data
• `get_column_data(session_id, column, start_row=None, end_row=None)` - Get column slice

### 🎯 **Row Operations** (Null-Value Compatible):
• `insert_row(session_id, row_index, data)` - Insert row with dict/list/JSON string (**null values supported**)
• `update_row(session_id, row_index, data)` - Update row columns with dict/JSON string (**null values supported**)
• `delete_row(session_id, row_index)` - Remove row at specified index

**🔧 JSON String Compatibility**: All row operations automatically parse JSON strings from Claude Code

### 📝 **Focused Data Transformations** (NEW - Eliminates operation parameters):
• `replace_in_column(column, pattern, replacement, regex=True)` - Text replacement with regex
• `extract_from_column(column, pattern, expand=False)` - Regex pattern extraction  
• `split_column(column, delimiter, part_index=None, expand_to_columns=False)` - String splitting
• `transform_column_case(column, transform)` - Case transformations (upper/lower/title/capitalize)
• `strip_column(column, chars=None)` - Remove whitespace/characters
• `fill_column_nulls(column, value)` - Fill null values specifically

### 💾 **Data I/O**: 
Load from files, URLs, or content; export to multiple formats (CSV, JSON, Excel, Parquet)

### 🔄 **Data Transformation**: 
Filter, sort, group, aggregate, type conversion, missing value handling

### 📊 **Analytics**: 
Statistical analysis, correlation matrices, outlier detection, data profiling

### ✅ **Validation**: 
Schema validation, data quality checks, anomaly detection

### 📈 **History Management**: 
Undo/redo operations, persistent history, operation tracking

### 💾 **Auto-Save**: 
Configurable automatic saving with multiple strategies

## Getting Started (AI Workflow):

### Step 1: Load Data
```python
# Load from content (most common for AI)
load_csv_from_content("name,age,city\nJohn,30,NYC\nJane,25,LA")
# Returns: session_id + enhanced preview with __row_index__ field
```

### Step 2: Inspect Data Structure
```python
# Get data with coordinates
get_session_info(session_id)  # Get shape, columns, memory info
get_row_data(session_id, 0)   # Inspect first row
get_column_data(session_id, "age", 0, 5)  # Get first 5 age values
```

### Step 3: Precise Cell Operations
```python
# Read specific cells
get_cell_value(session_id, 0, "name")     # First row, name column → "John"
get_cell_value(session_id, 1, 1)          # Second row, second column → 25

# Update specific cells  
set_cell_value(session_id, 0, "age", 31)  # Update John's age to 31
```

### Step 4: Work with Null Values
```python
# Insert rows with null values (JSON null → Python None → pandas NaN)
insert_row(session_id, -1, {
    "name": "Alice Smith",
    "email": null,              # Null values fully supported
    "phone": null,
    "status": "Active"
})

# Set cells to null
set_cell_value(session_id, 2, "email", null)

# Filter for/against null values
filter_rows(session_id, [{"column": "email", "operator": "is_null"}])
filter_rows(session_id, [{"column": "phone", "operator": "is_not_null"}])
```

### Step 5: Apply Focused Transformations
```python
# Clear, purpose-specific methods (no operation parameters!)
replace_in_column(session_id, "name", "John", "Jonathan")  # Name replacement
transform_column_case(session_id, "city", "upper")        # NYC → NYC, la → LA
strip_column(session_id, "name")                          # Remove whitespace
```

### Step 6: Analyze & Export
```python
get_statistics(session_id, ["age"])       # Statistical analysis
export_csv(session_id, "output.csv")     # Save results
```

## Enhanced Resource Endpoints:
- `csv://{session_id}/data` - Full data with enhanced indexing
- `csv://{session_id}/cell/{row}/{col}` - Direct cell access
- `csv://{session_id}/row/{index}` - Row-specific data
- `csv://{session_id}/preview` - Enhanced preview with coordinate system docs
- `csv://{session_id}/schema` - Column information and data types

## Key Features:
• **Session-based**: Multiple independent data sessions with automatic cleanup
• **History tracking**: Full operation history with snapshots for undo/redo
• **Coordinate precision**: Every operation includes row/column coordinate information
• **AI-optimized returns**: All data includes indexing for precise reference
• **Clear method names**: No confusing operation parameters - method names express intent
• **Enhanced error messages**: Include valid coordinate ranges in error responses
• **Progress reporting**: Real-time feedback for long operations
• **Type safety**: Proper handling of pandas/numpy types for JSON serialization
• **Null value support**: Full JSON null → Python None → pandas NaN compatibility
• **Claude Code compatible**: Automatic JSON string deserialization

## AI Usage Patterns:
1. **Inspection**: Use `get_session_info()` → `get_row_data()` → `get_cell_value()` for drilling down
2. **Bulk updates**: Use `get_column_data()` to understand data → focused transformation methods
3. **Precise editing**: Use `set_cell_value()` for specific corrections
4. **Data exploration**: Use enhanced resources for coordinate-aware data access

All operations return structured results with success/error status, coordinate information, and detailed metadata.

## 🔧 Technical Notes for AI Clients:

### Claude Code JSON String Handling
Claude Code serializes complex parameters as JSON strings instead of objects. CSV Editor automatically handles this:

**What Claude Code sends:**
```json
{
  "session_id": "abc123",
  "data": "{\"name\": \"John\", \"email\": null, \"status\": \"active\"}"
}
```

**Automatically parsed to:**
```python
{
  "session_id": "abc123", 
  "data": {"name": "John", "email": None, "status": "active"}
}
```

**Functions with JSON string support:** `insert_row`, `update_row`

### Null Value Handling
- JSON `null` values are preserved as Python `None`
- Python `None` values become pandas `NaN` in DataFrames
- All operations (insert, update, filter) fully support null values
- Use `is_null`/`is_not_null` operators for filtering null values