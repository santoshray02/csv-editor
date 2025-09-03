"""Tests for analytics MCP tools."""

from src.csv_editor.tools.analytics import (
    detect_outliers,
    get_column_statistics,
    get_correlation_matrix,
    get_statistics,
    get_value_counts,
    group_by_aggregate,
    profile_data,
)
from src.csv_editor.tools.transformations import (
    find_cells_with_value,
    get_data_summary,
    inspect_data_around,
)


class TestAnalyticsTools:
    """Test analytics tools availability."""

    def test_statistical_analysis_tools_available(self) -> None:
        """Test that statistical analysis tools are available."""
        stats_ops = [
            get_statistics,
            get_column_statistics,
            get_correlation_matrix,
            get_value_counts,
            profile_data,
        ]

        for op_func in stats_ops:
            assert callable(op_func)

    def test_data_exploration_tools_available(self) -> None:
        """Test that data exploration tools are available."""
        exploration_ops = [
            detect_outliers,
            group_by_aggregate,
        ]

        for op_func in exploration_ops:
            assert callable(op_func)

    def test_ai_convenience_tools_available(self) -> None:
        """Test that AI convenience tools are available."""
        ai_ops = [
            inspect_data_around,
            find_cells_with_value,
            get_data_summary,
        ]

        for op_func in ai_ops:
            assert callable(op_func)


class TestAnalyticsToolSignatures:
    """Test that analytics tools have expected signatures."""

    def test_get_statistics_signature(self) -> None:
        """Test get_statistics has correct function signature."""
        import inspect

        sig = inspect.signature(get_statistics)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "columns", "include_percentiles", "ctx"]
        assert all(param in params for param in expected_params)

    def test_detect_outliers_signature(self) -> None:
        """Test detect_outliers has correct function signature."""
        import inspect

        sig = inspect.signature(detect_outliers)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "columns", "method", "threshold", "ctx"]
        assert all(param in params for param in expected_params)

    def test_find_cells_with_value_signature(self) -> None:
        """Test find_cells_with_value has correct function signature."""
        import inspect

        sig = inspect.signature(find_cells_with_value)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "value", "column", "exact_match", "ctx"]
        assert all(param in params for param in expected_params)
