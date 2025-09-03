"""FastMCP validation tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from .validation import (
    check_data_quality as _check_data_quality,
)
from .validation import (
    find_anomalies as _find_anomalies,
)
from .validation import (
    validate_schema as _validate_schema,
)


def register_validation_tools(mcp: Any) -> None:
    """Register validation tools with FastMCP server."""

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
