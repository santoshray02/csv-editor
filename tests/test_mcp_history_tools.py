"""Tests for history and auto-save MCP tools."""

from src.csv_editor.tools.auto_save_operations import (
    configure_auto_save,
    disable_auto_save,
    get_auto_save_status,
    trigger_manual_save,
)
from src.csv_editor.tools.history_operations import (
    clear_history,
    export_history,
    get_operation_history,
    redo_operation,
    restore_to_operation,
    undo_operation,
)


class TestHistoryTools:
    """Test history tools availability."""

    def test_history_operations_available(self) -> None:
        """Test that history operation tools are available."""
        history_ops = [
            undo_operation,
            redo_operation,
            get_operation_history,
            restore_to_operation,
            clear_history,
            export_history,
        ]

        for op_func in history_ops:
            assert callable(op_func)

    def test_auto_save_tools_available(self) -> None:
        """Test that auto-save tools are available."""
        autosave_ops = [
            configure_auto_save,
            disable_auto_save,
            get_auto_save_status,
            trigger_manual_save,
        ]

        for op_func in autosave_ops:
            assert callable(op_func)


class TestHistoryToolSignatures:
    """Test that history tools have expected signatures."""

    def test_undo_operation_signature(self) -> None:
        """Test undo_operation has correct function signature."""
        import inspect

        sig = inspect.signature(undo_operation)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "ctx"]
        assert all(param in params for param in expected_params)

    def test_configure_auto_save_signature(self) -> None:
        """Test configure_auto_save has correct function signature."""
        import inspect

        sig = inspect.signature(configure_auto_save)
        params = list(sig.parameters.keys())

        expected_params = [
            "session_id",
            "enabled",
            "mode",
            "strategy",
            "interval_seconds",
            "max_backups",
            "backup_dir",
            "custom_path",
            "format",
            "encoding",
            "ctx",
        ]
        assert all(param in params for param in expected_params)

    def test_export_history_signature(self) -> None:
        """Test export_history has correct function signature."""
        import inspect

        sig = inspect.signature(export_history)
        params = list(sig.parameters.keys())

        expected_params = ["session_id", "file_path", "format", "ctx"]
        assert all(param in params for param in expected_params)
