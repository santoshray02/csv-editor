"""Main FastMCP server for CSV Editor."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# Local imports
from .models import get_session_manager
from .tools.io_operations import _create_data_preview_with_indices
from .tools.mcp_analytics_tools import register_analytics_tools
from .tools.mcp_data_tools import register_data_tools
from .tools.mcp_history_tools import register_history_tools
from .tools.mcp_io_tools import register_io_tools
from .tools.mcp_row_tools import register_row_tools
from .tools.mcp_system_tools import register_system_tools
from .tools.mcp_validation_tools import register_validation_tools
from .tools.transformations import get_cell_value as _get_cell_value
from .tools.transformations import get_row_data as _get_row_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_instructions() -> str:
    """Load instructions from the markdown file."""
    instructions_path = Path(__file__).parent / "instructions.md"
    try:
        return instructions_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Instructions file not found at {instructions_path}")
        return "CSV Editor MCP Server - Instructions file not available"
    except Exception as e:
        logger.error(f"Error loading instructions: {e}")
        return "CSV Editor MCP Server - Error loading instructions"


# Initialize FastMCP server
mcp = FastMCP("CSV Editor", instructions=_load_instructions())

# Register all tools with the FastMCP server
register_system_tools(mcp)
register_io_tools(mcp)
register_data_tools(mcp)
register_row_tools(mcp)
register_analytics_tools(mcp)
register_validation_tools(mcp)
register_history_tools(mcp)


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("csv://{session_id}/data")
async def get_csv_data(session_id: str) -> dict[str, Any]:
    """Get current CSV data from a session with enhanced indexing."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    # Use enhanced preview for better AI accessibility
    preview_data = _create_data_preview_with_indices(session.df, 10)

    return {
        "session_id": session_id,
        "shape": session.df.shape,
        "preview": preview_data,
        "columns_info": {
            "columns": session.df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in session.df.dtypes.items()},
        },
    }


@mcp.resource("csv://{session_id}/schema")
async def get_csv_schema(session_id: str) -> dict[str, Any]:
    """Get CSV schema information."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    return {
        "session_id": session_id,
        "columns": session.df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in session.df.dtypes.items()},
        "shape": session.df.shape,
    }


@mcp.resource("sessions://active")
async def list_active_sessions() -> list[dict[str, Any]]:
    """List all active CSV sessions."""
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions()
    return [s.dict() for s in sessions]


@mcp.resource("csv://{session_id}/cell/{row_index}/{column}")
async def get_csv_cell(session_id: str, row_index: str, column: str) -> dict[str, Any]:
    """Get data for a specific cell with coordinate information."""
    try:
        row_idx = int(row_index)
        # Try to convert column to int if it's numeric
        try:
            col_param: str | int = int(column)
        except ValueError:
            col_param = column

        result = await _get_cell_value(session_id, row_idx, col_param)
        return result
    except ValueError:
        return {"error": "Invalid row index - must be an integer"}


@mcp.resource("csv://{session_id}/row/{row_index}")
async def get_csv_row(session_id: str, row_index: str) -> dict[str, Any]:
    """Get data for a specific row with all column values."""
    try:
        row_idx = int(row_index)
        result = await _get_row_data(session_id, row_idx)
        return result
    except ValueError:
        return {"error": "Invalid row index - must be an integer"}


@mcp.resource("csv://{session_id}/preview")
async def get_csv_preview(session_id: str) -> dict[str, Any]:
    """Get a preview of the CSV data with enhanced indexing and coordinate information."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)

    if not session or session.df is None:
        return {"error": "Session not found or no data loaded"}

    preview_data = _create_data_preview_with_indices(session.df, 10)

    return {
        "session_id": session_id,
        "coordinate_system": {
            "description": "Uses 0-based indexing for both rows and columns",
            "row_indexing": "0 to N-1 where N is total rows",
            "column_indexing": "Use column names (strings) or 0-based column indices (integers)",
        },
        **preview_data,
    }


# ============================================================================
# PROMPTS
# ============================================================================


@mcp.prompt
def analyze_csv_prompt(session_id: str, analysis_type: str = "summary") -> str:
    """Generate a prompt to analyze CSV data."""
    return f"""Please analyze the CSV data in session {session_id}.

Analysis type: {analysis_type}

Provide insights about:
1. Data quality and completeness
2. Statistical patterns
3. Potential issues or anomalies
4. Recommended transformations or cleanups
"""


@mcp.prompt
def data_cleaning_prompt(session_id: str) -> str:
    """Generate a prompt for data cleaning suggestions."""
    return f"""Review the data in session {session_id} and suggest cleaning operations.

Consider:
- Missing values and how to handle them
- Duplicate rows
- Data type conversions needed
- Outliers that may need attention
- Column naming conventions
"""


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main() -> None:
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="CSV Editor")
    parser.add_argument(
        "--transport", choices=["stdio", "http", "sse"], default="stdio", help="Transport method"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP/SSE transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP/SSE transport")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    logger.info(f"Starting CSV Editor with {args.transport} transport")

    # Run the server
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
