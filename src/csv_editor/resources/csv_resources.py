"""Resource definitions - placeholder implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import Context


# Placeholder resources - will implement next
async def get_csv_data(session_id: str, ctx: Context | None) -> dict[str, Any]:  # noqa: ARG001
    return {"session_id": session_id, "data": "Not yet implemented"}


async def get_csv_schema(session_id: str, ctx: Context | None) -> dict[str, Any]:  # noqa: ARG001
    return {"session_id": session_id, "schema": "Not yet implemented"}


async def get_csv_preview(session_id: str, ctx: Context | None) -> dict[str, Any]:  # noqa: ARG001
    return {"session_id": session_id, "preview": "Not yet implemented"}


async def list_active_sessions(ctx: Context | None) -> list[dict[str, Any]]:  # noqa: ARG001
    return []
