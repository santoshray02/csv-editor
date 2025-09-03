"""Tests for CSV Editor settings functionality."""

import os
import tempfile
from unittest.mock import patch

from src.csv_editor.models.csv_session import CSVSession, CSVSettings, get_csv_settings


class TestCSVSettings:
    """Test CSV settings configuration."""

    def test_default_settings(self):
        """Test default settings configuration."""
        settings = CSVSettings()
        assert settings.csv_history_dir == "."

    def test_settings_with_custom_dir(self):
        """Test settings with custom directory."""
        with tempfile.TemporaryDirectory() as custom_dir:
            settings = CSVSettings(csv_history_dir=custom_dir)
            assert settings.csv_history_dir == custom_dir

    def test_environment_variable_override(self):
        """Test that environment variable overrides default."""
        with (
            tempfile.TemporaryDirectory() as test_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": test_dir}),
        ):
            settings = CSVSettings()
            assert settings.csv_history_dir == test_dir

    def test_case_insensitive_env_var(self):
        """Test that environment variable is case insensitive."""
        with (
            tempfile.TemporaryDirectory() as test_dir,
            patch.dict(os.environ, {"csv_editor_csv_history_dir": test_dir}),
        ):
            settings = CSVSettings()
            assert settings.csv_history_dir == test_dir


class TestCSVSettingsIntegration:
    """Test CSV settings integration with sessions."""

    def test_get_csv_settings_singleton(self):
        """Test that get_csv_settings returns singleton instance."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": temp_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            settings1 = get_csv_settings()
            settings2 = get_csv_settings()
            assert settings1 is settings2
            assert settings1.csv_history_dir == temp_dir

    def test_session_uses_default_settings(self):
        """Test that CSVSession uses default settings."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": temp_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            session = CSVSession()

            assert session.history_manager is not None
            assert session.history_manager.history_dir == temp_dir

    def test_session_with_environment_variable(self):
        """Test that CSVSession uses environment variable settings."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as test_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": test_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            session = CSVSession()
            assert session.history_manager is not None
            assert session.history_manager.history_dir == test_dir

    def test_session_history_manager_initialization(self):
        """Test that history manager is properly initialized with settings."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": temp_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            session = CSVSession()

            # Verify history manager configuration
            assert session.history_manager is not None
            assert session.history_manager.history_dir == temp_dir
            assert session.history_manager.session_id == session.session_id
            assert session.history_manager.enable_snapshots is True
            assert session.history_manager.snapshot_interval == 5

    def test_settings_are_configurable(self):
        """Test that settings can be configured multiple ways."""
        with tempfile.TemporaryDirectory() as temp_dir1, tempfile.TemporaryDirectory() as temp_dir2:
            # Test 1: Direct instantiation
            settings1 = CSVSettings(csv_history_dir=temp_dir1)
            assert settings1.csv_history_dir == temp_dir1

            # Test 2: Environment variable
            with patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": temp_dir2}):
                settings2 = CSVSettings()
                assert settings2.csv_history_dir == temp_dir2

            # Test 3: Default
            with patch.dict(os.environ, {}, clear=True):
                # Clear any existing env vars
                if "CSV_EDITOR_CSV_HISTORY_DIR" in os.environ:
                    del os.environ["CSV_EDITOR_CSV_HISTORY_DIR"]
                settings3 = CSVSettings()
                assert settings3.csv_history_dir == "."

    def test_session_history_disabled(self):
        """Test that settings work even when history is disabled."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as temp_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": temp_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            session = CSVSession(enable_history=False)

            # History manager should be None when disabled
            assert session.history_manager is None
            # But settings should still be accessible
            settings = get_csv_settings()
            assert settings.csv_history_dir == temp_dir


class TestSettingsDocumentation:
    """Test that settings behavior matches documentation."""

    def test_env_prefix_documentation(self):
        """Test that CSV_EDITOR_ prefix works as documented."""
        with (
            tempfile.TemporaryDirectory() as test_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": test_dir}),
        ):
            settings = CSVSettings()
            assert settings.csv_history_dir == test_dir

    def test_default_current_directory(self):
        """Test that default is current directory as documented."""
        # Clear environment and test default value without creating files
        with patch.dict(os.environ, {}, clear=True):
            if "CSV_EDITOR_CSV_HISTORY_DIR" in os.environ:
                del os.environ["CSV_EDITOR_CSV_HISTORY_DIR"]

            settings = CSVSettings()
            assert settings.csv_history_dir == ".", "Default should be current directory"

    def test_integration_with_history_manager(self):
        """Test that HistoryManager receives the configured directory."""
        with (  # Requires Python 3.9+
            tempfile.TemporaryDirectory() as test_dir,
            patch.dict(os.environ, {"CSV_EDITOR_CSV_HISTORY_DIR": test_dir}),
            patch.object(
                __import__("src.csv_editor.models.csv_session", fromlist=["_settings"]),
                "_settings",
                None,
            ),
        ):
            session = CSVSession()

            # Verify the directory was passed to HistoryManager
            assert session.history_manager.history_dir == test_dir

            # Verify other HistoryManager parameters are still correctly set
            assert session.history_manager.session_id == session.session_id
            assert hasattr(session.history_manager, "storage_type")
            assert hasattr(session.history_manager, "enable_snapshots")
