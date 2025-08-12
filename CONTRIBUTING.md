# Contributing to CSV Editor

Thank you for your interest in contributing to CSV Editor! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Put the project's best interests first

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/santoshray02/csv-editor.git
   cd csv-editor
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/santoshray02/csv-editor.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher (3.11+ recommended)
- Git
- [uv](https://github.com/astral-sh/uv) - Ultra-fast package manager (required)

### Installation

#### Using uv (Required - 10-100x faster than pip)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on macOS: brew install uv
# Or with pip: pip install uv

# Clone and setup in one command!
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# That's it! You're ready to go in seconds!
```

#### Alternative: Using pip (slower, not recommended)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

**Note**: We standardize on `uv` for all development. It's significantly faster and handles everything pip does plus more.

### Verify Installation

```bash
# All commands use uv
uv run server --help
uv run test
uv run lint

# Or use the shortcuts defined in uv.toml
uv run all-checks  # Runs all quality checks
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow these guidelines:

- **One feature per PR** - Keep pull requests focused
- **Write tests** - All new features must have tests
- **Update docs** - Update README and docstrings as needed
- **Follow style guide** - Use Black, Ruff, and MyPy

### 3. Run Quality Checks

```bash
# All commands use uv for speed and consistency
uv run fmt         # Format code with Black
uv run lint        # Lint with Ruff
uv run type-check  # Type check with MyPy
uv run all-checks  # Run everything at once
```

### 4. Test Your Changes

```bash
# Testing with uv
uv run test                              # Run all tests
uv run test-cov                          # Run with coverage report
uv run pytest tests/test_transformations.py  # Run specific file
uv run pytest -k "test_filter"          # Run tests matching pattern
uv run pytest -x                         # Stop on first failure
```

## Code Standards

### Python Style

We use modern Python tooling for code quality:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting (replaces flake8, isort, and more)
- **MyPy** for type checking
- **Pre-commit** for automated checks

### Code Guidelines

1. **Type Hints**: All functions must have type hints
   ```python
   async def process_data(
       session_id: str,
       options: Dict[str, Any],
       ctx: Optional[Context] = None
   ) -> Dict[str, Any]:
       """Process data with given options."""
       ...
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
       """Analyze DataFrame and return statistics.
       
       Args:
           df: Input DataFrame to analyze
           
       Returns:
           Dictionary containing analysis results
           
       Raises:
           ValueError: If DataFrame is empty
       """
   ```

3. **Error Handling**: Use specific exceptions
   ```python
   if not session:
       raise ValueError(f"Session {session_id} not found")
   ```

4. **Async/Await**: Use async for all tool functions
   ```python
   @mcp.tool
   async def my_tool(param: str, ctx: Context) -> Dict[str, Any]:
       result = await async_operation(param)
       return {"success": True, "data": result}
   ```

5. **Logging**: Use appropriate log levels
   ```python
   logger.debug("Processing row %d", row_num)
   logger.info("Session %s created", session_id)
   logger.warning("Large dataset: %d rows", row_count)
   logger.error("Failed to load file: %s", error)
   ```

### File Structure

```
src/csv_editor/
├── __init__.py          # Package initialization
├── server.py            # Main server entry point
├── models/              # Data models and schemas
│   ├── __init__.py
│   ├── csv_session.py   # Session management
│   └── data_models.py   # Pydantic models
├── tools/               # MCP tool implementations
│   ├── __init__.py
│   ├── io_operations.py
│   ├── transformations.py
│   ├── analytics.py
│   └── validation.py
├── resources/           # MCP resources
├── prompts/            # MCP prompts
└── utils/              # Utility functions
```

## Testing

### Test Structure

```
tests/
├── unit/               # Unit tests
│   ├── test_models.py
│   ├── test_transformations.py
│   └── test_analytics.py
├── integration/        # Integration tests
│   ├── test_server.py
│   └── test_workflows.py
├── benchmark/          # Performance tests
│   └── test_performance.py
└── fixtures/           # Test data
    └── sample_data.csv
```

### Writing Tests

1. **Use pytest fixtures**:
   ```python
   @pytest.fixture
   async def session_with_data():
       """Create a session with sample data."""
       manager = get_session_manager()
       session_id = manager.create_session()
       # ... setup
       yield session_id
       # ... cleanup
       manager.remove_session(session_id)
   ```

2. **Test async functions**:
   ```python
   @pytest.mark.asyncio
   async def test_filter_rows(session_with_data):
       result = await filter_rows(
           session_id=session_with_data,
           conditions=[{"column": "age", "operator": ">", "value": 18}]
       )
       assert result["success"]
       assert result["rows_after"] < result["rows_before"]
   ```

3. **Use parametrize for multiple cases**:
   ```python
   @pytest.mark.parametrize("dtype,expected", [
       ("int", True),
       ("float", True),
       ("str", False),
   ])
   def test_is_numeric(dtype, expected):
       assert is_numeric_dtype(dtype) == expected
   ```

### Coverage Requirements

- Minimum coverage: 80%
- New features must have >90% coverage
- Run coverage: `hatch run test-cov`

## Documentation

### Docstring Standards

All public functions, classes, and modules must have docstrings:

```python
"""Module description.

This module provides functionality for X, Y, and Z.
"""

class DataProcessor:
    """Process CSV data with various transformations.
    
    Attributes:
        session_id: Unique session identifier
        df: Pandas DataFrame containing the data
    """
    
    def transform(
        self,
        operation: str,
        **kwargs: Any
    ) -> pd.DataFrame:
        """Apply transformation to data.
        
        Args:
            operation: Name of the transformation
            **kwargs: Additional parameters for the operation
            
        Returns:
            Transformed DataFrame
            
        Raises:
            ValueError: If operation is not supported
            
        Examples:
            >>> processor.transform("normalize", columns=["price"])
            >>> processor.transform("fill_missing", strategy="mean")
        """
```

### Updating Documentation

1. **README.md**: Update for new features or breaking changes
2. **API Docs**: Ensure docstrings are complete
3. **Examples**: Add examples for new features
4. **Changelog**: Update CHANGELOG.md

## Submitting Changes

### Pull Request Process

1. **Update your branch**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link related issues

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by at least one maintainer
3. **Address feedback** promptly
4. **Squash commits** if requested

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Create release PR**
4. **Tag release** after merge
5. **Publish to PyPI** (automated)

## Getting Help

- **Issues**: Use GitHub Issues for bugs and features
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord server (link in README)

## Recognition

Contributors are recognized in:
- AUTHORS.md file
- Release notes
- Project README

Thank you for contributing to CSV Editor! 🎉