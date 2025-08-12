#!/usr/bin/env python
"""
Basic usage example for CSV MCP Server

This script demonstrates basic CSV operations using the server's tools.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.csv_editor.tools.io_operations import (
    load_csv_from_content,
    export_csv,
    get_session_info
)
from src.csv_editor.tools.transformations import (
    filter_rows,
    sort_data,
    fill_missing_values
)
from src.csv_editor.tools.analytics import (
    get_statistics,
    get_column_statistics
)

# Sample CSV data
SAMPLE_DATA = """product,category,price,quantity,date
Laptop,Electronics,999.99,10,2024-01-15
Mouse,Electronics,29.99,50,2024-01-16
Desk,Furniture,299.99,5,2024-01-17
Chair,Furniture,149.99,15,2024-01-18
Keyboard,Electronics,79.99,25,2024-01-19
Monitor,Electronics,399.99,8,2024-01-20
Bookshelf,Furniture,199.99,7,2024-01-21
Headphones,Electronics,89.99,20,2024-01-22
Table,Furniture,499.99,3,2024-01-23
Webcam,Electronics,59.99,30,2024-01-24
"""

async def main():
    print("CSV MCP Server - Basic Usage Example")
    print("=" * 40)
    
    # 1. Load CSV data
    print("\n1. Loading CSV data...")
    result = await load_csv_from_content(
        content=SAMPLE_DATA,
        delimiter=","
    )
    
    if not result["success"]:
        print(f"Failed to load data: {result.get('error', 'Unknown error')}")
        return
    
    session_id = result["session_id"]
    print(f"✓ Loaded {result['rows_affected']} rows")
    print(f"  Session ID: {session_id}")
    print(f"  Columns: {', '.join(result['columns_affected'])}")
    
    # 2. Get statistics
    print("\n2. Calculating statistics...")
    stats = await get_statistics(
        session_id=session_id,
        columns=["price", "quantity"]
    )
    
    if stats["success"]:
        print("✓ Statistics calculated:")
        for col, col_stats in stats["statistics"].items():
            if isinstance(col_stats, dict):
                print(f"\n  {col}:")
                print(f"    Mean: ${col_stats.get('mean', 0):.2f}" if col == "price" else f"    Mean: {col_stats.get('mean', 0):.1f}")
                print(f"    Min: ${col_stats.get('min', 0):.2f}" if col == "price" else f"    Min: {col_stats.get('min', 0):.0f}")
                print(f"    Max: ${col_stats.get('max', 0):.2f}" if col == "price" else f"    Max: {col_stats.get('max', 0):.0f}")
    
    # 3. Filter data
    print("\n3. Filtering electronics over $50...")
    filtered = await filter_rows(
        session_id=session_id,
        conditions=[
            {"column": "category", "operator": "==", "value": "Electronics"},
            {"column": "price", "operator": ">", "value": 50}
        ],
        mode="and"
    )
    
    if filtered["success"]:
        print(f"✓ Filtered: {filtered['rows_before']} → {filtered['rows_after']} rows")
    
    # 4. Sort data
    print("\n4. Sorting by price (descending)...")
    sorted_result = await sort_data(
        session_id=session_id,
        columns=[{"column": "price", "ascending": False}]
    )
    
    if sorted_result["success"]:
        print("✓ Data sorted by price")
    
    # 5. Export results
    print("\n5. Exporting results...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Export as JSON
    json_file = output_dir / "filtered_products.json"
    export_result = await export_csv(
        session_id=session_id,
        file_path=str(json_file),
        format="json"
    )
    
    if export_result["success"]:
        print(f"✓ Exported to: {json_file}")
    
    # Export as CSV
    csv_file = output_dir / "filtered_products.csv"
    export_result = await export_csv(
        session_id=session_id,
        file_path=str(csv_file),
        format="csv"
    )
    
    if export_result["success"]:
        print(f"✓ Exported to: {csv_file}")
    
    print("\n" + "=" * 40)
    print("Example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())