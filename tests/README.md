# CSV Editor Tests

Comprehensive test suite for the CSV Editor MCP Server.

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=src/csv_editor --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/test_basic.py
```

### Run integration tests
```bash
uv run pytest tests/test_integration.py
```

## Test Structure

- **test_basic.py** - Unit tests for core functionality
  - Validators
  - Session management
  - Basic operations

- **test_integration.py** - Full integration tests
  - Complete workflows
  - All tool operations
  - Export functionality

- **conftest.py** - Pytest configuration and fixtures
  - Session fixtures
  - Sample data fixtures
  - Event loop configuration

## Writing New Tests

All test files should:
1. Start with `test_`
2. Use pytest fixtures from conftest.py
3. Mark async tests with `@pytest.mark.asyncio`
4. Clean up sessions after tests

Example:
```python
@pytest.mark.asyncio
async def test_my_feature(test_session):
    """Test description."""
    from src.csv_editor.tools.analytics import get_statistics
    
    result = await get_statistics(
        session_id=test_session,
        columns=["price"]
    )
    
    assert result["success"] == True
```