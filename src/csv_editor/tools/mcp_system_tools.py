"""FastMCP system tool definitions for CSV Editor."""

from __future__ import annotations

import os
from typing import Any

from fastmcp import Context

from ..models import get_session_manager


def register_system_tools(mcp: Any) -> None:
    """Register system tools with FastMCP server."""

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
                    "null_value_support",  # Explicitly mention null support
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
                "session_management": [
                    "multi_session_support",
                    "session_isolation",
                    "auto_cleanup",
                ],
                "null_handling": [
                    "json_null_support",
                    "python_none_support",
                    "pandas_nan_compatibility",
                    "null_value_insertion",
                    "null_value_updates",
                ],
            },
            "supported_formats": ["csv", "tsv", "json", "excel", "parquet", "html", "markdown"],
            "max_file_size_mb": int(os.getenv("CSV_MAX_FILE_SIZE", "1024")),
            "session_timeout_minutes": int(os.getenv("CSV_SESSION_TIMEOUT", "60")),
        }
