"""Tests for data manipulation MCP tools."""

from src.csv_editor.tools.transformations import (
    add_column,
    change_column_type,
    extract_from_column,
    fill_column_nulls,
    fill_missing_values,
    filter_rows,
    remove_columns,
    remove_duplicates,
    rename_columns,
    replace_in_column,
    select_columns,
    sort_data,
    split_column,
    strip_column,
    transform_column_case,
    update_column,
)


class TestDataManipulationTools:
    """Test data manipulation tools availability."""

    def test_basic_data_tools_available(self) -> None:
        """Test that basic data manipulation tools are available."""
        basic_ops = [
            filter_rows,
            sort_data,
            select_columns,
            rename_columns,
            add_column,
            remove_columns,
            change_column_type,
            fill_missing_values,
            remove_duplicates,
            update_column,
        ]

        for op_func in basic_ops:
            assert callable(op_func)

    def test_focused_column_operations_available(self) -> None:
        """Test that focused column operation tools are available."""
        focused_ops = [
            replace_in_column,
            extract_from_column,
            split_column,
            transform_column_case,
            strip_column,
            fill_column_nulls,
        ]

        for op_func in focused_ops:
            assert callable(op_func)


class TestDataToolSignatures:
    """Test that data manipulation tools have expected signatures."""

    def test_filter_rows_signature(self) -> None:
        """Test filter_rows has correct function signature."""
        import inspect

        sig = inspect.signature(filter_rows)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "conditions", "mode", "ctx"]
        assert all(param in params for param in expected_params)

    def test_add_column_signature(self) -> None:
        """Test add_column has correct function signature."""
        import inspect

        sig = inspect.signature(add_column)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "name", "value", "formula", "ctx"]
        assert all(param in params for param in expected_params)

    def test_replace_in_column_signature(self) -> None:
        """Test replace_in_column has correct function signature."""
        import inspect

        sig = inspect.signature(replace_in_column)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "column", "pattern", "replacement", "regex", "ctx"]
        assert all(param in params for param in expected_params)
