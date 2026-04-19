# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-04-20

### BREAKING CHANGES
- **Python floor raised to 3.11.** Users on Python 3.8, 3.9, or 3.10 must upgrade. Users who pinned `csv-editor>=1,<2` are unaffected.
- **`--transport sse` CLI option removed.** Use `--transport http` (Streamable HTTP) for remote deployments. This aligns with the MCP 2025-11-25 spec and FastMCP 3 guidance that SSE is "backward compatibility only, shouldn't be used in new projects."
- **FastMCP dependency bumped to `>=3.2,<4`.** Any code importing FastMCP APIs transitively may require updates per the [FastMCP 3 upgrade guide](https://gofastmcp.com/getting-started/upgrading/from-fastmcp-2).

### Added
- GitHub Actions `test.yml` workflow: pytest matrix on Python 3.11–3.14.
- `tests/test_server_boot.py` regression tests for server import, tool registry size, and CLI argument handling.
- Python 3.14 classifier and test coverage.
- Contributing guide: local virtualenv rebuild instructions.
- Design spec and implementation plan for the v2.0.0 migration under `specs/` and `plans/`.

### Changed
- Python floor: `>=3.10` → `>=3.11`.
- `fastmcp`: `>=2.11.3` → `>=3.2,<4` (resolved to 3.2.4).
- `pydantic`: `>=2.10.4` → `>=2.13`.
- `pydantic-settings`: `>=2.10.1` → `>=2.13`.
- `pyarrow`: `>=17.0.0` → `>=23`.
- `httpx`: `>=0.27.0` → `>=0.28`.
- `aiofiles`: `>=24.1.0` → `>=25`.
- `tabulate`: `>=0.9.0` → `>=0.10`.
- `black` target-version: `["py38", "py39", "py310", "py311", "py312", "py313"]` → `["py311", "py312", "py313"]` (black stable does not yet support `py314` as a target).
- `ruff` target-version: `py38` → `py311`.
- `mypy` python_version: `3.8` → `3.11`.
- Applied ruff `--fix` and `black` formatting across `src/` and `tests/` now that Python 3.11+ is the floor (large diff, no behavior change).
- Dockerfile base image pinned to `python:3.11-slim-bookworm`.
- `main()` signature: now accepts optional `argv: list[str] | None` for testability.
- README Python badge updated from `3.8+` to `3.11+`.

### Removed
- `--transport sse` CLI option.
- Python 3.8, 3.9, 3.10 classifier entries.

### Unchanged (deferred to follow-up release)
- `pandas>=2.2.3` and `numpy>=2.1.3`. Upgrading to pandas 3.0 (Copy-on-Write mandatory, Arrow-backed default string dtype) is deferred to a focused sub-project because the behavioral changes deserve dedicated test coverage.

## [1.0.1] - 2025-08-13

### Changed
- **Publishing strategy**: Switched to GitHub-based distribution due to PyPI naming conflicts
- **Installation method**: Primary installation now via `pip install git+https://github.com/santoshray02/csv-editor.git`
- **Package name**: Kept original `csv-editor` name

### Added
- Alternative publishing guide (ALTERNATIVE_PUBLISHING.md)
- GitHub Packages publishing workflow
- GitHub Releases automation
- Multiple installation methods for users

## [1.0.0] - 2025-08-13

### Added
- Initial release of CSV Editor MCP Server
- Core CSV operations: read, write, filter, transform
- Data validation and quality checks
- Statistical analysis and profiling capabilities
- Outlier detection and handling
- Support for multiple file formats (CSV, Excel, Parquet)
- Async operations for high performance
- Comprehensive error handling and logging
- FastMCP integration for seamless AI assistant integration
- Pandas-powered data manipulation
- Full test coverage with pytest
- Documentation with examples
- Type hints and mypy compatibility

### Features
- **File Operations**: Read/write CSV, Excel, Parquet files
- **Data Filtering**: Advanced filtering with multiple conditions
- **Data Transformation**: Column operations, data type conversions
- **Data Validation**: Schema validation, data quality checks
- **Statistical Analysis**: Descriptive statistics, correlation analysis
- **Outlier Detection**: Multiple algorithms (IQR, Z-score, Isolation Forest)
- **Data Profiling**: Comprehensive data profiling reports
- **Performance**: Optimized for large datasets with chunking support
- **AI Integration**: Seamless integration with Claude, ChatGPT, and other AI assistants

### Technical Details
- Python 3.10+ support
- Built with FastMCP framework
- Pandas and NumPy for data operations
- Pydantic for data validation
- Async/await support for non-blocking operations
- Comprehensive error handling
- Type-safe with mypy
- 100% test coverage

[2.0.0]: https://github.com/santoshray02/csv-editor/releases/tag/v2.0.0
[1.0.1]: https://github.com/santoshray02/csv-editor/releases/tag/v1.0.1
[1.0.0]: https://github.com/santoshray02/csv-editor/releases/tag/v1.0.0
