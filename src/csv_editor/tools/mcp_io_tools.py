"""FastMCP I/O tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from ..models import ExportFormat
from .io_operations import (
    close_session as _close_session,
)
from .io_operations import (
    export_csv as _export_csv,
)
from .io_operations import (
    get_session_info as _get_session_info,
)
from .io_operations import (
    list_sessions as _list_sessions,
)
from .io_operations import (
    load_csv as _load_csv,
)
from .io_operations import (
    load_csv_from_content as _load_csv_from_content,
)
from .io_operations import (
    load_csv_from_url as _load_csv_from_url,
)


def register_io_tools(mcp: Any) -> None:
    """Register I/O tools with FastMCP server."""

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
