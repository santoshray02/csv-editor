"""FastMCP analytics tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context

# Import type aliases
from .transformations import CellValue

from .analytics import (
    detect_outliers as _detect_outliers,
)
from .analytics import (
    get_column_statistics as _get_column_statistics,
)
from .analytics import (
    get_correlation_matrix as _get_correlation_matrix,
)
from .analytics import (
    get_statistics as _get_statistics,
)
from .analytics import (
    get_value_counts as _get_value_counts,
)
from .analytics import (
    group_by_aggregate as _group_by_aggregate,
)
from .analytics import (
    profile_data as _profile_data,
)
from .transformations import (
    find_cells_with_value as _find_cells_with_value,
)
from .transformations import (
    get_data_summary as _get_data_summary,
)
from .transformations import (
    inspect_data_around as _inspect_data_around,
)


def register_analytics_tools(mcp: Any) -> None:
    """Register analytics tools with FastMCP server."""

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
        session_id: str,
        group_by: list[str],
        aggregations: dict[str, Any],
        ctx: Context | None = None,
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

    # AI-Friendly convenience tools
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
        value: CellValue,
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
