"""History operations for CSV sessions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..models.csv_session import get_session_manager

if TYPE_CHECKING:
    from fastmcp import Context

logger = logging.getLogger(__name__)


async def undo_operation(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Undo the last operation in a session.

    Args:
        session_id: Session identifier
        ctx: FastMCP context

    Returns:
        Dict with success status and undo result
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
            await ctx.info(f"Undoing last operation for session {session_id}")

        result = await session.undo()

        if result["success"]:
            if ctx:
                await ctx.info(f"Successfully undid operation: {result.get('message')}")

            return {
                "success": True,
                "message": result["message"],
                "session_id": session_id,
                "data": result,
            }
        else:
            return {
                "success": False,
                "message": "Failed to undo operation",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error undoing operation: {e!s}")
        if ctx:
            await ctx.error(f"Failed to undo operation: {e!s}")
        return {"success": False, "message": "Failed to undo operation", "error": str(e)}


async def redo_operation(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Redo a previously undone operation.

    Args:
        session_id: Session identifier
        ctx: FastMCP context

    Returns:
        Dict with success status and redo result
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
            await ctx.info(f"Redoing operation for session {session_id}")

        result = await session.redo()

        if result["success"]:
            if ctx:
                await ctx.info(f"Successfully redid operation: {result.get('message')}")

            return {
                "success": True,
                "message": result["message"],
                "session_id": session_id,
                "data": result,
            }
        else:
            return {
                "success": False,
                "message": "Failed to redo operation",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error redoing operation: {e!s}")
        if ctx:
            await ctx.error(f"Failed to redo operation: {e!s}")
        return {"success": False, "message": "Failed to redo operation", "error": str(e)}


async def get_operation_history(
    session_id: str, limit: int | None = None, ctx: Context | None = None
) -> dict[str, Any]:
    """
    Get operation history for a session.

    Args:
        session_id: Session identifier
        limit: Maximum number of operations to return
        ctx: FastMCP context

    Returns:
        Dict with history and statistics
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
            await ctx.info(f"Getting operation history for session {session_id}")

        result = session.get_history(limit)

        if result["success"]:
            return {
                "success": True,
                "message": "History retrieved successfully",
                "session_id": session_id,
                "data": result,
            }
        else:
            return {
                "success": False,
                "message": "Failed to get history",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error getting history: {e!s}")
        if ctx:
            await ctx.error(f"Failed to get history: {e!s}")
        return {"success": False, "message": "Failed to get history", "error": str(e)}


async def restore_to_operation(
    session_id: str, operation_id: str, ctx: Context | None = None
) -> dict[str, Any]:
    """
    Restore session data to a specific operation point.

    Args:
        session_id: Session identifier
        operation_id: Operation ID to restore to
        ctx: FastMCP context

    Returns:
        Dict with success status and restore result
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
            await ctx.info(f"Restoring session {session_id} to operation {operation_id}")

        result = await session.restore_to_operation(operation_id)

        if result["success"]:
            if ctx:
                await ctx.info(f"Successfully restored to operation {operation_id}")

            return {
                "success": True,
                "message": result["message"],
                "session_id": session_id,
                "data": result,
            }
        else:
            return {
                "success": False,
                "message": "Failed to restore to operation",
                "error": result.get("error"),
            }

    except Exception as e:
        logger.error(f"Error restoring to operation: {e!s}")
        if ctx:
            await ctx.error(f"Failed to restore to operation: {e!s}")
        return {"success": False, "message": "Failed to restore to operation", "error": str(e)}


async def clear_history(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """
    Clear all operation history for a session.

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

        if not session.history_manager:
            return {
                "success": False,
                "message": "History is not enabled for this session",
                "error": "History management is disabled",
            }

        if ctx:
            await ctx.info(f"Clearing history for session {session_id}")

        session.history_manager.clear_history()

        return {
            "success": True,
            "message": "History cleared successfully",
            "session_id": session_id,
        }

    except Exception as e:
        logger.error(f"Error clearing history: {e!s}")
        if ctx:
            await ctx.error(f"Failed to clear history: {e!s}")
        return {"success": False, "message": "Failed to clear history", "error": str(e)}


async def export_history(
    session_id: str, file_path: str, format: str = "json", ctx: Context | None = None
) -> dict[str, Any]:
    """
    Export operation history to a file.

    Args:
        session_id: Session identifier
        file_path: Path to export history to
        format: Export format ('json' or 'csv')
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

        if not session.history_manager:
            return {
                "success": False,
                "message": "History is not enabled for this session",
                "error": "History management is disabled",
            }

        if ctx:
            await ctx.info(f"Exporting history for session {session_id} to {file_path}")

        success = session.history_manager.export_history(file_path, format)

        if success:
            return {
                "success": True,
                "message": f"History exported to {file_path}",
                "session_id": session_id,
                "data": {"file_path": file_path, "format": format},
            }
        else:
            return {
                "success": False,
                "message": "Failed to export history",
                "error": "Export operation failed",
            }

    except Exception as e:
        logger.error(f"Error exporting history: {e!s}")
        if ctx:
            await ctx.error(f"Failed to export history: {e!s}")
        return {"success": False, "message": "Failed to export history", "error": str(e)}
