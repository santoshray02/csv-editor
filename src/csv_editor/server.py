"""Main FastMCP server for CSV Editor."""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from fastmcp import FastMCP, Context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("CSV Editor")

# Import our models
from .models import get_session_manager, OperationResult

# ============================================================================
# HEALTH AND INFO TOOLS
# ============================================================================

@mcp.tool
async def health_check(ctx: Context) -> Dict[str, Any]:
    """Check the health status of the CSV Editor."""
    session_manager = get_session_manager()
    
    try:
        active_sessions = len(session_manager.sessions)
        
        if ctx:
            await ctx.info("Health check performed successfully")
        
        return {
            "success": True,
            "status": "healthy",
            "version": "1.0.0",
            "active_sessions": active_sessions,
            "max_sessions": session_manager.max_sessions,
            "session_ttl_minutes": session_manager.ttl_minutes,
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Health check failed: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }


@mcp.tool
async def get_server_info(ctx: Context) -> Dict[str, Any]:
    """Get information about the CSV Editor capabilities."""
    if ctx:
        await ctx.info("Server information requested")
    
    return {
        "name": "CSV Editor",
        "version": "1.0.0",
        "description": "A comprehensive MCP server for CSV file operations and data analysis",
        "capabilities": {
            "data_io": [
                "load_csv", "load_csv_from_url", "load_csv_from_content",
                "export_csv", "multiple_export_formats"
            ],
            "data_manipulation": [
                "filter_rows", "sort_data", "select_columns", "rename_columns",
                "add_column", "remove_columns", "change_column_type",
                "fill_missing_values", "remove_duplicates"
            ],
            "data_analysis": [
                "get_statistics", "correlation_matrix", "group_by_aggregate",
                "value_counts", "detect_outliers", "profile_data"
            ],
            "data_validation": [
                "validate_schema", "check_data_quality", "find_anomalies"
            ],
            "session_management": [
                "multi_session_support", "session_isolation", "auto_cleanup"
            ]
        },
        "supported_formats": ["csv", "tsv", "json", "excel", "parquet", "html", "markdown"],
        "max_file_size_mb": int(os.getenv("CSV_MAX_FILE_SIZE", "1024")),
        "session_timeout_minutes": int(os.getenv("CSV_SESSION_TIMEOUT", "60"))
    }


# ============================================================================
# DATA I/O TOOLS
# ============================================================================

from .tools.io_operations import (
    load_csv as _load_csv,
    load_csv_from_url as _load_csv_from_url,
    load_csv_from_content as _load_csv_from_content,
    export_csv as _export_csv,
    get_session_info as _get_session_info,
    list_sessions as _list_sessions,
    close_session as _close_session
)

# Register I/O tools with decorators
@mcp.tool
async def load_csv(
    file_path: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load a CSV file into a session."""
    return await _load_csv(file_path, encoding, delimiter, session_id, ctx=ctx)


@mcp.tool
async def load_csv_from_url(
    url: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load a CSV file from a URL."""
    return await _load_csv_from_url(url, encoding, delimiter, session_id, ctx)


@mcp.tool
async def load_csv_from_content(
    content: str,
    delimiter: str = ",",
    session_id: Optional[str] = None,
    has_header: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """Load CSV data from string content."""
    return await _load_csv_from_content(content, delimiter, session_id, has_header, ctx)


@mcp.tool
async def export_csv(
    session_id: str,
    file_path: Optional[str] = None,
    format: str = "csv",
    encoding: str = "utf-8",
    index: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """Export session data to various formats."""
    from .models import ExportFormat
    format_enum = ExportFormat(format)
    return await _export_csv(session_id, file_path, format_enum, encoding, index, ctx)


@mcp.tool
async def get_session_info(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get information about a specific session."""
    return await _get_session_info(session_id, ctx)


@mcp.tool
async def list_sessions(ctx: Context = None) -> Dict[str, Any]:
    """List all active sessions."""
    return await _list_sessions(ctx)


@mcp.tool
async def close_session(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Close and clean up a session."""
    return await _close_session(session_id, ctx)


# ============================================================================
# DATA TRANSFORMATION TOOLS
# ============================================================================

from .tools.transformations import (
    filter_rows as _filter_rows,
    sort_data as _sort_data,
    select_columns as _select_columns,
    rename_columns as _rename_columns,
    add_column as _add_column,
    remove_columns as _remove_columns,
    change_column_type as _change_column_type,
    fill_missing_values as _fill_missing_values,
    remove_duplicates as _remove_duplicates,
    update_column as _update_column
)

@mcp.tool
async def filter_rows(
    session_id: str,
    conditions: List[Dict[str, Any]],
    mode: str = "and",
    ctx: Context = None
) -> Dict[str, Any]:
    """Filter rows based on conditions."""
    return await _filter_rows(session_id, conditions, mode, ctx)

@mcp.tool
async def sort_data(
    session_id: str,
    columns: List[Any],
    ctx: Context = None
) -> Dict[str, Any]:
    """Sort data by columns."""
    return await _sort_data(session_id, columns, ctx)

@mcp.tool
async def select_columns(
    session_id: str,
    columns: List[str],
    ctx: Context = None
) -> Dict[str, Any]:
    """Select specific columns from the dataframe."""
    return await _select_columns(session_id, columns, ctx)

@mcp.tool
async def rename_columns(
    session_id: str,
    mapping: Dict[str, str],
    ctx: Context = None
) -> Dict[str, Any]:
    """Rename columns in the dataframe."""
    return await _rename_columns(session_id, mapping, ctx)

@mcp.tool
async def add_column(
    session_id: str,
    name: str,
    value: Any = None,
    formula: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Add a new column to the dataframe."""
    return await _add_column(session_id, name, value, formula, ctx)

@mcp.tool
async def remove_columns(
    session_id: str,
    columns: List[str],
    ctx: Context = None
) -> Dict[str, Any]:
    """Remove columns from the dataframe."""
    return await _remove_columns(session_id, columns, ctx)

@mcp.tool
async def change_column_type(
    session_id: str,
    column: str,
    dtype: str,
    errors: str = "coerce",
    ctx: Context = None
) -> Dict[str, Any]:
    """Change the data type of a column."""
    return await _change_column_type(session_id, column, dtype, errors, ctx)

@mcp.tool
async def fill_missing_values(
    session_id: str,
    strategy: str = "drop",
    value: Any = None,
    columns: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Fill or remove missing values."""
    return await _fill_missing_values(session_id, strategy, value, columns, ctx)

@mcp.tool
async def remove_duplicates(
    session_id: str,
    subset: Optional[List[str]] = None,
    keep: str = "first",
    ctx: Context = None
) -> Dict[str, Any]:
    """Remove duplicate rows."""
    return await _remove_duplicates(session_id, subset, keep, ctx)

@mcp.tool
async def update_column(
    session_id: str,
    column: str,
    operation: str,
    value: Optional[Any] = None,
    pattern: Optional[str] = None,
    replacement: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Update values in a specific column with simple operations like replace, extract, split, etc."""
    return await _update_column(session_id, column, operation, value, pattern, replacement, ctx)

# ============================================================================
# DATA ANALYTICS TOOLS
# ============================================================================

from .tools.analytics import (
    get_statistics as _get_statistics,
    get_column_statistics as _get_column_statistics,
    get_correlation_matrix as _get_correlation_matrix,
    group_by_aggregate as _group_by_aggregate,
    get_value_counts as _get_value_counts,
    detect_outliers as _detect_outliers,
    profile_data as _profile_data
)

@mcp.tool
async def get_statistics(
    session_id: str,
    columns: Optional[List[str]] = None,
    include_percentiles: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get statistical summary of numerical columns."""
    return await _get_statistics(session_id, columns, include_percentiles, ctx)

@mcp.tool
async def get_column_statistics(
    session_id: str,
    column: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get detailed statistics for a specific column."""
    return await _get_column_statistics(session_id, column, ctx)

@mcp.tool
async def get_correlation_matrix(
    session_id: str,
    method: str = "pearson",
    columns: Optional[List[str]] = None,
    min_correlation: Optional[float] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Calculate correlation matrix for numeric columns."""
    return await _get_correlation_matrix(session_id, method, columns, min_correlation, ctx)

@mcp.tool
async def group_by_aggregate(
    session_id: str,
    group_by: List[str],
    aggregations: Dict[str, Any],
    ctx: Context = None
) -> Dict[str, Any]:
    """Group data and apply aggregation functions."""
    return await _group_by_aggregate(session_id, group_by, aggregations, ctx)

@mcp.tool
async def get_value_counts(
    session_id: str,
    column: str,
    normalize: bool = False,
    sort: bool = True,
    ascending: bool = False,
    top_n: Optional[int] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get value counts for a column."""
    return await _get_value_counts(session_id, column, normalize, sort, ascending, top_n, ctx)

@mcp.tool
async def detect_outliers(
    session_id: str,
    columns: Optional[List[str]] = None,
    method: str = "iqr",
    threshold: float = 1.5,
    ctx: Context = None
) -> Dict[str, Any]:
    """Detect outliers in numeric columns."""
    return await _detect_outliers(session_id, columns, method, threshold, ctx)

@mcp.tool
async def profile_data(
    session_id: str,
    include_correlations: bool = True,
    include_outliers: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """Generate comprehensive data profile."""
    return await _profile_data(session_id, include_correlations, include_outliers, ctx)

# ============================================================================
# DATA VALIDATION TOOLS  
# ============================================================================

from .tools.validation import (
    validate_schema as _validate_schema,
    check_data_quality as _check_data_quality,
    find_anomalies as _find_anomalies
)

@mcp.tool
async def validate_schema(
    session_id: str,
    schema: Dict[str, Dict[str, Any]],
    ctx: Context = None
) -> Dict[str, Any]:
    """Validate data against a schema definition."""
    return await _validate_schema(session_id, schema, ctx)

@mcp.tool
async def check_data_quality(
    session_id: str,
    rules: Optional[List[Dict[str, Any]]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Check data quality based on predefined or custom rules."""
    return await _check_data_quality(session_id, rules, ctx)

@mcp.tool
async def find_anomalies(
    session_id: str,
    columns: Optional[List[str]] = None,
    sensitivity: float = 0.95,
    methods: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Find anomalies in the data using multiple detection methods."""
    return await _find_anomalies(session_id, columns, sensitivity, methods, ctx)


# ============================================================================
# AUTO-SAVE TOOLS
# ============================================================================

from .tools.auto_save_operations import (
    configure_auto_save as _configure_auto_save,
    disable_auto_save as _disable_auto_save,
    get_auto_save_status as _get_auto_save_status,
    trigger_manual_save as _trigger_manual_save
)

@mcp.tool
async def configure_auto_save(
    session_id: str,
    enabled: bool = True,
    mode: str = "after_operation",
    strategy: str = "backup",
    interval_seconds: Optional[int] = None,
    max_backups: Optional[int] = None,
    backup_dir: Optional[str] = None,
    custom_path: Optional[str] = None,
    format: str = "csv",
    encoding: str = "utf-8",
    ctx: Context = None
) -> Dict[str, Any]:
    """Configure auto-save settings for a session."""
    return await _configure_auto_save(
        session_id, enabled, mode, strategy, interval_seconds,
        max_backups, backup_dir, custom_path, format, encoding, ctx
    )

@mcp.tool
async def disable_auto_save(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Disable auto-save for a session."""
    return await _disable_auto_save(session_id, ctx)

@mcp.tool
async def get_auto_save_status(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get auto-save status for a session."""
    return await _get_auto_save_status(session_id, ctx)

@mcp.tool
async def trigger_manual_save(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Manually trigger a save for a session."""
    return await _trigger_manual_save(session_id, ctx)


# ============================================================================
# HISTORY OPERATIONS
# ============================================================================

from .tools.history_operations import (
    undo_operation as _undo_operation,
    redo_operation as _redo_operation,
    get_operation_history as _get_operation_history,
    restore_to_operation as _restore_to_operation,
    clear_history as _clear_history,
    export_history as _export_history
)

@mcp.tool
async def undo(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Undo the last operation in a session."""
    return await _undo_operation(session_id, ctx)

@mcp.tool
async def redo(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Redo a previously undone operation."""
    return await _redo_operation(session_id, ctx)

@mcp.tool
async def get_history(
    session_id: str,
    limit: Optional[int] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get operation history for a session."""
    return await _get_operation_history(session_id, limit, ctx)

@mcp.tool
async def restore_to_operation(
    session_id: str,
    operation_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Restore session data to a specific operation point."""
    return await _restore_to_operation(session_id, operation_id, ctx)

@mcp.tool
async def clear_history(
    session_id: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Clear all operation history for a session."""
    return await _clear_history(session_id, ctx)

@mcp.tool
async def export_history(
    session_id: str,
    file_path: str,
    format: str = "json",
    ctx: Context = None
) -> Dict[str, Any]:
    """Export operation history to a file."""
    return await _export_history(session_id, file_path, format, ctx)


# ============================================================================
# RESOURCES
# ============================================================================

@mcp.resource("csv://{session_id}/data")
async def get_csv_data(session_id: str) -> Dict[str, Any]:
    """Get current CSV data from a session."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}
    
    return {
        "session_id": session_id,
        "data": session.df.to_dict('records'),
        "shape": session.df.shape
    }


@mcp.resource("csv://{session_id}/schema")
async def get_csv_schema(session_id: str) -> Dict[str, Any]:
    """Get CSV schema information."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}
    
    return {
        "session_id": session_id,
        "columns": session.df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in session.df.dtypes.items()},
        "shape": session.df.shape
    }


@mcp.resource("sessions://active")
async def list_active_sessions() -> List[Dict[str, Any]]:
    """List all active CSV sessions."""
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions()
    return [s.dict() for s in sessions]


# ============================================================================
# PROMPTS
# ============================================================================

@mcp.prompt
def analyze_csv_prompt(session_id: str, analysis_type: str = "summary") -> str:
    """Generate a prompt to analyze CSV data."""
    return f"""Please analyze the CSV data in session {session_id}.
    
Analysis type: {analysis_type}

Provide insights about:
1. Data quality and completeness
2. Statistical patterns
3. Potential issues or anomalies
4. Recommended transformations or cleanups
"""


@mcp.prompt  
def data_cleaning_prompt(session_id: str) -> str:
    """Generate a prompt for data cleaning suggestions."""
    return f"""Review the data in session {session_id} and suggest cleaning operations.

Consider:
- Missing values and how to handle them
- Duplicate rows
- Data type conversions needed
- Outliers that may need attention
- Column naming conventions
"""


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CSV Editor")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport method"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP/SSE transport"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE transport"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info(f"Starting CSV Editor with {args.transport} transport")
    
    # Run the server
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(
            transport=args.transport,
            host=args.host,
            port=args.port
        )


if __name__ == "__main__":
    main()