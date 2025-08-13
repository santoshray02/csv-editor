---
sidebar_position: 1
title: Quick Start
---

# Quick Start Tutorial

Learn how to use CSV Editor in 10 minutes with this hands-on tutorial. We'll process a sample sales dataset step by step.

## Prerequisites

- CSV Editor installed and configured (see [Installation Guide](../installation))
- An AI assistant client (Claude Desktop, Continue, etc.) configured

## Sample Dataset

For this tutorial, we'll use a sample sales dataset. You can create it or use your own CSV file.

```csv
date,product,category,quantity,price,customer_id
2024-01-15,Laptop,Electronics,2,1299.99,C001
2024-01-16,Mouse,Electronics,5,29.99,C002
2024-01-16,Desk,Furniture,1,399.99,C001
2024-01-17,Chair,Furniture,3,199.99,C003
2024-01-18,Monitor,Electronics,2,599.99,C002
2024-01-18,Keyboard,Electronics,,89.99,C001
2024-01-19,Lamp,Furniture,4,49.99,
2024-01-20,Laptop,Electronics,1,1299.99,C004
2024-01-20,Mouse,Electronics,3,29.99,C003
```

## Step 1: Load the Data

First, let's load the CSV file into CSV Editor:

```python
# Load the CSV file
result = load_csv(file_path="/path/to/sales_data.csv")

# The result contains:
# - session_id: Unique identifier for this session
# - row_count: Number of rows loaded
# - column_count: Number of columns
# - columns: List of column names
```

**Expected Output:**
```json
{
  "session_id": "abc123",
  "row_count": 9,
  "column_count": 6,
  "columns": ["date", "product", "category", "quantity", "price", "customer_id"]
}
```

## Step 2: Explore the Data

Let's get basic statistics about our dataset:

```python
# Get statistical summary
stats = get_statistics(session_id="abc123")

# Get value counts for categories
categories = get_value_counts(
    session_id="abc123",
    column="category"
)
```

**Statistics Output:**
```json
{
  "quantity": {
    "count": 8,
    "mean": 2.625,
    "std": 1.302,
    "min": 1,
    "max": 5
  },
  "price": {
    "count": 9,
    "mean": 454.43,
    "std": 498.12,
    "min": 29.99,
    "max": 1299.99
  }
}
```

## Step 3: Clean the Data

Notice we have missing values? Let's fix them:

```python
# Fill missing quantity with median
fill_missing_values(
    session_id="abc123",
    strategy="median",
    columns=["quantity"]
)

# Fill missing customer_id with "UNKNOWN"
fill_missing_values(
    session_id="abc123",
    strategy="fill",
    columns=["customer_id"],
    fill_value="UNKNOWN"
)
```

## Step 4: Transform the Data

Let's add a calculated column for total sales:

```python
# Add total_sales column (quantity * price)
add_column(
    session_id="abc123",
    name="total_sales",
    formula="quantity * price"
)

# Convert date to datetime type
change_column_type(
    session_id="abc123",
    column="date",
    dtype="datetime"
)
```

## Step 5: Filter and Sort

Let's find high-value transactions:

```python
# Filter for sales over $500
filter_rows(
    session_id="abc123",
    conditions=[
        {"column": "total_sales", "operator": ">", "value": 500}
    ]
)

# Sort by total_sales descending
sort_data(
    session_id="abc123",
    columns=["total_sales"],
    ascending=[False]
)
```

## Step 6: Analyze

Perform aggregation by category:

```python
# Group by category and calculate totals
analysis = group_by_aggregate(
    session_id="abc123",
    group_by=["category"],
    aggregations={
        "quantity": ["sum", "mean"],
        "total_sales": ["sum", "mean"],
        "product": "count"
    }
)
```

**Aggregation Result:**
```json
{
  "data": [
    {
      "category": "Electronics",
      "quantity_sum": 13,
      "quantity_mean": 2.6,
      "total_sales_sum": 4919.92,
      "total_sales_mean": 983.98,
      "product_count": 5
    },
    {
      "category": "Furniture",
      "quantity_sum": 8,
      "quantity_mean": 2.67,
      "total_sales_sum": 1049.94,
      "total_sales_mean": 349.98,
      "product_count": 3
    }
  ]
}
```

## Step 7: Validate Quality

Check the data quality:

```python
# Check overall data quality
quality = check_data_quality(session_id="abc123")

# Validate against schema
schema = {
    "date": {"type": "datetime", "required": True},
    "product": {"type": "string", "required": True},
    "category": {"type": "string", "required": True},
    "quantity": {"type": "integer", "min": 0},
    "price": {"type": "float", "min": 0},
    "customer_id": {"type": "string", "required": True}
}

validation = validate_schema(
    session_id="abc123",
    schema=schema
)
```

## Step 8: Export Results

Finally, export the cleaned and processed data:

```python
# Export as Excel with formatting
export_csv(
    session_id="abc123",
    file_path="/path/to/processed_sales.xlsx",
    format="excel"
)

# Export summary as JSON
export_csv(
    session_id="abc123",
    file_path="/path/to/sales_summary.json",
    format="json"
)
```

## Complete Workflow Example

Here's the entire workflow as a single script:

```python
# 1. Load data
session = load_csv("/path/to/sales_data.csv")
sid = session["session_id"]

# 2. Clean missing values
fill_missing_values(sid, strategy="median", columns=["quantity"])
fill_missing_values(sid, strategy="fill", columns=["customer_id"], fill_value="UNKNOWN")

# 3. Add calculated columns
add_column(sid, name="total_sales", formula="quantity * price")
change_column_type(sid, column="date", dtype="datetime")

# 4. Analyze by category
analysis = group_by_aggregate(
    sid,
    group_by=["category"],
    aggregations={
        "total_sales": ["sum", "mean"],
        "quantity": "sum"
    }
)

# 5. Find high-value transactions
filter_rows(sid, conditions=[
    {"column": "total_sales", "operator": ">", "value": 500}
])

# 6. Export results
export_csv(sid, "/path/to/results.xlsx", format="excel")

# 7. Clean up
close_session(sid)
```

## Using Auto-Save

Enable auto-save to never lose your work:

```python
# Configure auto-save with backup strategy
configure_auto_save(
    session_id="abc123",
    enabled=True,
    strategy="backup",
    backup_dir="/path/to/backups",
    max_backups=5
)

# Now all operations are automatically saved!
```

## Using History

Track and undo operations:

```python
# View operation history
history = get_history(session_id="abc123")

# Undo last operation
undo(session_id="abc123")

# Redo if needed
redo(session_id="abc123")

# Restore to specific point
restore_to_operation(
    session_id="abc123",
    operation_id="op_5"
)
```

## Tips for Success

1. **Start Simple**: Begin with basic operations before complex transformations
2. **Check Your Data**: Use `get_session_info()` frequently to understand your data state
3. **Save Often**: Enable auto-save for important data
4. **Validate Early**: Check data quality before extensive processing
5. **Use Appropriate Types**: Convert columns to correct types for better performance

## Common Use Cases

### Data Cleaning Pipeline
```python
# Remove duplicates → Fill missing → Fix types → Validate
remove_duplicates(sid)
fill_missing_values(sid, strategy="mean")
change_column_type(sid, column="date", dtype="datetime")
check_data_quality(sid)
```

### Quick Analysis
```python
# Stats → Correlations → Outliers → Profile
get_statistics(sid)
get_correlation_matrix(sid)
detect_outliers(sid, method="iqr")
profile_data(sid)
```

### Export Multiple Formats
```python
# Same data, different formats for different uses
export_csv(sid, "report.xlsx", format="excel")  # For business users
export_csv(sid, "data.parquet", format="parquet")  # For data warehouse
export_csv(sid, "api_response.json", format="json")  # For API
```

## Next Steps

Congratulations! You've learned the basics of CSV Editor. Continue with:

- [Advanced Filtering](./advanced-filtering) - Complex multi-condition filters
- [Data Transformation](./data-transformation) - Advanced column operations
- [Statistical Analysis](./statistical-analysis) - In-depth analytics
- [API Reference](../api/overview) - Complete tool documentation

## Need Help?

- Check the [API Reference](../api/overview) for detailed tool documentation
- Visit [GitHub Discussions](https://github.com/santoshray02/csv-editor/discussions) for community support
- Report issues on [GitHub Issues](https://github.com/santoshray02/csv-editor/issues)