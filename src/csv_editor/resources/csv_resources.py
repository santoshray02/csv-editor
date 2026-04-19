"""Resource definitions - placeholder implementation."""

from typing import Any

from fastmcp import Context


# Placeholder resources - will implement next
async def get_csv_data(session_id: str, ctx: Context) -> dict[str, Any]:
    return {"session_id": session_id, "data": "Not yet implemented"}


async def get_csv_schema(session_id: str, ctx: Context) -> dict[str, Any]:
    return {"session_id": session_id, "schema": "Not yet implemented"}


async def get_csv_preview(session_id: str, ctx: Context) -> dict[str, Any]:
    return {"session_id": session_id, "preview": "Not yet implemented"}


async def list_active_sessions(ctx: Context) -> list[dict[str, Any]]:
    return []
