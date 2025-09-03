"""FastMCP row manipulation tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from .transformations import (
    delete_row as _delete_row,
)
from .transformations import (
    get_cell_value as _get_cell_value,
)
from .transformations import (
    get_column_data as _get_column_data,
)
from .transformations import (
    get_row_data as _get_row_data,
)
from .transformations import (
    insert_row as _insert_row,
)
from .transformations import (
    set_cell_value as _set_cell_value,
)
from .transformations import (
    update_row as _update_row,
)


def register_row_tools(mcp: Any) -> None:
    """Register row manipulation tools with FastMCP server."""

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
        session_id: str, row_index: int, column: str | int, value: str | int | float | bool | None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Set the value of a specific cell by row index and column name/index.

        Args:
            session_id: Session identifier
            row_index: Row index (0-based)
            column: Column name (str) or column index (int, 0-based)
            value: New value for the cell (supports null/None values)

        Returns:
            Dict with old value, new value, and coordinates

        Examples:
            set_cell_value("session123", 0, "name", "Jane") -> Set first row, "name" column to "Jane"
            set_cell_value("session123", 2, 1, 25) -> Set third row, second column to 25
            set_cell_value("session123", 1, "email", null) -> Set email to null
        """
        return await _set_cell_value(session_id, row_index, column, value, ctx)

    @mcp.tool
    async def get_row_data(
        session_id: str,
        row_index: int,
        columns: list[str] | None = None,
        ctx: Context | None = None,
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

    @mcp.tool
    async def insert_row(
        session_id: str,
        row_index: int,
        data: dict[str, str | int | float | bool | None] | list[str | int | float | bool | None] | str,  # Accept string for Claude Code compatibility
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Insert a new row at the specified index.

        Args:
            session_id: Session identifier
            row_index: Index where to insert the row (0-based). Use -1 to append at end
            data: Row data as dict (column_name: value) or list of values
                  Supports null/None values - JSON null becomes Python None

        Returns:
            Dict with success status and insertion info

        Examples:
            insert_row("session123", 1, {"name": "Alice", "age": 28, "city": "Boston"})
            insert_row("session123", -1, ["David", 40, "Miami"])  # Append at end
            insert_row("session123", 0, {"name": "John", "age": null, "city": "NYC"})  # With null values
            insert_row("session123", 2, ["Jane", None, "LA", None])  # List with null values
        """
        return await _insert_row(session_id, row_index, data, ctx)

    @mcp.tool
    async def delete_row(
        session_id: str, row_index: int, ctx: Context | None = None
    ) -> dict[str, Any]:
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
        session_id: str, row_index: int, data: dict[str, str | int | float | bool | None] | str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Update specific columns in a row with new values.

        Args:
            session_id: Session identifier
            row_index: Row index to update (0-based)
            data: Dict with column names and new values (partial updates allowed) or JSON string
                  Supports null/None values - JSON null becomes Python None

        Returns:
            Dict with success status and update info

        Examples:
            update_row("session123", 0, {"age": 31, "city": "Boston"}) -> Update age and city for first row
            update_row("session123", 1, {"phone": null, "email": null}) -> Set phone and email to null
            update_row("session123", 2, '{"status": "active", "notes": null}') -> JSON string from Claude Code
        """
        return await _update_row(session_id, row_index, data, ctx)
