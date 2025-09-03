"""Auto-save operations for CSV sessions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..models.csv_session import get_session_manager

if TYPE_CHECKING:
    from fastmcp import Context

logger = logging.getLogger(__name__)


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
    """
    Configure auto-save settings for a session.

    Args:
        session_id: Session identifier
        enabled: Whether auto-save is enabled
        mode: Auto-save mode ('disabled', 'after_operation', 'periodic', 'hybrid')
        strategy: Save strategy ('overwrite', 'backup', 'versioned', 'custom')
        interval_seconds: Interval for periodic saves (default 300)
        max_backups: Maximum number of backup files to keep (default 10)
        backup_dir: Directory for backup files
        custom_path: Custom path for saves (when strategy='custom')
        format: Export format ('csv', 'tsv', 'json', 'excel', 'parquet')
        encoding: File encoding (default 'utf-8')
        ctx: FastMCP context

    Returns:
        Dict with success status and configuration
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session:
            return {
                "success": False,
                "message": "Session not found",
                "error": f"No session with ID: {session_id}",
            }

        if ctx:
            await ctx.info(f"Configuring auto-save for session {session_id}")

        # Build configuration
        config = {
            "enabled": enabled,
            "mode": mode,
            "strategy": strategy,
            "format": format,
            "encoding": encoding,
        }

        if interval_seconds is not None:
            config["interval_seconds"] = interval_seconds
        if max_backups is not None:
            config["max_backups"] = max_backups
        if backup_dir is not None:
            config["backup_dir"] = backup_dir
        if custom_path is not None:
            config["custom_path"] = custom_path

        # Apply configuration
        result = await session.enable_auto_save(config)

        if result["success"]:
            if ctx:
                await ctx.info(f"Auto-save configured: {mode} mode, {strategy} strategy")

            return {
                "success": True,
                "message": "Auto-save configured successfully",
                "session_id": session_id,
                "data": result["config"],
            }
        else:
            return {
                "success": False,
                "message": "Failed to configure auto-save",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error configuring auto-save: {e!s}")
        if ctx:
            await ctx.error(f"Failed to configure auto-save: {e!s}")
        return {"success": False, "message": "Failed to configure auto-save", "error": str(e)}


async def disable_auto_save(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Disable auto-save for a session.

    Args:
        session_id: Session identifier
        ctx: FastMCP context

    Returns:
        Dict with success status
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session:
            return {
                "success": False,
                "message": "Session not found",
                "error": f"No session with ID: {session_id}",
            }

        result = await session.disable_auto_save()

        if result["success"]:
            if ctx:
                await ctx.info(f"Auto-save disabled for session {session_id}")

            return {"success": True, "message": "Auto-save disabled", "session_id": session_id}
        else:
            return {
                "success": False,
                "message": "Failed to disable auto-save",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error disabling auto-save: {e!s}")
        if ctx:
            await ctx.error(f"Failed to disable auto-save: {e!s}")
        return {"success": False, "message": "Failed to disable auto-save", "error": str(e)}


async def get_auto_save_status(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Get auto-save status for a session.

    Args:
        session_id: Session identifier
        ctx: FastMCP context

    Returns:
        Dict with auto-save status
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session:
            return {
                "success": False,
                "message": "Session not found",
                "error": f"No session with ID: {session_id}",
            }

        status = session.get_auto_save_status()

        if ctx:
            await ctx.info(f"Auto-save status retrieved for session {session_id}")

        return {
            "success": True,
            "message": "Auto-save status retrieved",
            "session_id": session_id,
            "data": status,
        }

    except Exception as e:
        logger.error(f"Error getting auto-save status: {e!s}")
        if ctx:
            await ctx.error(f"Failed to get auto-save status: {e!s}")
        return {"success": False, "message": "Failed to get auto-save status", "error": str(e)}


async def trigger_manual_save(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Manually trigger a save for a session.

    Args:
        session_id: Session identifier
        ctx: FastMCP context

    Returns:
        Dict with save result
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session:
            return {
                "success": False,
                "message": "Session not found",
                "error": f"No session with ID: {session_id}",
            }

        if ctx:
            await ctx.info(f"Triggering manual save for session {session_id}")

        result = await session.manual_save()

        if result["success"]:
            if ctx:
                await ctx.info(f"Manual save completed: {result.get('save_path')}")

            return {
                "success": True,
                "message": "Manual save completed",
                "session_id": session_id,
                "data": result,
            }
        else:
            return {"success": False, "message": "Manual save failed", "error": result.get("error")}

    except Exception as e:
        logger.error(f"Error in manual save: {e!s}")
        if ctx:
            await ctx.error(f"Failed to trigger manual save: {e!s}")
        return {"success": False, "message": "Failed to trigger manual save", "error": str(e)}
