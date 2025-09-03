"""Basic unit tests for CSV Editor."""

import pytest

from src.csv_editor.models import get_session_manager
from src.csv_editor.utils.validators import sanitize_filename, validate_column_name, validate_url


class TestValidators:
    """Test validation utilities."""

    def test_validate_column_name(self):
        """Test column name validation."""
        # Valid names
        assert validate_column_name("age")[0]
        assert validate_column_name("first_name")[0]
        assert validate_column_name("_id")[0]

        # Invalid names
        assert not validate_column_name("123name")[0]
        assert not validate_column_name("name-with-dash")[0]
        assert not validate_column_name("")[0]

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("test.csv") == "test.csv"
        assert sanitize_filename("test<>file.csv") == "test__file.csv"
        assert sanitize_filename("../../../etc/passwd") == "passwd"

    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com/data.csv")[0]
        assert validate_url("http://localhost:8000/file.csv")[0]

        # Invalid URLs
        assert not validate_url("ftp://example.com/data.csv")[0]
        assert not validate_url("not-a-url")[0]


@pytest.mark.asyncio
class TestSessionManager:
    """Test session management."""

    async def test_create_session(self):
        """Test session creation."""
        manager = get_session_manager()
        session_id = manager.create_session()

        assert session_id is not None
        assert manager.get_session(session_id) is not None

        # Cleanup
        await manager.remove_session(session_id)

    async def test_session_cleanup(self):
        """Test session removal."""
        manager = get_session_manager()
        session_id = manager.create_session()

        # Session should exist
        assert manager.get_session(session_id) is not None

        # Remove session
        await manager.remove_session(session_id)

        # Session should not exist
        assert manager.get_session(session_id) is None


@pytest.mark.asyncio
class TestDataOperations:
    """Test basic data operations."""

    async def test_load_csv_from_content(self):
        """Test loading CSV from string content."""
        from src.csv_editor.tools.io_operations import load_csv_from_content

        csv_content = """a,b,c
1,2,3
4,5,6"""

        result = await load_csv_from_content(content=csv_content, delimiter=",")

        assert result["success"]
        assert result["rows_affected"] == 2
        assert len(result["columns_affected"]) == 3

        # Cleanup
        manager = get_session_manager()
        await manager.remove_session(result["session_id"])

    async def test_filter_rows(self, test_session):
        """Test filtering rows."""
        from src.csv_editor.tools.transformations import filter_rows

        result = await filter_rows(
            session_id=test_session,
            conditions=[{"column": "price", "operator": ">", "value": 50}],
            mode="and",
        )

        assert result["success"]
        assert result["rows_after"] < result["rows_before"]
