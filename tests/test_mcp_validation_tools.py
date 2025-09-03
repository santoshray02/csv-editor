"""Tests for validation MCP tools."""

from src.csv_editor.tools.validation import (
    check_data_quality,
    find_anomalies,
    validate_schema,
)


class TestValidationTools:
    """Test validation tools availability."""

    def test_validation_tools_available(self) -> None:
        """Test that validation tools are available."""
        validation_ops = [
            validate_schema,
            check_data_quality,
            find_anomalies,
        ]

        for op_func in validation_ops:
            assert callable(op_func)


class TestValidationToolSignatures:
    """Test that validation tools have expected signatures."""

    def test_validate_schema_signature(self) -> None:
        """Test validate_schema has correct function signature."""
        import inspect

        sig = inspect.signature(validate_schema)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "schema", "ctx"]
        assert all(param in params for param in expected_params)

    def test_check_data_quality_signature(self) -> None:
        """Test check_data_quality has correct function signature."""
        import inspect

        sig = inspect.signature(check_data_quality)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "rules", "ctx"]
        assert all(param in params for param in expected_params)

    def test_find_anomalies_signature(self) -> None:
        """Test find_anomalies has correct function signature."""
        import inspect

        sig = inspect.signature(find_anomalies)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "columns", "sensitivity", "methods", "ctx"]
        assert all(param in params for param in expected_params)
