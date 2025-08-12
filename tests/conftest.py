"""Pytest configuration for CSV Editor tests."""

import pytest
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_csv_data():
    """Provide sample CSV data for testing."""
    return """name,age,salary,department
Alice,30,60000,Engineering
Bob,25,50000,Marketing
Charlie,35,70000,Engineering
Diana,28,55000,Sales"""

@pytest.fixture
async def test_session():
    """Create a test session."""
    from src.csv_editor.models import get_session_manager
    from src.csv_editor.tools.io_operations import load_csv_from_content
    
    # Create session with sample data
    result = await load_csv_from_content(
        content="""product,price,quantity
Laptop,999.99,10
Mouse,29.99,50
Keyboard,79.99,25""",
        delimiter=","
    )
    
    yield result["session_id"]
    
    # Cleanup
    manager = get_session_manager()
    manager.remove_session(result["session_id"])