"""I/O operations tools for CSV Editor MCP Server."""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from ..models import ExportFormat, OperationType, get_session_manager
from ..utils.validators import validate_file_path, validate_url

if TYPE_CHECKING:
    from fastmcp import Context


def _create_data_preview_with_indices(df: pd.DataFrame, num_rows: int = 5) -> dict[str, Any]:
    """Create a data preview with row indices for AI accessibility."""
    preview_df = df.head(num_rows)

    # Create records with row indices
    preview_records = []
    for _, (row_idx, row) in enumerate(preview_df.iterrows()):
        record = {"__row_index__": int(row_idx)}  # Include original row index
        record.update(row.to_dict())

        # Handle pandas/numpy types for JSON serialization
        for key, value in record.items():
            if key == "__row_index__":
                continue
            if pd.isna(value):
                record[key] = None
            elif hasattr(value, "item"):
                record[key] = value.item()

        preview_records.append(record)

    return {
        "records": preview_records,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "preview_rows": len(preview_records),
    }


async def load_csv(
    file_path: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: str | None = None,
    header: int | None = 0,
    na_values: list[str] | None = None,
    parse_dates: list[str] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load a CSV file into a session.

    Args:
        file_path: Path to the CSV file
        encoding: File encoding (default: utf-8)
        delimiter: Column delimiter (default: comma)
        session_id: Optional existing session ID to use
        header: Row number to use as header (default: 0)
        na_values: Additional strings to recognize as NA/NaN
        parse_dates: Columns to parse as dates
        ctx: FastMCP context

    Returns:
        Operation result with session ID and data info
    """
    try:
        # Validate file path
        is_valid, validated_path = validate_file_path(file_path)
        if not is_valid:
            return {
                "success": False,
                "message": f"Invalid file path: {validated_path}",
                "error": validated_path,
            }

        if ctx:
            await ctx.info(f"Loading CSV file: {validated_path}")
            await ctx.report_progress(0.1)

        # Get or create session
        session_manager = get_session_manager()
        session = session_manager.get_or_create_session(session_id)

        if ctx:
            await ctx.report_progress(0.3)

        # Read CSV with pandas
        read_params: dict[str, Any] = {
            "filepath_or_buffer": validated_path,
            "encoding": encoding,
            "delimiter": delimiter,
            "header": header,
        }

        if na_values:
            read_params["na_values"] = na_values
        if parse_dates:
            read_params["parse_dates"] = parse_dates

        df = pd.read_csv(**read_params)

        if ctx:
            await ctx.report_progress(0.8)

        # Load into session
        session.load_data(df, validated_path)

        if ctx:
            await ctx.report_progress(1.0)
            await ctx.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

        return {
            "success": True,
            "message": "Successfully loaded CSV file",
            "session_id": session.session_id,
            "rows_affected": len(df),
            "columns_affected": df.columns.tolist(),
            "data": {
                "shape": df.shape,
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
                "preview": _create_data_preview_with_indices(df, 5),
            },
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to load CSV: {e!s}")
        return {"success": False, "message": "Failed to load CSV file", "error": str(e)}


async def load_csv_from_url(
    url: str,
    encoding: str = "utf-8",
    delimiter: str = ",",
    session_id: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load a CSV file from a URL.

    Args:
        url: URL of the CSV file
        encoding: File encoding
        delimiter: Column delimiter
        session_id: Optional existing session ID
        ctx: FastMCP context

    Returns:
        Operation result with session ID and data info
    """
    try:
        # Validate URL
        is_valid, validated_url = validate_url(url)
        if not is_valid:
            return {
                "success": False,
                "message": f"Invalid URL: {validated_url}",
                "error": validated_url,
            }

        if ctx:
            await ctx.info(f"Loading CSV from URL: {url}")
            await ctx.report_progress(0.1)

        # Download CSV using pandas (it handles URLs directly)
        df = pd.read_csv(url, encoding=encoding, delimiter=delimiter)

        if ctx:
            await ctx.report_progress(0.8)

        # Get or create session
        session_manager = get_session_manager()
        session = session_manager.get_or_create_session(session_id)
        session.load_data(df, url)

        if ctx:
            await ctx.report_progress(1.0)
            await ctx.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

        return {
            "success": True,
            "message": "Successfully loaded CSV from URL",
            "session_id": session.session_id,
            "rows_affected": len(df),
            "columns_affected": df.columns.tolist(),
            "data": {
                "shape": df.shape,
                "source_url": url,
                "preview": _create_data_preview_with_indices(df, 5),
            },
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to load CSV from URL: {e!s}")
        return {"success": False, "message": "Failed to load CSV from URL", "error": str(e)}


async def load_csv_from_content(
    content: str,
    delimiter: str = ",",
    session_id: str | None = None,
    has_header: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Load CSV data from a string content.

    Args:
        content: CSV content as string
        delimiter: Column delimiter
        session_id: Optional existing session ID
        has_header: Whether first row is header
        ctx: FastMCP context

    Returns:
        Operation result with session ID and data info
    """
    try:
        if ctx:
            await ctx.info("Loading CSV from content string")

        # Parse CSV from string
        from io import StringIO

        df = pd.read_csv(StringIO(content), delimiter=delimiter, header=0 if has_header else None)

        # Get or create session
        session_manager = get_session_manager()
        session = session_manager.get_or_create_session(session_id)
        session.load_data(df, None)

        if ctx:
            await ctx.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

        return {
            "success": True,
            "message": "Successfully loaded CSV from content",
            "session_id": session.session_id,
            "rows_affected": len(df),
            "columns_affected": df.columns.tolist(),
            "data": {"shape": df.shape, "preview": _create_data_preview_with_indices(df, 5)},
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to parse CSV content: {e!s}")
        return {"success": False, "message": "Failed to parse CSV content", "error": str(e)}


async def export_csv(
    session_id: str,
    file_path: str | None = None,
    format: ExportFormat = ExportFormat.CSV,
    encoding: str = "utf-8",
    index: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Export session data to various formats.

    Args:
        session_id: Session ID to export
        file_path: Optional output file path (auto-generated if not provided)
        format: Export format (csv, tsv, json, excel, parquet, html, markdown)
        encoding: Output encoding
        index: Whether to include index in output
        ctx: FastMCP context

    Returns:
        Operation result with file path
    """
    try:
        # Get session
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session or session.df is None:
            return {
                "success": False,
                "message": "Session not found or no data loaded",
                "error": "Invalid session ID",
            }

        if ctx:
            await ctx.info(f"Exporting data in {format.value} format")
            await ctx.report_progress(0.1)

        # Generate file path if not provided
        if not file_path:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"export_{session_id[:8]}_{timestamp}"

            # Determine extension based on format
            extensions = {
                ExportFormat.CSV: ".csv",
                ExportFormat.TSV: ".tsv",
                ExportFormat.JSON: ".json",
                ExportFormat.EXCEL: ".xlsx",
                ExportFormat.PARQUET: ".parquet",
                ExportFormat.HTML: ".html",
                ExportFormat.MARKDOWN: ".md",
            }

            file_path = tempfile.gettempdir() + "/" + filename + extensions[format]

        path_obj = Path(file_path)
        df = session.df

        if ctx:
            await ctx.report_progress(0.5)

        # Export based on format
        if format == ExportFormat.CSV:
            df.to_csv(path_obj, encoding=encoding, index=index)
        elif format == ExportFormat.TSV:
            df.to_csv(path_obj, sep="\t", encoding=encoding, index=index)
        elif format == ExportFormat.JSON:
            df.to_json(path_obj, orient="records", indent=2)
        elif format == ExportFormat.EXCEL:
            df.to_excel(path_obj, index=index, engine="openpyxl")
        elif format == ExportFormat.PARQUET:
            df.to_parquet(path_obj, index=index)
        elif format == ExportFormat.HTML:
            df.to_html(path_obj, index=index)
        elif format == ExportFormat.MARKDOWN:
            df.to_markdown(path_obj, index=index)
        else:
            return {
                "success": False,
                "message": f"Unsupported format: {format}",
                "error": "Invalid export format",
            }

        # Record operation
        session.record_operation(
            OperationType.EXPORT, {"format": format.value, "file_path": str(file_path)}
        )

        if ctx:
            await ctx.report_progress(1.0)
            await ctx.info(f"Exported to {file_path}")

        return {
            "success": True,
            "message": f"Successfully exported data to {format.value}",
            "session_id": session_id,
            "data": {
                "file_path": str(file_path),
                "format": format.value,
                "rows_exported": len(df),
                "file_size_bytes": path_obj.stat().st_size,
            },
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to export data: {e!s}")
        return {"success": False, "message": "Failed to export data", "error": str(e)}


async def get_session_info(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Get information about a specific session.

    Args:
        session_id: Session ID
        ctx: FastMCP context

    Returns:
        Session information
    """
    try:
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)

        if not session:
            return {"success": False, "message": "Session not found", "error": "Invalid session ID"}

        if ctx:
            await ctx.info(f"Retrieved info for session {session_id}")

        info = session.get_info()
        return {
            "success": True,
            "message": "Session info retrieved",
            "session_id": session_id,
            "data": info.model_dump(),
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get session info: {e!s}")
        return {"success": False, "message": "Failed to get session info", "error": str(e)}


async def list_sessions(ctx: Context | None = None) -> dict[str, Any]:
    """List all active sessions.

    Args:
        ctx: FastMCP context

    Returns:
        List of active sessions
    """
    try:
        session_manager = get_session_manager()
        sessions = session_manager.list_sessions()

        if ctx:
            await ctx.info(f"Found {len(sessions)} active sessions")

        return {
            "success": True,
            "message": f"Found {len(sessions)} active sessions",
            "sessions": [s.model_dump() for s in sessions],
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to list sessions: {e!s}")
        return {"success": False, "message": "Failed to list sessions", "error": str(e)}


async def close_session(session_id: str, ctx: Context | None = None) -> dict[str, Any]:
    """Close and clean up a session.

    Args:
        session_id: Session ID to close
        ctx: FastMCP context

    Returns:
        Operation result
    """
    try:
        session_manager = get_session_manager()
        removed = await session_manager.remove_session(session_id)

        if not removed:
            return {"success": False, "message": "Session not found", "error": "Invalid session ID"}

        if ctx:
            await ctx.info(f"Closed session {session_id}")

        return {
            "success": True,
            "message": f"Session {session_id} closed successfully",
            "session_id": session_id,
        }

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to close session: {e!s}")
        return {"success": False, "message": "Failed to close session", "error": str(e)}
