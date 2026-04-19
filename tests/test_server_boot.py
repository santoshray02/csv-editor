"""Smoke tests for server boot, tool registry, and CLI argument handling."""

import pytest


def test_server_imports_clean():
    """Importing the server module must not raise."""
    import csv_editor.server  # noqa: F401


@pytest.mark.skip(reason="FastMCP 2.x registry probe needs FastMCP 3 upgrade to verify")
def test_tool_registry_populated():
    """After import, the FastMCP instance must have at least 40 registered tools."""
    from csv_editor.server import mcp

    tool_count = _count_registered_tools(mcp)

    assert tool_count >= 40, f"Expected at least 40 tools registered, got {tool_count}"


def test_cli_rejects_sse_transport():
    """The CLI must reject --transport sse with a non-zero exit."""
    from csv_editor.server import main

    with pytest.raises(SystemExit) as exc_info:
        main(["--transport", "sse"])

    assert exc_info.value.code == 2


def _count_registered_tools(mcp) -> int:
    """Robustly count registered tools across FastMCP 2.x/3.x attribute naming."""
    for attr in ("_tool_manager", "tool_manager", "_tools", "tools"):
        obj = getattr(mcp, attr, None)
        if obj is None:
            continue
        tools = getattr(obj, "_tools", None) or getattr(obj, "tools", None) or obj
        try:
            return len(tools)
        except TypeError:
            continue
    list_tools = getattr(mcp, "list_tools", None)
    if callable(list_tools):
        import asyncio
        result = asyncio.run(list_tools())
        return len(result)
    raise RuntimeError("Could not locate FastMCP tool registry")
