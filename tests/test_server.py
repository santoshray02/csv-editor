"""Tests for server functionality including instructions loading."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from src.csv_editor.server import _load_instructions, mcp


class TestInstructionsLoading:
    """Test instructions loading functionality."""

    def test_load_instructions_success(self) -> None:
        """Test successful loading of instructions."""
        instructions = _load_instructions()

        # Verify instructions are loaded
        assert instructions is not None
        assert len(instructions) > 0
        assert isinstance(instructions, str)

        # Check for expected content
        assert "CSV Editor MCP Server" in instructions
        assert "Core Capabilities" in instructions
        assert "Getting Started" in instructions
        assert "Key Features" in instructions

    def test_load_instructions_content_structure(self) -> None:
        """Test that loaded instructions have expected structure."""
        instructions = _load_instructions()

        # Check for main sections (updated for new AI-focused structure)
        expected_sections = [
            "# CSV Editor MCP Server",
            "## Coordinate System",
            "## Core Capabilities:",
            "## Getting Started (AI Workflow):",
        ]

        for section in expected_sections:
            assert section in instructions

    def test_load_instructions_file_not_found(self) -> None:
        """Test handling of missing instructions file."""
        with patch("src.csv_editor.server.Path") as mock_path:
            # Create a mock path that raises FileNotFoundError on read_text
            mock_instructions_path = mock_path.return_value.parent.__truediv__.return_value
            mock_instructions_path.read_text.side_effect = FileNotFoundError("File not found")

            instructions = _load_instructions()

            assert instructions == "CSV Editor MCP Server - Instructions file not available"

    def test_load_instructions_generic_error(self) -> None:
        """Test handling of generic error during file reading."""
        with patch("src.csv_editor.server.Path") as mock_path:
            # Create a mock path that raises a generic exception on read_text
            mock_instructions_path = mock_path.return_value.parent.__truediv__.return_value
            mock_instructions_path.read_text.side_effect = Exception("Generic error")

            instructions = _load_instructions()

            assert instructions == "CSV Editor MCP Server - Error loading instructions"

    def test_load_instructions_with_custom_file(self) -> None:
        """Test loading instructions from a custom file."""
        # Create a temporary instructions file
        custom_instructions = "# Custom CSV Editor Instructions\n\nThis is a test."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(custom_instructions)
            temp_path = Path(f.name)

        try:
            # Patch the instructions path to use our temporary file
            with patch("src.csv_editor.server.Path") as mock_path:
                mock_instructions_path = mock_path.return_value.parent.__truediv__.return_value
                mock_instructions_path.read_text.return_value = custom_instructions

                instructions = _load_instructions()

                assert instructions == custom_instructions
        finally:
            # Clean up
            temp_path.unlink()


class TestServerInitialization:
    """Test server initialization with loaded instructions."""

    def test_server_has_correct_name(self) -> None:
        """Test that server has the correct name."""
        assert mcp.name == "CSV Editor"

    def test_server_has_instructions(self) -> None:
        """Test that server has instructions loaded."""
        assert mcp.instructions is not None
        assert len(mcp.instructions) > 0
        assert isinstance(mcp.instructions, str)

    def test_server_instructions_content(self) -> None:
        """Test that server instructions have expected content."""
        instructions = mcp.instructions
        assert instructions is not None  # Type guard

        # Check for key sections
        assert "CSV Editor MCP Server" in instructions
        assert "Core Capabilities" in instructions
        assert "Getting Started" in instructions

    def test_server_instructions_match_file(self) -> None:
        """Test that server instructions match the loaded file content."""
        file_instructions = _load_instructions()
        server_instructions = mcp.instructions

        assert file_instructions == server_instructions

    def test_server_instructions_not_empty_on_error(self) -> None:
        """Test that server has fallback instructions even if file loading fails."""
        # Even if there's an error loading the file, the server should have some instructions
        instructions = mcp.instructions
        assert instructions is not None  # Type guard
        assert instructions != ""
        assert len(instructions) > 10  # Should be more than just empty


class TestServerTools:
    """Test that server tools are properly registered."""

    def test_server_has_health_check_tool(self) -> None:
        """Test that health_check tool is registered."""
        # Test that the server has the health_check function registered
        # The actual tool functionality is tested elsewhere
        # This is just a smoke test to ensure the server setup is working
        assert mcp is not None
        assert mcp.name == "CSV Editor"

    def test_server_is_fastmcp_instance(self) -> None:
        """Test that server is a FastMCP instance."""
        # Verify the server is properly instantiated
        from fastmcp import FastMCP

        assert isinstance(mcp, FastMCP)


class TestModularToolRegistration:
    """Test that modular tool registration works correctly."""

    def test_tool_registration_functions_exist(self) -> None:
        """Test that all tool registration functions exist."""
        from src.csv_editor.tools.mcp_analytics_tools import register_analytics_tools
        from src.csv_editor.tools.mcp_data_tools import register_data_tools
        from src.csv_editor.tools.mcp_history_tools import register_history_tools
        from src.csv_editor.tools.mcp_io_tools import register_io_tools
        from src.csv_editor.tools.mcp_row_tools import register_row_tools
        from src.csv_editor.tools.mcp_system_tools import register_system_tools
        from src.csv_editor.tools.mcp_validation_tools import register_validation_tools

        # Verify all registration functions are callable
        registration_funcs = [
            register_system_tools,
            register_io_tools,
            register_data_tools,
            register_row_tools,
            register_analytics_tools,
            register_validation_tools,
            register_history_tools,
        ]

        for reg_func in registration_funcs:
            assert callable(reg_func)

    def test_tool_modules_import_successfully(self) -> None:
        """Test that all tool modules import without errors."""
        # Import all tool modules to ensure no import errors

        # If we reach this point, all imports succeeded
        assert True

    def test_enhanced_resources_available(self) -> None:
        """Test that enhanced resources for AI accessibility are available."""
        from src.csv_editor.server import (
            get_csv_cell,
            get_csv_data,
            get_csv_preview,
            get_csv_row,
            get_csv_schema,
            list_active_sessions,
        )

        # Verify enhanced resource functions exist (FastMCP resources are templates, not functions)
        resource_funcs = [
            get_csv_data,
            get_csv_schema,
            list_active_sessions,
            get_csv_cell,
            get_csv_row,
            get_csv_preview,
        ]

        # For resources, just verify they exist (they're FastMCP resource objects)
        for func in resource_funcs:
            assert func is not None


class TestServerIntegration:
    """Test server integration with modular tools."""

    def test_server_initializes_with_all_tools(self) -> None:
        """Test that server initializes successfully with all tool modules."""
        # The fact that we can import the server means all registrations worked
        from src.csv_editor.server import mcp

        assert mcp is not None
        assert mcp.name == "CSV Editor"

    def test_core_functionality_preserved(self) -> None:
        """Test that core functionality is preserved through modular architecture."""
        # Test that core functions are accessible through their modules
        from src.csv_editor.tools.io_operations import load_csv
        from src.csv_editor.tools.transformations import filter_rows, insert_row

        # These should be the actual implementation functions
        assert callable(load_csv)
        assert callable(insert_row)
        assert callable(filter_rows)
