"""Pytest configuration for CSV Editor tests."""

import asyncio
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session", autouse=True)
def cleanup_history_files():
    """Clean up history files created during testing."""
    yield  # Let all tests run first

    # Clean up any history files created during testing
    project_root = Path(__file__).parent.parent
    for history_file in project_root.glob("history_*.json"):
        try:
            history_file.unlink()
        except (OSError, FileNotFoundError):
            pass  # File might already be removed


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
        delimiter=",",
    )

    yield result["session_id"]

    # Cleanup
    manager = get_session_manager()
    await manager.remove_session(result["session_id"])
