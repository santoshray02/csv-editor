"""FastMCP history and auto-save tool definitions for CSV Editor."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from .auto_save_operations import (
    configure_auto_save as _configure_auto_save,
)
from .auto_save_operations import (
    disable_auto_save as _disable_auto_save,
)
from .auto_save_operations import (
    get_auto_save_status as _get_auto_save_status,
)
from .auto_save_operations import (
    trigger_manual_save as _trigger_manual_save,
)
from .history_operations import (
    clear_history as _clear_history,
)
from .history_operations import (
    export_history as _export_history,
)
from .history_operations import (
    get_operation_history as _get_operation_history,
)
from .history_operations import (
    redo_operation as _redo_operation,
)
from .history_operations import (
    restore_to_operation as _restore_to_operation,
)
from .history_operations import (
    undo_operation as _undo_operation,
)


def register_history_tools(mcp: Any) -> None:
    """Register history and auto-save tools with FastMCP server."""

    # Auto-save tools
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

    # History operations
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
