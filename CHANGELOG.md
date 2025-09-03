# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-09-03

### Added
- **Null Value Support**: Comprehensive support for JSON `null` → Python `None` → pandas `NaN`
- **Claude Code Compatibility**: Automatic JSON string deserialization for complex parameters
- **Modular Tool Architecture**: Organized tools into logical modules (system, I/O, data, row, analytics, validation, history)
- **Enhanced Type Safety**: Replaced `Any` types with specific `CellValue`, `RowData`, `FilterCondition` types
- **JSON String Parsing**: `insert_row` and `update_row` now accept JSON strings from Claude Code
- **Comprehensive Test Coverage**: Added tests for null value scenarios and JSON string handling

### Changed
- **Tool Organization**: Moved FastMCP tool definitions from `server.py` to modular files in `tools/mcp_*.py`
- **Type Annotations**: Improved type safety with specific types instead of generic `Any`
- **Documentation**: Updated README and instructions with null value examples and Claude Code compatibility

### Fixed
- **Claude Code JSON Serialization**: Resolved "Data Validation" errors when Claude Code sends JSON strings
- **Null Value Insertion**: Fixed handling of null values in row insertion and updates
- **Test Architecture**: Refactored tests to parallel tool module structure

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

[1.0.0]: https://github.com/santoshray02/csv-editor/releases/tag/v1.0.0
