"""Basic unit tests for CSV Editor."""

import pytest
import pandas as pd
from src.csv_editor.models import get_session_manager
from src.csv_editor.utils.validators import (
    validate_column_name,
    sanitize_filename,
    validate_url
)

class TestValidators:
    """Test validation utilities."""
    
    def test_validate_column_name(self):
        """Test column name validation."""
        # Valid names
        assert validate_column_name("age")[0] == True
        assert validate_column_name("first_name")[0] == True
        assert validate_column_name("_id")[0] == True
        
        # Invalid names
        assert validate_column_name("123name")[0] == False
        assert validate_column_name("name-with-dash")[0] == False
        assert validate_column_name("")[0] == False
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("test.csv") == "test.csv"
        assert sanitize_filename("test<>file.csv") == "test__file.csv"
        assert sanitize_filename("../../../etc/passwd") == "passwd"
    
    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        assert validate_url("https://example.com/data.csv")[0] == True
        assert validate_url("http://localhost:8000/file.csv")[0] == True
        
        # Invalid URLs
        assert validate_url("ftp://example.com/data.csv")[0] == False
        assert validate_url("not-a-url")[0] == False

class TestSessionManager:
    """Test session management."""
    
    def test_create_session(self):
        """Test session creation."""
        manager = get_session_manager()
        session_id = manager.create_session()
        
        assert session_id is not None
        assert manager.get_session(session_id) is not None
        
        # Cleanup
        manager.remove_session(session_id)
    
    def test_session_cleanup(self):
        """Test session removal."""
        manager = get_session_manager()
        session_id = manager.create_session()
        
        # Session should exist
        assert manager.get_session(session_id) is not None
        
        # Remove session
        manager.remove_session(session_id)
        
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
        
        result = await load_csv_from_content(
            content=csv_content,
            delimiter=","
        )
        
        assert result["success"] == True
        assert result["rows_affected"] == 2
        assert len(result["columns_affected"]) == 3
        
        # Cleanup
        manager = get_session_manager()
        manager.remove_session(result["session_id"])
    
    async def test_filter_rows(self, test_session):
        """Test filtering rows."""
        from src.csv_editor.tools.transformations import filter_rows
        
        result = await filter_rows(
            session_id=test_session,
            conditions=[{"column": "price", "operator": ">", "value": 50}],
            mode="and"
        )
        
        assert result["success"] == True
        assert result["rows_after"] < result["rows_before"]