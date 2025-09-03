"""Tests for row manipulation MCP tools."""

from src.csv_editor.tools.transformations import (
    delete_row,
    get_cell_value,
    get_column_data,
    get_row_data,
    insert_row,
    set_cell_value,
    update_row,
)


class TestRowLevelTools:
    """Test row-level access tools availability."""

    def test_cell_level_tools_available(self) -> None:
        """Test that cell-level access tools are available."""
        # Verify cell access tools exist and are callable
        assert callable(get_cell_value)
        assert callable(set_cell_value)

    def test_row_level_tools_available(self) -> None:
        """Test that row-level access tools are available."""
        # Verify row access tools exist and are callable
        assert callable(get_row_data)
        assert callable(get_column_data)

    def test_row_manipulation_tools_available(self) -> None:
        """Test that row manipulation tools are available."""
        # Verify row manipulation tools exist and are callable
        row_ops = [insert_row, delete_row, update_row]

        for op_func in row_ops:
            assert callable(op_func)


class TestRowToolFunctionality:
    """Test that row tool functions have expected signatures."""

    def test_insert_row_signature(self) -> None:
        """Test insert_row has correct function signature."""
        import inspect

        sig = inspect.signature(insert_row)
        params = list(sig.parameters.keys())

        # Should have session_id, row_index, data, and optional ctx
        expected_params = ["session_id", "row_index", "data", "ctx"]
        assert all(param in params for param in expected_params)

    def test_set_cell_value_signature(self) -> None:
        """Test set_cell_value has correct function signature."""
        import inspect

        sig = inspect.signature(set_cell_value)
        params = list(sig.parameters.keys())

        # Should have session_id, row_index, column, value, and optional ctx
        expected_params = ["session_id", "row_index", "column", "value", "ctx"]
        assert all(param in params for param in expected_params)

    def test_update_row_signature(self) -> None:
        """Test update_row has correct function signature."""
        import inspect

        sig = inspect.signature(update_row)
        params = list(sig.parameters.keys())

        # Should have session_id, row_index, data, and optional ctx
        expected_params = ["session_id", "row_index", "data", "ctx"]
        assert all(param in params for param in expected_params)
