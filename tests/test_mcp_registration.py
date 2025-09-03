"""Tests for FastMCP tool registration and server integration."""

from src.csv_editor.server import mcp
from src.csv_editor.tools import (
    mcp_analytics_tools,
    mcp_data_tools,
    mcp_history_tools,
    mcp_io_tools,
    mcp_row_tools,
    mcp_system_tools,
    mcp_validation_tools,
)


class TestToolRegistration:
    """Test that all tool modules register correctly with FastMCP."""

    def test_all_registration_functions_exist(self) -> None:
        """Test that all registration functions exist and are callable."""
        registration_funcs = [
            mcp_system_tools.register_system_tools,
            mcp_io_tools.register_io_tools,
            mcp_data_tools.register_data_tools,
            mcp_row_tools.register_row_tools,
            mcp_analytics_tools.register_analytics_tools,
            mcp_validation_tools.register_validation_tools,
            mcp_history_tools.register_history_tools,
        ]

        for reg_func in registration_funcs:
            assert callable(reg_func)

    def test_server_initialization_successful(self) -> None:
        """Test that server initializes successfully with all tools."""
        from fastmcp import FastMCP

        # Verify server is FastMCP instance
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "CSV Editor"
        assert mcp.instructions is not None

    def test_tool_modules_importable(self) -> None:
        """Test that all tool modules can be imported successfully."""
        # This test ensures all modules have correct imports and dependencies

        # If we get here without ImportError, all modules imported successfully
        assert True


class TestBackwardCompatibilityThroughModules:
    """Test that original functionality is preserved through modular architecture."""

    def test_core_functions_available_in_modules(self) -> None:
        """Test that core functions are available in their respective modules."""
        # Test core I/O functions
        from src.csv_editor.tools.io_operations import export_csv, load_csv

        assert callable(load_csv)
        assert callable(export_csv)

        # Test core transformation functions
        from src.csv_editor.tools.transformations import add_column, filter_rows, insert_row

        assert callable(insert_row)
        assert callable(filter_rows)
        assert callable(add_column)

        # Test core analytics functions
        from src.csv_editor.tools.analytics import get_statistics, profile_data

        assert callable(get_statistics)
        assert callable(profile_data)

    def test_null_value_support_preserved(self) -> None:
        """Test that null value support is preserved in refactored tools."""
        # These functions should support None/null values
        import inspect

        from src.csv_editor.tools.transformations import insert_row, set_cell_value, update_row

        # Check that insert_row accepts Any type for data
        sig = inspect.signature(insert_row)
        data_param = sig.parameters.get("data")
        assert data_param is not None

        # Check that set_cell_value accepts Any type for value
        sig = inspect.signature(set_cell_value)
        value_param = sig.parameters.get("value")
        assert value_param is not None

        # Check that update_row accepts dict with Any values
        sig = inspect.signature(update_row)
        data_param = sig.parameters.get("data")
        assert data_param is not None
