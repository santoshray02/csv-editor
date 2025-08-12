"""Data operations - imports from io_operations for compatibility."""

# Re-export io_operations functions as data_operations
from .io_operations import (
    load_csv,
    load_csv_from_url,
    load_csv_from_content,
    export_csv,
    get_session_info,
    list_sessions,
    close_session
)