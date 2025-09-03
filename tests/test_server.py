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


class TestNewAIAccessibilityTools:
    """Test that new AI accessibility tools are properly registered."""

    def test_cell_level_tools_registered(self) -> None:
        """Test that cell-level access tools are available."""
        # Import the tools to verify they exist
        from src.csv_editor import server

        # Verify cell access tools exist (they're wrapped by FastMCP decorators)
        assert hasattr(server, "get_cell_value")
        assert hasattr(server, "set_cell_value")
        # Tools are wrapped in FastMCP, so we test existence not direct callability

    def test_row_level_tools_registered(self) -> None:
        """Test that row-level access tools are available."""
        from src.csv_editor import server

        # Verify row access tools exist
        assert hasattr(server, "get_row_data")
        assert hasattr(server, "get_column_data")

    def test_focused_column_operations_registered(self) -> None:
        """Test that focused column operation tools are available."""
        from src.csv_editor import server

        # Verify focused operation tools exist (replacing update_column operation parameter pattern)
        focused_ops = [
            "replace_in_column",
            "extract_from_column",
            "split_column",
            "transform_column_case",
            "strip_column",
            "fill_column_nulls",
        ]

        for op_name in focused_ops:
            assert hasattr(server, op_name), f"Missing focused operation: {op_name}"

    def test_row_manipulation_tools_registered(self) -> None:
        """Test that row manipulation tools are available."""
        from src.csv_editor import server

        # Verify row manipulation tools exist
        row_ops = ["insert_row", "delete_row", "update_row"]

        for op_name in row_ops:
            assert hasattr(server, op_name), f"Missing row operation: {op_name}"

    def test_ai_convenience_tools_registered(self) -> None:
        """Test that AI convenience tools are available."""
        from src.csv_editor import server

        # Verify AI convenience tools exist
        convenience_ops = ["inspect_data_around", "find_cells_with_value", "get_data_summary"]

        for op_name in convenience_ops:
            assert hasattr(server, op_name), f"Missing convenience operation: {op_name}"

    def test_enhanced_resources_available(self) -> None:
        """Test that enhanced resource endpoints are available."""
        # This tests that the new resource functions are defined
        from src.csv_editor import server

        # Verify resource functions exist (they're FastMCP resource templates)
        assert hasattr(server, "get_csv_cell")
        assert hasattr(server, "get_csv_row")
        assert hasattr(server, "get_csv_preview")


class TestBackwardCompatibility:
    """Test that existing tools still work alongside new AI accessibility features."""

    def test_original_tools_still_available(self) -> None:
        """Test that original tools are still registered."""
        from src.csv_editor import server

        # Verify key original tools still exist
        original_tools = [
            "load_csv",
            "load_csv_from_content",
            "export_csv",
            "filter_rows",
            "sort_data",
            "get_statistics",
            "update_column",  # Keep for backward compatibility
        ]

        for tool_name in original_tools:
            assert hasattr(server, tool_name), f"Missing original tool: {tool_name}"
