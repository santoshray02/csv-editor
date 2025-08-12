# CSV Editor Examples

This directory contains example scripts demonstrating how to use the CSV Editor MCP Server.

## Available Examples

### basic_usage.py
Demonstrates basic CSV operations:
- Loading CSV data
- Calculating statistics
- Filtering data
- Sorting data
- Exporting to different formats

**Run it:**
```bash
uv run python examples/basic_usage.py
```

### demo.py
Comprehensive feature demonstration:
- Data quality assessment
- Statistical analysis
- High performer analysis
- Data profiling
- Correlation detection

**Run it:**
```bash
uv run python examples/demo.py
```

## Creating Your Own Examples

To create your own example:

1. Import the necessary tools:
```python
from src.csv_editor.tools.io_operations import load_csv_from_content
from src.csv_editor.tools.transformations import filter_rows
from src.csv_editor.tools.analytics import get_statistics
```

2. Load your data and get a session ID
3. Perform operations using the session ID
4. Export or analyze results

See the existing examples for detailed patterns.