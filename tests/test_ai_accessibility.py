"""Tests for AI accessibility features in CSV Editor."""

import pytest

from src.csv_editor.models import get_session_manager
from src.csv_editor.tools.io_operations import load_csv_from_content
from src.csv_editor.tools.transformations import (
    delete_row,
    extract_from_column,
    fill_column_nulls,
    find_cells_with_value,
    get_cell_value,
    get_column_data,
    get_data_summary,
    get_row_data,
    insert_row,
    inspect_data_around,
    replace_in_column,
    set_cell_value,
    split_column,
    strip_column,
    transform_column_case,
    update_row,
)


@pytest.fixture
async def ai_test_session():
    """Create a test session with sample data for AI accessibility testing."""
    sample_data = """name,age,city,email
John Doe,30,New York City,john.doe@email.com
Jane Smith,25,Los Angeles,jane.smith@email.com
Bob Johnson,35,  Chicago  ,bob.johnson@email.com
Alice Brown,28,,alice.brown@email.com"""

    result = await load_csv_from_content(content=sample_data, delimiter=",")
    yield result["session_id"]

    # Cleanup
    manager = get_session_manager()
    await manager.remove_session(result["session_id"])


@pytest.mark.asyncio
class TestCellLevelAccess:
    """Test cell-level access methods."""

    async def test_get_cell_value_by_name(self, ai_test_session) -> None:
        """Test getting cell value by column name."""
        result = await get_cell_value(ai_test_session, 0, "name")

        assert result["success"]
        assert result["value"] == "John Doe"
        assert result["coordinates"] == {"row": 0, "column": "name"}
        assert "data_type" in result

    async def test_get_cell_value_by_index(self, ai_test_session) -> None:
        """Test getting cell value by column index."""
        result = await get_cell_value(ai_test_session, 1, 1)  # Jane's age

        assert result["success"]
        assert result["value"] == 25
        assert result["coordinates"]["row"] == 1
        assert result["coordinates"]["column"] == "age"

    async def test_get_cell_value_invalid_coordinates(self, ai_test_session) -> None:
        """Test error handling for invalid coordinates."""
        # Invalid row
        result = await get_cell_value(ai_test_session, 999, "name")
        assert not result["success"]
        assert "out of range" in result["error"]

        # Invalid column name
        result = await get_cell_value(ai_test_session, 0, "nonexistent")
        assert not result["success"]
        assert "not found" in result["error"]

        # Invalid column index
        result = await get_cell_value(ai_test_session, 0, 999)
        assert not result["success"]
        assert "out of range" in result["error"]

    async def test_set_cell_value_success(self, ai_test_session) -> None:
        """Test setting cell values successfully."""
        # Set by column name
        result = await set_cell_value(ai_test_session, 0, "age", 31)

        assert result["success"]
        assert result["old_value"] == 30
        assert result["new_value"] == 31
        assert result["coordinates"] == {"row": 0, "column": "age"}

        # Verify the change
        check_result = await get_cell_value(ai_test_session, 0, "age")
        assert check_result["value"] == 31

    async def test_get_row_data_complete(self, ai_test_session) -> None:
        """Test getting complete row data."""
        result = await get_row_data(ai_test_session, 0)

        assert result["success"]
        assert result["row_index"] == 0
        assert result["data"]["name"] == "John Doe"
        assert result["data"]["age"] == 30
        assert len(result["columns_included"]) == 4

    async def test_get_row_data_partial(self, ai_test_session) -> None:
        """Test getting partial row data."""
        result = await get_row_data(ai_test_session, 1, ["name", "age"])

        assert result["success"]
        assert result["data"] == {"name": "Jane Smith", "age": 25}
        assert result["columns_included"] == ["name", "age"]

    async def test_get_column_data_full(self, ai_test_session) -> None:
        """Test getting full column data."""
        result = await get_column_data(ai_test_session, "age")

        assert result["success"]
        assert result["column"] == "age"
        assert result["data"] == [30, 25, 35, 28]
        assert result["count"] == 4

    async def test_get_column_data_slice(self, ai_test_session) -> None:
        """Test getting column data slice."""
        result = await get_column_data(ai_test_session, "name", 1, 3)

        assert result["success"]
        assert result["data"] == ["Jane Smith", "Bob Johnson"]
        assert result["start_row"] == 1
        assert result["end_row"] == 3


@pytest.mark.asyncio
class TestFocusedColumnOperations:
    """Test focused column operation methods."""

    async def test_replace_in_column(self, ai_test_session) -> None:
        """Test pattern replacement in column."""
        result = await replace_in_column(ai_test_session, "name", "John", "Jonathan")

        assert result["success"]
        assert result["operation"] == "replace"
        assert "John Doe" in result["original_sample"]
        assert "Jonathan Doe" in result["updated_sample"]

    async def test_extract_from_column(self, ai_test_session) -> None:
        """Test regex extraction from column."""
        # Use simpler extraction that returns single value
        result = await extract_from_column(ai_test_session, "email", r"([^@]+)")

        assert result["success"]
        assert result["operation"] == "extract"

    async def test_split_column_keep_part(self, ai_test_session) -> None:
        """Test column splitting keeping specific part."""
        result = await split_column(ai_test_session, "name", " ", 0)

        assert result["success"]
        assert result["operation"] == "split"
        assert result["part_index"] == 0

    async def test_transform_column_case(self, ai_test_session) -> None:
        """Test case transformation."""
        result = await transform_column_case(ai_test_session, "city", "upper")

        assert result["success"]
        assert result["transform"] == "upper"

    async def test_strip_column(self, ai_test_session) -> None:
        """Test column stripping."""
        result = await strip_column(ai_test_session, "city")

        assert result["success"]
        assert result["operation"] == "strip"

    async def test_fill_column_nulls(self, ai_test_session) -> None:
        """Test filling null values in column."""
        result = await fill_column_nulls(ai_test_session, "city", "Unknown")

        assert result["success"]
        assert result["operation"] == "fill_nulls"
        assert result["nulls_filled"] >= 0


@pytest.mark.asyncio
class TestRowManipulation:
    """Test row manipulation methods."""

    async def test_insert_row_dict(self, ai_test_session) -> None:
        """Test inserting row with dictionary data."""
        new_data = {"name": "Carol White", "age": 32, "city": "Seattle", "email": "carol@email.com"}
        result = await insert_row(ai_test_session, 1, new_data)

        assert result["success"]
        assert result["operation"] == "insert_row"
        assert result["row_index"] == 1
        assert result["rows_after"] == 5  # Original 4 + 1 new

    async def test_insert_row_list(self, ai_test_session) -> None:
        """Test inserting row with list data."""
        new_data = ["David Lee", 29, "Portland", "david@email.com"]
        result = await insert_row(ai_test_session, -1, new_data)  # Append

        assert result["success"]
        assert result["rows_after"] == 5

    async def test_insert_row_with_null_dict(self, ai_test_session) -> None:
        """Test inserting row with null values in dictionary data."""
        # Test dict with null values (simulating JSON null -> Python None)
        new_data = {"name": "Alice Null", "age": None, "city": "Portland", "email": None}
        result = await insert_row(ai_test_session, 1, new_data)

        assert result["success"], f"insert_row with null dict failed: {result.get('error')}"
        assert result["operation"] == "insert_row"
        assert result["row_index"] == 1
        assert result["rows_after"] == 5  # Original 4 + 1 new

        # Verify the null values were inserted correctly
        row_result = await get_row_data(ai_test_session, 1)
        assert row_result["success"]
        assert row_result["data"]["name"] == "Alice Null"
        assert row_result["data"]["age"] is None
        assert row_result["data"]["city"] == "Portland"
        assert row_result["data"]["email"] is None

    async def test_insert_row_with_null_list(self, ai_test_session) -> None:
        """Test inserting row with null values in list data."""
        # Test list with null values (simulating JSON null -> Python None)
        new_data = ["Bob Null", None, "Seattle", None]
        result = await insert_row(ai_test_session, -1, new_data)  # Append

        assert result["success"], f"insert_row with null list failed: {result.get('error')}"
        assert result["operation"] == "insert_row"
        assert result["rows_after"] == 5

        # Verify the null values were inserted correctly
        row_result = await get_row_data(ai_test_session, 4)  # Last row (0-indexed)
        assert row_result["success"]
        assert row_result["data"]["name"] == "Bob Null"
        assert row_result["data"]["age"] is None
        assert row_result["data"]["city"] == "Seattle"
        assert row_result["data"]["email"] is None

    async def test_insert_row_partial_data_with_nulls(self, ai_test_session) -> None:
        """Test inserting row with partial data that gets filled with None."""
        # Test dict with missing columns (should be filled with None)
        new_data = {"name": "Charlie Partial", "city": "Miami"}  # Missing age and email
        result = await insert_row(ai_test_session, 2, new_data)

        assert result["success"], f"insert_row with partial data failed: {result.get('error')}"
        assert result["operation"] == "insert_row"

        # Verify missing columns were filled with None
        row_result = await get_row_data(ai_test_session, 2)
        assert row_result["success"]
        assert row_result["data"]["name"] == "Charlie Partial"
        assert row_result["data"]["age"] is None  # Should be filled with None
        assert row_result["data"]["city"] == "Miami"
        assert row_result["data"]["email"] is None  # Should be filled with None

    async def test_insert_row_with_json_string(self, ai_test_session) -> None:
        """Test inserting row with JSON string (Claude Code compatibility)."""
        import json

        # Test JSON string with null values (as Claude Code would send)
        json_data_dict = {"name": "JSON Test", "age": None, "city": "Portland", "email": None}
        json_string = json.dumps(json_data_dict)

        result = await insert_row(ai_test_session, 1, json_string)

        assert result["success"], f"insert_row with JSON string failed: {result.get('error')}"
        assert result["operation"] == "insert_row"
        assert result["row_index"] == 1
        assert result["rows_after"] == 5

        # Verify the data was parsed correctly from JSON string
        row_result = await get_row_data(ai_test_session, 1)
        assert row_result["success"]
        assert row_result["data"]["name"] == "JSON Test"
        assert row_result["data"]["age"] is None
        assert row_result["data"]["city"] == "Portland"
        assert row_result["data"]["email"] is None

    async def test_update_row_with_json_string(self, ai_test_session) -> None:
        """Test updating row with JSON string (Claude Code compatibility)."""
        import json

        # Test JSON string update with null values
        update_dict = {"age": None, "city": "Updated City", "email": None}
        json_string = json.dumps(update_dict)

        result = await update_row(ai_test_session, 0, json_string)

        assert result["success"], f"update_row with JSON string failed: {result.get('error')}"
        assert result["operation"] == "update_row"
        assert result["columns_updated"] == ["age", "city", "email"]

        # Verify the updates were applied correctly
        assert result["new_values"]["age"] is None
        assert result["new_values"]["city"] == "Updated City"
        assert result["new_values"]["email"] is None

    async def test_insert_row_invalid_json_string(self, ai_test_session) -> None:
        """Test insert_row with invalid JSON string returns clear error."""
        invalid_json = '{"name": "test", invalid json here}'

        result = await insert_row(ai_test_session, -1, invalid_json)

        assert not result["success"]
        assert "Invalid JSON string" in result["error"]

    async def test_delete_row(self, ai_test_session) -> None:
        """Test deleting a row."""
        # First, check what's in row 1
        row_data = await get_row_data(ai_test_session, 1)
        original_name = row_data["data"]["name"]

        result = await delete_row(ai_test_session, 1)

        assert result["success"]
        assert result["operation"] == "delete_row"
        assert result["deleted_data"]["name"] == original_name
        assert result["rows_after"] == 3  # Original 4 - 1

    async def test_update_row(self, ai_test_session) -> None:
        """Test updating specific columns in a row."""
        updates = {"age": 31, "city": "Boston"}
        result = await update_row(ai_test_session, 0, updates)

        assert result["success"]
        assert result["operation"] == "update_row"
        assert result["changes_made"] == 2
        assert "age" in result["columns_updated"]
        assert "city" in result["columns_updated"]

        # Verify the changes
        row_check = await get_row_data(ai_test_session, 0)
        assert row_check["data"]["age"] == 31
        assert row_check["data"]["city"] == "Boston"


@pytest.mark.asyncio
class TestAIConvenienceMethods:
    """Test AI-friendly convenience methods."""

    async def test_inspect_data_around(self, ai_test_session) -> None:
        """Test data inspection around a cell."""
        result = await inspect_data_around(ai_test_session, 1, "name", 1)

        assert result["success"]
        assert result["center_coordinates"]["row"] == 1
        assert result["center_coordinates"]["column"] == "name"
        assert "inspection_area" in result
        assert "data" in result

    async def test_find_cells_with_value_exact(self, ai_test_session) -> None:
        """Test finding cells with exact value match."""
        result = await find_cells_with_value(ai_test_session, 30)

        assert result["success"]
        assert result["exact_match"]
        assert result["matches_found"] >= 1
        assert any(match["coordinates"]["column"] == "age" for match in result["matches"])

    async def test_find_cells_with_value_column_specific(self, ai_test_session) -> None:
        """Test finding cells in specific column."""
        result = await find_cells_with_value(ai_test_session, 25, "age")

        assert result["success"]
        assert result["search_column"] == "age"
        assert result["matches_found"] >= 1

    async def test_find_cells_substring(self, ai_test_session) -> None:
        """Test finding cells with substring matching."""
        result = await find_cells_with_value(ai_test_session, "john", None, False)

        assert result["success"]
        assert not result["exact_match"]
        # Should find "john.doe@email.com" and possibly "Bob Johnson"

    async def test_get_data_summary_with_preview(self, ai_test_session) -> None:
        """Test comprehensive data summary with preview."""
        result = await get_data_summary(ai_test_session, True, 3)

        assert result["success"]
        assert "coordinate_system" in result
        assert "shape" in result
        assert "columns" in result
        assert "data_types" in result
        assert "missing_data" in result
        assert "preview" in result
        assert result["shape"]["rows"] == 4
        assert result["shape"]["columns"] == 4

    async def test_get_data_summary_without_preview(self, ai_test_session) -> None:
        """Test data summary without preview."""
        result = await get_data_summary(ai_test_session, False)

        assert result["success"]
        assert "preview" not in result
        assert "shape" in result


@pytest.mark.asyncio
class TestEnhancedDataReturns:
    """Test enhanced data returns with indexing."""

    async def test_load_csv_enhanced_preview(self) -> None:
        """Test that loaded CSV includes enhanced preview with indices."""
        result = await load_csv_from_content("name,age\nJohn,30\nJane,25")

        assert result["success"]
        assert "preview" in result["data"]

        preview = result["data"]["preview"]
        assert "records" in preview
        assert "total_rows" in preview
        assert "columns" in preview

        # Check that records include row indices
        for record in preview["records"]:
            assert "__row_index__" in record

        # Cleanup
        manager = get_session_manager()
        await manager.remove_session(result["session_id"])


@pytest.mark.asyncio
class TestCoordinateSystemValidation:
    """Test coordinate system validation and error handling."""

    async def test_coordinate_bounds_validation(self, ai_test_session) -> None:
        """Test that coordinate bounds are properly validated."""
        # Test row bounds
        result = await get_cell_value(ai_test_session, -1, "name")
        assert not result["success"]

        result = await get_cell_value(ai_test_session, 999, "name")
        assert not result["success"]

        # Test column bounds
        result = await get_cell_value(ai_test_session, 0, -1)
        assert not result["success"]

        result = await get_cell_value(ai_test_session, 0, 999)
        assert not result["success"]

    async def test_coordinate_information_in_responses(self, ai_test_session) -> None:
        """Test that responses include proper coordinate information."""
        # Cell operations should include coordinates
        result = await get_cell_value(ai_test_session, 0, "name")
        assert "coordinates" in result
        assert result["coordinates"]["row"] == 0
        assert result["coordinates"]["column"] == "name"

        # Row operations should include row index
        result = await get_row_data(ai_test_session, 0)
        assert "row_index" in result
        assert result["row_index"] == 0

        # Column operations should include range info
        result = await get_column_data(ai_test_session, "age", 0, 2)
        assert "start_row" in result
        assert "end_row" in result


@pytest.mark.asyncio
class TestMethodDiscoverabilityAndDocumentation:
    """Test that methods are discoverable and well-documented."""

    async def test_methods_have_clear_names(self) -> None:
        """Test that method names clearly express their intent."""
        # These tests verify the method names exist and are descriptive
        # The names should be self-explanatory without needing operation parameters

        # Cell access methods
        assert callable(get_cell_value)
        assert callable(set_cell_value)

        # Row access methods
        assert callable(get_row_data)
        assert callable(insert_row)
        assert callable(delete_row)
        assert callable(update_row)

        # Column access methods
        assert callable(get_column_data)

        # Focused column operations (no operation parameters!)
        assert callable(replace_in_column)
        assert callable(extract_from_column)
        assert callable(split_column)
        assert callable(transform_column_case)
        assert callable(strip_column)
        assert callable(fill_column_nulls)

        # AI convenience methods
        assert callable(inspect_data_around)
        assert callable(find_cells_with_value)
        assert callable(get_data_summary)

    async def test_comprehensive_error_messages(self, ai_test_session) -> None:
        """Test that error messages include helpful coordinate information."""
        # Row out of range should specify valid range
        result = await get_cell_value(ai_test_session, 999, "name")
        assert "0-3" in result["error"]  # Valid range for 4 rows

        # Column not found should be clear
        result = await get_cell_value(ai_test_session, 0, "invalid_col")
        assert "not found" in result["error"]


@pytest.mark.asyncio
class TestEnhancedPreviewFunctionality:
    """Test enhanced preview and data structure functionality."""

    async def test_preview_includes_coordinate_system(self, ai_test_session) -> None:
        """Test that data summary includes coordinate system documentation."""
        result = await get_data_summary(ai_test_session, True, 5)

        assert result["success"]
        assert "coordinate_system" in result
        assert "row_indexing" in result["coordinate_system"]
        assert "column_indexing" in result["coordinate_system"]

    async def test_enhanced_data_preview_structure(self, ai_test_session) -> None:
        """Test enhanced data returns with indexing."""
        result = await get_data_summary(ai_test_session, True, 3)

        assert result["success"]
        assert "preview" in result
        assert "records" in result["preview"]

        # Check that records include row indices
        for record in result["preview"]["records"]:
            assert "__row_index__" in record


@pytest.mark.asyncio
class TestIntegrationWorkflow:
    """Test complete AI workflow integration."""

    async def test_ai_inspection_workflow(self, ai_test_session) -> None:
        """Test complete workflow: summary → inspection → modification → verification."""
        # Step 1: Get data summary
        summary = await get_data_summary(ai_test_session)
        assert summary["success"]
        assert summary["shape"]["rows"] == 4

        # Step 2: Inspect specific area
        inspect_result = await inspect_data_around(ai_test_session, 1, "name", 1)
        assert inspect_result["success"]

        # Step 3: Find cells with specific pattern
        find_result = await find_cells_with_value(ai_test_session, "John", "name")
        assert find_result["success"]

        # Step 4: Modify specific cell
        if find_result["matches_found"] > 0:
            coords = find_result["matches"][0]["coordinates"]
            set_result = await set_cell_value(
                ai_test_session, coords["row"], coords["column"], "Jonathan Doe"
            )
            assert set_result["success"]

            # Step 5: Verify change
            verify_result = await get_cell_value(ai_test_session, coords["row"], coords["column"])
            assert verify_result["value"] == "Jonathan Doe"

    async def test_batch_row_operations(self, ai_test_session) -> None:
        """Test batch row operations maintaining coordinate consistency."""
        # Insert row
        insert_result = await insert_row(
            ai_test_session,
            2,
            {"name": "New Person", "age": 40, "city": "Denver", "email": "new@email.com"},
        )
        assert insert_result["success"]

        # Update inserted row
        update_result = await update_row(ai_test_session, 2, {"age": 41})
        assert update_result["success"]

        # Verify coordinates are consistent
        check_result = await get_row_data(ai_test_session, 2)
        assert check_result["data"]["name"] == "New Person"
        assert check_result["data"]["age"] == 41
