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
    _create_data_preview_with_indices,
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
    delete_row as _delete_row,
)
from .tools.transformations import (
    extract_from_column as _extract_from_column,
)
from .tools.transformations import (
    fill_column_nulls as _fill_column_nulls,
)
from .tools.transformations import (
    fill_missing_values as _fill_missing_values,
)
from .tools.transformations import (
    filter_rows as _filter_rows,
)
from .tools.transformations import (
    find_cells_with_value as _find_cells_with_value,
)
from .tools.transformations import (
    get_cell_value as _get_cell_value,
)
from .tools.transformations import (
    get_column_data as _get_column_data,
)
from .tools.transformations import (
    get_data_summary as _get_data_summary,
)
from .tools.transformations import (
    get_row_data as _get_row_data,
)
from .tools.transformations import (
    insert_row as _insert_row,
)
from .tools.transformations import (
    inspect_data_around as _inspect_data_around,
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
    replace_in_column as _replace_in_column,
)
from .tools.transformations import (
    select_columns as _select_columns,
)
from .tools.transformations import (
    set_cell_value as _set_cell_value,
)
from .tools.transformations import (
    sort_data as _sort_data,
)
from .tools.transformations import (
    split_column as _split_column,
)
from .tools.transformations import (
    strip_column as _strip_column,
)
from .tools.transformations import (
    transform_column_case as _transform_column_case,
)
from .tools.transformations import (
    update_column as _update_column,
)
from .tools.transformations import (
    update_row as _update_row,
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
# CELL-LEVEL AND ROW-LEVEL ACCESS TOOLS
# ============================================================================


@mcp.tool
async def get_cell_value(
    session_id: str, row_index: int, column: str | int, ctx: Context | None = None
) -> dict[str, Any]:
    """Get the value of a specific cell by row index and column name/index.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        column: Column name (str) or column index (int, 0-based)

    Returns:
        Dict with cell value and coordinates

    Examples:
        get_cell_value("session123", 0, "name") -> Get first row, "name" column
        get_cell_value("session123", 2, 1) -> Get third row, second column
    """
    return await _get_cell_value(session_id, row_index, column, ctx)


@mcp.tool
async def set_cell_value(
    session_id: str, row_index: int, column: str | int, value: Any, ctx: Context | None = None
) -> dict[str, Any]:
    """Set the value of a specific cell by row index and column name/index.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        column: Column name (str) or column index (int, 0-based)
        value: New value for the cell

    Returns:
        Dict with old value, new value, and coordinates

    Examples:
        set_cell_value("session123", 0, "name", "Jane") -> Set first row, "name" column to "Jane"
        set_cell_value("session123", 2, 1, 25) -> Set third row, second column to 25
    """
    return await _set_cell_value(session_id, row_index, column, value, ctx)


@mcp.tool
async def get_row_data(
    session_id: str, row_index: int, columns: list[str] | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """Get data from a specific row, optionally filtered by columns.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        columns: Optional list of column names to include (None for all columns)

    Returns:
        Dict with row data and metadata

    Examples:
        get_row_data("session123", 0) -> Get all data from first row
        get_row_data("session123", 1, ["name", "age"]) -> Get specific columns from second row
    """
    return await _get_row_data(session_id, row_index, columns, ctx)


@mcp.tool
async def get_column_data(
    session_id: str,
    column: str,
    start_row: int | None = None,
    end_row: int | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get data from a specific column, optionally sliced by row range.

    Args:
        session_id: Session identifier
        column: Column name
        start_row: Starting row index (0-based, inclusive). None for beginning
        end_row: Ending row index (0-based, exclusive). None for end

    Returns:
        Dict with column data and metadata

    Examples:
        get_column_data("session123", "age") -> Get all values from "age" column
        get_column_data("session123", "name", 0, 5) -> Get first 5 values from "name" column
    """
    return await _get_column_data(session_id, column, start_row, end_row, ctx)


# ============================================================================
# FOCUSED COLUMN OPERATIONS (Replacing operation-parameter pattern)
# ============================================================================


@mcp.tool
async def replace_in_column(
    session_id: str,
    column: str,
    pattern: str,
    replacement: str,
    regex: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Replace patterns in a column with replacement text.

    Args:
        session_id: Session identifier
        column: Column name to update
        pattern: Pattern to search for (regex or literal string)
        replacement: Replacement string
        regex: Whether to treat pattern as regex (default: True)

    Returns:
        Dict with success status and replacement info

    Examples:
        replace_in_column("session123", "name", r"Mr\\.", "Mister") -> Replace "Mr." with "Mister"
        replace_in_column("session123", "phone", r"\\D", "", True) -> Remove non-digits from phone
    """
    return await _replace_in_column(session_id, column, pattern, replacement, regex, ctx)


@mcp.tool
async def extract_from_column(
    session_id: str, column: str, pattern: str, expand: bool = False, ctx: Context | None = None
) -> dict[str, Any]:
    """Extract patterns from a column using regex.

    Args:
        session_id: Session identifier
        column: Column name to update
        pattern: Regex pattern to extract (use capturing groups)
        expand: Whether to expand to multiple columns if multiple groups

    Returns:
        Dict with success status and extraction info

    Examples:
        extract_from_column("session123", "email", r"(.+)@(.+)") -> Extract username and domain
        extract_from_column("session123", "code", r"([A-Z]{2})-(\\d+)") -> Extract prefix and number
    """
    return await _extract_from_column(session_id, column, pattern, expand, ctx)


@mcp.tool
async def split_column(
    session_id: str,
    column: str,
    delimiter: str = " ",
    part_index: int | None = None,
    expand_to_columns: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Split column values by delimiter.

    Args:
        session_id: Session identifier
        column: Column name to update
        delimiter: String to split on (default: space)
        part_index: Which part to keep (0-based index). None keeps first part
        expand_to_columns: Whether to expand splits into multiple columns

    Returns:
        Dict with success status and split info

    Examples:
        split_column("session123", "name", " ", 0) -> Keep first part of name
        split_column("session123", "full_name", " ", expand_to_columns=True) -> Split into multiple columns
    """
    return await _split_column(session_id, column, delimiter, part_index, expand_to_columns, ctx)


@mcp.tool
async def transform_column_case(
    session_id: str,
    column: str,
    transform: Literal["upper", "lower", "title", "capitalize"],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Transform the case of text in a column.

    Args:
        session_id: Session identifier
        column: Column name to update
        transform: Type of case transformation

    Returns:
        Dict with success status and transformation info

    Examples:
        transform_column_case("session123", "name", "title") -> "john doe" becomes "John Doe"
        transform_column_case("session123", "code", "upper") -> "abc123" becomes "ABC123"
    """
    return await _transform_column_case(session_id, column, transform, ctx)


@mcp.tool
async def strip_column(
    session_id: str, column: str, chars: str | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """Strip whitespace or specified characters from column values.

    Args:
        session_id: Session identifier
        column: Column name to update
        chars: Characters to strip (None for whitespace)

    Returns:
        Dict with success status and strip info

    Examples:
        strip_column("session123", "name") -> Remove leading/trailing whitespace
        strip_column("session123", "code", "()") -> Remove parentheses from ends
    """
    return await _strip_column(session_id, column, chars, ctx)


@mcp.tool
async def fill_column_nulls(
    session_id: str, column: str, value: Any, ctx: Context | None = None
) -> dict[str, Any]:
    """Fill null/NaN values in a column with a specified value.

    Args:
        session_id: Session identifier
        column: Column name to update
        value: Value to use for filling nulls

    Returns:
        Dict with success status and fill info

    Examples:
        fill_column_nulls("session123", "age", 0) -> Replace NaN ages with 0
        fill_column_nulls("session123", "name", "Unknown") -> Replace missing names with "Unknown"
    """
    return await _fill_column_nulls(session_id, column, value, ctx)


# ============================================================================
# ROW MANIPULATION TOOLS
# ============================================================================


@mcp.tool
async def insert_row(
    session_id: str,
    row_index: int,
    data: dict[str, Any] | list[Any],
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Insert a new row at the specified index.

    Args:
        session_id: Session identifier
        row_index: Index where to insert the row (0-based). Use -1 to append at end
        data: Row data as dict (column_name: value) or list of values

    Returns:
        Dict with success status and insertion info

    Examples:
        insert_row("session123", 1, {"name": "Alice", "age": 28, "city": "Boston"})
        insert_row("session123", -1, ["David", 40, "Miami"])  # Append at end
    """
    return await _insert_row(session_id, row_index, data, ctx)


@mcp.tool
async def delete_row(session_id: str, row_index: int, ctx: Context | None = None) -> dict[str, Any]:
    """Delete a row at the specified index.

    Args:
        session_id: Session identifier
        row_index: Row index to delete (0-based)

    Returns:
        Dict with success status and deletion info

    Example:
        delete_row("session123", 1) -> Delete second row
    """
    return await _delete_row(session_id, row_index, ctx)


@mcp.tool
async def update_row(
    session_id: str, row_index: int, data: dict[str, Any], ctx: Context | None = None
) -> dict[str, Any]:
    """Update specific columns in a row with new values.

    Args:
        session_id: Session identifier
        row_index: Row index to update (0-based)
        data: Dict with column names and new values (partial updates allowed)

    Returns:
        Dict with success status and update info

    Example:
        update_row("session123", 0, {"age": 31, "city": "Boston"}) -> Update age and city for first row
    """
    return await _update_row(session_id, row_index, data, ctx)


# ============================================================================
# AI-FRIENDLY CONVENIENCE TOOLS
# ============================================================================


@mcp.tool
async def inspect_data_around(
    session_id: str,
    row: int,
    column: str | int,
    radius: int = 2,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get data around a specific cell for context inspection.

    Args:
        session_id: Session identifier
        row: Center row index (0-based)
        column: Column name (str) or column index (int, 0-based)
        radius: Number of rows/columns around the center to include

    Returns:
        Dict with surrounding data and coordinate information

    Example:
        inspect_data_around("session123", 5, "name", 2) -> Get 5x5 grid centered on (5, "name")
    """
    return await _inspect_data_around(session_id, row, column, radius, ctx)


@mcp.tool
async def find_cells_with_value(
    session_id: str,
    value: Any,
    column: str | None = None,
    exact_match: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Find all cells containing a specific value.

    Args:
        session_id: Session identifier
        value: Value to search for
        column: Optional column name to restrict search (None for all columns)
        exact_match: Whether to use exact matching or substring matching for strings

    Returns:
        Dict with coordinates of matching cells

    Examples:
        find_cells_with_value("session123", "John") -> Find all cells with "John"
        find_cells_with_value("session123", 25, "age") -> Find all age cells with value 25
        find_cells_with_value("session123", "john", None, False) -> Substring search across all columns
    """
    return await _find_cells_with_value(session_id, value, column, exact_match, ctx)


@mcp.tool
async def get_data_summary(
    session_id: str,
    include_preview: bool = True,
    max_preview_rows: int = 10,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get comprehensive data summary optimized for AI understanding.

    Args:
        session_id: Session identifier
        include_preview: Whether to include data preview
        max_preview_rows: Maximum number of rows in preview

    Returns:
        Dict with comprehensive data summary and metadata

    Examples:
        get_data_summary("session123") -> Complete summary with 10-row preview
        get_data_summary("session123", False) -> Summary without preview data
        get_data_summary("session123", True, 5) -> Summary with 5-row preview
    """
    return await _get_data_summary(session_id, include_preview, max_preview_rows, ctx)


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
    """Get current CSV data from a session with enhanced indexing."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    # Use enhanced preview for better AI accessibility
    preview_data = _create_data_preview_with_indices(session.df, 10)

    return {
        "session_id": session_id,
        "shape": session.df.shape,
        "preview": preview_data,
        "columns_info": {
            "columns": session.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in session.df.dtypes.items()},
        },
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


@mcp.resource("csv://{session_id}/cell/{row_index}/{column}")
async def get_csv_cell(session_id: str, row_index: str, column: str) -> dict[str, Any]:
    """Get data for a specific cell with coordinate information."""
    try:
        row_idx = int(row_index)
        # Try to convert column to int if it's numeric
        try:
            col_param: str | int = int(column)
        except ValueError:
            col_param = column

        result = await _get_cell_value(session_id, row_idx, col_param)
        return result
    except ValueError:
        return {"error": "Invalid row index - must be an integer"}


@mcp.resource("csv://{session_id}/row/{row_index}")
async def get_csv_row(session_id: str, row_index: str) -> dict[str, Any]:
    """Get data for a specific row with all column values."""
    try:
        row_idx = int(row_index)
        result = await _get_row_data(session_id, row_idx)
        return result
    except ValueError:
        return {"error": "Invalid row index - must be an integer"}


@mcp.resource("csv://{session_id}/preview")
async def get_csv_preview(session_id: str) -> dict[str, Any]:
    """Get a preview of the CSV data with enhanced indexing and coordinate information."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    preview_data = _create_data_preview_with_indices(session.df, 10)

    return {
        "session_id": session_id,
        "coordinate_system": {
            "description": "Uses 0-based indexing for both rows and columns",
            "row_indexing": "0 to N-1 where N is total rows",
            "column_indexing": "Use column names (strings) or 0-based column indices (integers)",
        },
        **preview_data,
    }


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
