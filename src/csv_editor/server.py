"""Main FastMCP server for CSV Editor."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context, FastMCP

# Local imports
from .models import get_session_manager
from .tools.analytics import (
    detect_outliers as _detect_outliers,
)
from .tools.analytics import (
    get_column_statistics as _get_column_statistics,
)
from .tools.analytics import (
    get_correlation_matrix as _get_correlation_matrix,
)
from .tools.analytics import (
    get_statistics as _get_statistics,
)
from .tools.analytics import (
    get_value_counts as _get_value_counts,
)
from .tools.analytics import (
    group_by_aggregate as _group_by_aggregate,
)
from .tools.analytics import (
    profile_data as _profile_data,
)
from .tools.auto_save_operations import (
    configure_auto_save as _configure_auto_save,
)
from .tools.auto_save_operations import (
    disable_auto_save as _disable_auto_save,
)
from .tools.auto_save_operations import (
    get_auto_save_status as _get_auto_save_status,
)
from .tools.auto_save_operations import (
    trigger_manual_save as _trigger_manual_save,
)
from .tools.history_operations import (
    clear_history as _clear_history,
)
from .tools.history_operations import (
    export_history as _export_history,
)
from .tools.history_operations import (
    get_operation_history as _get_operation_history,
)
from .tools.history_operations import (
    redo_operation as _redo_operation,
)
from .tools.history_operations import (
    restore_to_operation as _restore_to_operation,
)
from .tools.history_operations import (
    undo_operation as _undo_operation,
)
from .tools.io_operations import (
    close_session as _close_session,
)
from .tools.io_operations import (
    export_csv as _export_csv,
)
from .tools.io_operations import (
    get_session_info as _get_session_info,
)
from .tools.io_operations import (
    list_sessions as _list_sessions,
)
from .tools.io_operations import (
    load_csv as _load_csv,
)
from .tools.io_operations import (
    load_csv_from_content as _load_csv_from_content,
)
from .tools.io_operations import (
    load_csv_from_url as _load_csv_from_url,
)
from .tools.transformations import (
    add_column as _add_column,
)
from .tools.transformations import (
    change_column_type as _change_column_type,
)
from .tools.transformations import (
    fill_missing_values as _fill_missing_values,
)
from .tools.transformations import (
    filter_rows as _filter_rows,
)
from .tools.transformations import (
    remove_columns as _remove_columns,
)
from .tools.transformations import (
    remove_duplicates as _remove_duplicates,
)
from .tools.transformations import (
    rename_columns as _rename_columns,
)
from .tools.transformations import (
    select_columns as _select_columns,
)
from .tools.transformations import (
    sort_data as _sort_data,
)
from .tools.transformations import (
    update_column as _update_column,
)
from .tools.validation import (
    check_data_quality as _check_data_quality,
)
from .tools.validation import (
    find_anomalies as _find_anomalies,
)
from .tools.validation import (
    validate_schema as _validate_schema,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_instructions() -> str:
    """Load instructions from the markdown file."""
    instructions_path = Path(__file__).parent / "instructions.md"
    try:
        return instructions_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Instructions file not found at {instructions_path}")
        return "CSV Editor MCP Server - Instructions file not available"
    except Exception as e:
        logger.error(f"Error loading instructions: {e}")
        return "CSV Editor MCP Server - Error loading instructions"


# Initialize FastMCP server
mcp = FastMCP("CSV Editor", instructions=_load_instructions())


# ============================================================================
# HEALTH AND INFO TOOLS
# ============================================================================


@mcp.tool
async def health_check(ctx: Context) -> dict[str, Any]:
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
            await ctx.error(f"Health check failed: {e!s}")
        return {"success": False, "status": "error", "error": str(e)}


@mcp.tool
async def get_server_info(ctx: Context) -> dict[str, Any]:
    """Get information about the CSV Editor capabilities."""
    if ctx:
        await ctx.info("Server information requested")

    return {
        "name": "CSV Editor",
        "version": "1.0.0",
        "description": "A comprehensive MCP server for CSV file operations and data analysis",
        "capabilities": {
            "data_io": [
                "load_csv",
                "load_csv_from_url",
                "load_csv_from_content",
                "export_csv",
                "multiple_export_formats",
            ],
            "data_manipulation": [
                "filter_rows",
                "sort_data",
                "select_columns",
                "rename_columns",
                "add_column",
                "remove_columns",
                "change_column_type",
                "fill_missing_values",
                "remove_duplicates",
            ],
            "data_analysis": [
                "get_statistics",
                "correlation_matrix",
                "group_by_aggregate",
                "value_counts",
                "detect_outliers",
                "profile_data",
            ],
            "data_validation": ["validate_schema", "check_data_quality", "find_anomalies"],
            "session_management": ["multi_session_support", "session_isolation", "auto_cleanup"],
        },
        "supported_formats": ["csv", "tsv", "json", "excel", "parquet", "html", "markdown"],
        "max_file_size_mb": int(os.getenv("CSV_MAX_FILE_SIZE", "1024")),
        "session_timeout_minutes": int(os.getenv("CSV_SESSION_TIMEOUT", "60")),
    }


# ============================================================================
# DATA I/O TOOLS
# ============================================================================


# Register I/O tools with decorators
@mcp.tool
async def load_csv(
    file_path: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load a CSV file into a session."""
    return await _load_csv(file_path, encoding, delimiter, session_id, ctx=ctx)


@mcp.tool
async def load_csv_from_url(
    url: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load a CSV file from a URL."""
    return await _load_csv_from_url(url, encoding, delimiter, session_id, ctx)


@mcp.tool
async def load_csv_from_content(
    content: str,
    delimiter: str = ",",
    session_id: str | None = None,
    has_header: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load CSV data from string content."""
    return await _load_csv_from_content(content, delimiter, session_id, has_header, ctx)


@mcp.tool
async def export_csv(
    session_id: str,
    file_path: str | None = None,
    format: str = "csv",
    encoding: str = "utf-8",
    index: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Export session data to various formats."""
    from .models import ExportFormat

    format_enum = ExportFormat(format)
    return await _export_csv(session_id, file_path, format_enum, encoding, index, ctx)


@mcp.tool
async def get_session_info(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Get information about a specific session."""
    return await _get_session_info(session_id, ctx)


@mcp.tool
async def list_sessions(ctx: Context | None = None) -> dict[str, Any]:
    """List all active sessions."""
    return await _list_sessions(ctx)


@mcp.tool
async def close_session(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Close and clean up a session."""
    return await _close_session(session_id, ctx)


# ============================================================================
# DATA TRANSFORMATION TOOLS
# ============================================================================


@mcp.tool
async def filter_rows(
    session_id: str, conditions: list[dict[str, Any]], mode: str = "and", ctx: Context | None = None
) -> dict[str, Any]:
    """Filter rows based on conditions."""
    return await _filter_rows(session_id, conditions, mode, ctx)


@mcp.tool
async def sort_data(
    session_id: str, columns: list[Any], ctx: Context | None = None
) -> dict[str, Any]:
    """Sort data by columns."""
    return await _sort_data(session_id, columns, ctx)


@mcp.tool
async def select_columns(
    session_id: str, columns: list[str], ctx: Context | None = None
) -> dict[str, Any]:
    """Select specific columns from the dataframe."""
    return await _select_columns(session_id, columns, ctx)


@mcp.tool
async def rename_columns(
    session_id: str, mapping: dict[str, str], ctx: Context | None = None
) -> dict[str, Any]:
    """Rename columns in the dataframe."""
    return await _rename_columns(session_id, mapping, ctx)


@mcp.tool
async def add_column(
    session_id: str,
    name: str,
    value: Any = None,
    formula: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Add a new column to the dataframe."""
    return await _add_column(session_id, name, value, formula, ctx)


@mcp.tool
async def remove_columns(
    session_id: str, columns: list[str], ctx: Context | None = None
) -> dict[str, Any]:
    """Remove columns from the dataframe."""
    return await _remove_columns(session_id, columns, ctx)


@mcp.tool
async def change_column_type(
    session_id: str,
    column: str,
    dtype: str,
    errors: Literal["raise", "coerce"] = "coerce",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Change the data type of a column."""
    return await _change_column_type(session_id, column, dtype, errors, ctx)


@mcp.tool
async def fill_missing_values(
    session_id: str,
    strategy: str = "drop",
    value: Any = None,
    columns: list[str] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Fill or remove missing values."""
    return await _fill_missing_values(session_id, strategy, value, columns, ctx)


@mcp.tool
async def remove_duplicates(
    session_id: str,
    subset: list[str] | None = None,
    keep: Literal["first", "last", "none"] = "first",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Remove duplicate rows."""
    return await _remove_duplicates(session_id, subset, keep, ctx)


@mcp.tool
async def update_column(
    session_id: str,
    column: str,
    operation: str,
    value: Any | None = None,
    pattern: str | None = None,
    replacement: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Update values in a specific column with simple operations like replace, extract, split, etc."""
    return await _update_column(session_id, column, operation, value, pattern, replacement, ctx)


# ============================================================================
# DATA ANALYTICS TOOLS
# ============================================================================


@mcp.tool
async def get_statistics(
    session_id: str,
    columns: list[str] | None = None,
    include_percentiles: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get statistical summary of numerical columns."""
    return await _get_statistics(session_id, columns, include_percentiles, ctx)


@mcp.tool
async def get_column_statistics(
    session_id: str, column: str, ctx: Context | None = None
) -> dict[str, Any]:
    """Get detailed statistics for a specific column."""
    return await _get_column_statistics(session_id, column, ctx)


@mcp.tool
async def get_correlation_matrix(
    session_id: str,
    method: Literal["pearson", "spearman", "kendall"] = "pearson",
    columns: list[str] | None = None,
    min_correlation: float | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Calculate correlation matrix for numeric columns."""
    return await _get_correlation_matrix(session_id, method, columns, min_correlation, ctx)


@mcp.tool
async def group_by_aggregate(
    session_id: str, group_by: list[str], aggregations: dict[str, Any], ctx: Context | None = None
) -> dict[str, Any]:
    """Group data and apply aggregation functions."""
    return await _group_by_aggregate(session_id, group_by, aggregations, ctx)


@mcp.tool
async def get_value_counts(
    session_id: str,
    column: str,
    normalize: bool = False,
    sort: bool = True,
    ascending: bool = False,
    top_n: int | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get value counts for a column."""
    return await _get_value_counts(session_id, column, normalize, sort, ascending, top_n, ctx)


@mcp.tool
async def detect_outliers(
    session_id: str,
    columns: list[str] | None = None,
    method: str = "iqr",
    threshold: float = 1.5,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Detect outliers in numeric columns."""
    return await _detect_outliers(session_id, columns, method, threshold, ctx)


@mcp.tool
async def profile_data(
    session_id: str,
    include_correlations: bool = True,
    include_outliers: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Generate comprehensive data profile."""
    return await _profile_data(session_id, include_correlations, include_outliers, ctx)


# ============================================================================
# DATA VALIDATION TOOLS
# ============================================================================


@mcp.tool
async def validate_schema(
    session_id: str, schema: dict[str, dict[str, Any]], ctx: Context | None = None
) -> dict[str, Any]:
    """Validate data against a schema definition."""
    return await _validate_schema(session_id, schema, ctx)


@mcp.tool
async def check_data_quality(
    session_id: str, rules: list[dict[str, Any]] | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """Check data quality based on predefined or custom rules."""
    return await _check_data_quality(session_id, rules, ctx)


@mcp.tool
async def find_anomalies(
    session_id: str,
    columns: list[str] | None = None,
    sensitivity: float = 0.95,
    methods: list[str] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Find anomalies in the data using multiple detection methods."""
    return await _find_anomalies(session_id, columns, sensitivity, methods, ctx)


# ============================================================================
# AUTO-SAVE TOOLS
# ============================================================================


@mcp.tool
async def configure_auto_save(
    session_id: str,
    enabled: bool = True,
    mode: str = "after_operation",
    strategy: str = "backup",
    interval_seconds: int | None = None,
    max_backups: int | None = None,
    backup_dir: str | None = None,
    custom_path: str | None = None,
    format: str = "csv",
    encoding: str = "utf-8",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Configure auto-save settings for a session."""
    return await _configure_auto_save(
        session_id,
        enabled,
        mode,
        strategy,
        interval_seconds,
        max_backups,
        backup_dir,
        custom_path,
        format,
        encoding,
        ctx,
    )


@mcp.tool
async def disable_auto_save(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Disable auto-save for a session."""
    return await _disable_auto_save(session_id, ctx)


@mcp.tool
async def get_auto_save_status(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Get auto-save status for a session."""
    return await _get_auto_save_status(session_id, ctx)


@mcp.tool
async def trigger_manual_save(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Manually trigger a save for a session."""
    return await _trigger_manual_save(session_id, ctx)


# ============================================================================
# HISTORY OPERATIONS
# ============================================================================


@mcp.tool
async def undo(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Undo the last operation in a session."""
    return await _undo_operation(session_id, ctx)


@mcp.tool
async def redo(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Redo a previously undone operation."""
    return await _redo_operation(session_id, ctx)


@mcp.tool
async def get_history(
    session_id: str, limit: int | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """Get operation history for a session."""
    return await _get_operation_history(session_id, limit, ctx)


@mcp.tool
async def restore_to_operation(
    session_id: str, operation_id: str, ctx: Context | None = None
) -> dict[str, Any]:
    """Restore session data to a specific operation point."""
    return await _restore_to_operation(session_id, operation_id, ctx)


@mcp.tool
async def clear_history(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Clear all operation history for a session."""
    return await _clear_history(session_id, ctx)


@mcp.tool
async def export_history(
    session_id: str, file_path: str, format: str = "json", ctx: Context | None = None
) -> dict[str, Any]:
    """Export operation history to a file."""
    return await _export_history(session_id, file_path, format, ctx)


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("csv://{session_id}/data")
async def get_csv_data(session_id: str) -> dict[str, Any]:
    """Get current CSV data from a session."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    return {
        "session_id": session_id,
        "data": session.df.to_dict("records"),
        "shape": session.df.shape,
    }


@mcp.resource("csv://{session_id}/schema")
async def get_csv_schema(session_id: str) -> dict[str, Any]:
    """Get CSV schema information."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    return {
        "session_id": session_id,
        "columns": session.df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in session.df.dtypes.items()},
        "shape": session.df.shape,
    }


@mcp.resource("sessions://active")
async def list_active_sessions() -> list[dict[str, Any]]:
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


def main() -> None:
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="CSV Editor")
    parser.add_argument(
        "--transport", choices=["stdio", "http", "sse"], default="stdio", help="Transport method"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP/SSE transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP/SSE transport")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info(f"Starting CSV Editor with {args.transport} transport")

    # Run the server
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
