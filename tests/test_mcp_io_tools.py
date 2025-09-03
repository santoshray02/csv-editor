"""Tests for I/O MCP tools."""

from src.csv_editor.tools.io_operations import (
    close_session,
    export_csv,
    get_session_info,
    list_sessions,
    load_csv,
    load_csv_from_content,
    load_csv_from_url,
)


class TestIOTools:
    """Test I/O tools availability."""

    def test_csv_loading_tools_available(self) -> None:
        """Test that CSV loading tools are available."""
        loading_ops = [
            load_csv,
            load_csv_from_url,
            load_csv_from_content,
        ]

        for op_func in loading_ops:
            assert callable(op_func)

    def test_session_management_tools_available(self) -> None:
        """Test that session management tools are available."""
        session_ops = [
            get_session_info,
            list_sessions,
            close_session,
        ]

        for op_func in session_ops:
            assert callable(op_func)

    def test_export_tools_available(self) -> None:
        """Test that export tools are available."""
        assert callable(export_csv)


class TestIOToolSignatures:
    """Test that I/O tools have expected signatures."""

    def test_load_csv_signature(self) -> None:
        """Test load_csv has correct function signature."""
        import inspect

        sig = inspect.signature(load_csv)
        params = list(sig.parameters.keys())

        expected_params = [
            "file_path",
            "encoding",
            "delimiter",
            "session_id",
            "header",
            "na_values",
            "parse_dates",
            "ctx",
        ]
        assert all(param in params for param in expected_params)

    def test_export_csv_signature(self) -> None:
        """Test export_csv has correct function signature."""
        import inspect

        sig = inspect.signature(export_csv)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "file_path", "format", "encoding", "index", "ctx"]
        assert all(param in params for param in expected_params)

    def test_session_info_signature(self) -> None:
        """Test get_session_info has correct function signature."""
        import inspect

        sig = inspect.signature(get_session_info)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "ctx"]
        assert all(param in params for param in expected_params)
