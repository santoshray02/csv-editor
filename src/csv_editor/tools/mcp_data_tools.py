"""FastMCP data manipulation tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context

# Import type aliases
from .transformations import CellValue, FilterCondition, OperationResult

from .transformations import (
    add_column as _add_column,
)
from .transformations import (
    change_column_type as _change_column_type,
)
from .transformations import (
    extract_from_column as _extract_from_column,
)
from .transformations import (
    fill_column_nulls as _fill_column_nulls,
)
from .transformations import (
    fill_missing_values as _fill_missing_values,
)
from .transformations import (
    filter_rows as _filter_rows,
)
from .transformations import (
    remove_columns as _remove_columns,
)
from .transformations import (
    remove_duplicates as _remove_duplicates,
)
from .transformations import (
    rename_columns as _rename_columns,
)
from .transformations import (
    replace_in_column as _replace_in_column,
)
from .transformations import (
    select_columns as _select_columns,
)
from .transformations import (
    sort_data as _sort_data,
)
from .transformations import (
    split_column as _split_column,
)
from .transformations import (
    strip_column as _strip_column,
)
from .transformations import (
    transform_column_case as _transform_column_case,
)
from .transformations import (
    update_column as _update_column,
)


def register_data_tools(mcp: Any) -> None:
    """Register data manipulation tools with FastMCP server."""

    @mcp.tool
    async def filter_rows(
        session_id: str,
        conditions: list[FilterCondition],
        mode: str = "and",
        ctx: Context | None = None,
    ) -> OperationResult:
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
        value: CellValue | list[CellValue] = None,
        formula: str | None = None,
        ctx: Context | None = None,
    ) -> OperationResult:
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

    # Focused Column Operations
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
        return await _split_column(
            session_id, column, delimiter, part_index, expand_to_columns, ctx
        )

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
