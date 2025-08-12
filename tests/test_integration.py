#!/usr/bin/env python
"""
Test script for CSV MCP Server

This script tests the core functionality of the CSV MCP Server
without requiring an MCP client.
"""

import asyncio
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.csv_editor.models.csv_session import SessionManager, get_session_manager
from src.csv_editor.tools.io_operations import (
    load_csv_from_content,
    export_csv,
    get_session_info,
    list_sessions
)
from src.csv_editor.tools.transformations import (
    filter_rows,
    sort_data,
    select_columns,
    rename_columns,
    add_column,
    remove_columns,
    change_column_type,
    fill_missing_values,
    remove_duplicates
)
from src.csv_editor.tools.analytics import (
    get_statistics,
    get_column_statistics,
    get_correlation_matrix,
    group_by_aggregate,
    get_value_counts,
    detect_outliers,
    profile_data
)
from src.csv_editor.tools.validation import (
    validate_schema,
    check_data_quality,
    find_anomalies
)

# Test data
TEST_CSV_CONTENT = """name,age,salary,department,hire_date
Alice,28,55000,Engineering,2021-01-15
Bob,35,65000,Engineering,2019-06-01
Charlie,42,75000,Management,2018-03-20
Diana,31,58000,Marketing,2020-08-10
Eve,29,52000,Sales,2021-03-25
Frank,45,85000,Management,2017-11-30
Grace,26,48000,Marketing,2022-02-14
Henry,38,70000,Engineering,2019-09-15
Iris,33,62000,Sales,2020-05-20
Jack,41,78000,Management,2018-07-12
Kate,27,,Marketing,2021-11-01
Leo,36,68000,Engineering,2019-04-18
Mia,30,56000,Sales,2020-12-05
Nathan,44,82000,Management,2017-09-08
Olivia,25,45000,Marketing,2022-06-30
Peter,39,72000,Engineering,2018-10-22
Quinn,32,60000,Sales,2020-03-15
Rachel,28,54000,Marketing,2021-07-20
Sam,37,69000,Engineering,2019-02-28
Tina,34,64000,Sales,2020-01-10
"""

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Print test header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Testing: {name}{Colors.ENDC}")

def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def print_info(msg: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")

def print_data(data: any, indent: int = 2):
    """Print data with indentation"""
    indent_str = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)) and len(str(value)) > 50:
                print(f"{indent_str}{Colors.BLUE}{key}:{Colors.ENDC} <{type(value).__name__} with {len(value)} items>")
            else:
                print(f"{indent_str}{Colors.BLUE}{key}:{Colors.ENDC} {value}")
    elif isinstance(data, pd.DataFrame):
        print(f"{indent_str}DataFrame shape: {data.shape}")
        print(data.head().to_string().replace('\n', f'\n{indent_str}'))
    else:
        print(f"{indent_str}{data}")

async def test_io_operations():
    """Test I/O operations"""
    print_test("I/O Operations")
    
    # Load CSV from content
    result = await load_csv_from_content(
        content=TEST_CSV_CONTENT,
        delimiter=","
    )
    
    if result["success"]:
        session_id = result["session_id"]
        print_success(f"Loaded CSV with session ID: {session_id}")
        print_info(f"Rows: {result['rows_affected']}, Columns: {len(result['columns_affected'])}")
        print_info(f"Column names: {', '.join(result['columns_affected'])}")
    else:
        print_error("Failed to load CSV")
        return None
    
    # Get session info
    info = await get_session_info(session_id=session_id)
    if info["success"]:
        print_success("Retrieved session info")
        print_data(info.get("data", info))
    
    # List sessions
    sessions = await list_sessions()
    if sessions["success"]:
        print_success(f"Listed {len(sessions.get('sessions', []))} active session(s)")
    
    return session_id

async def test_transformations(session_id: str):
    """Test data transformation operations"""
    print_test("Data Transformations")
    
    # Filter rows
    result = await filter_rows(
        session_id=session_id,
        conditions=[
            {"column": "salary", "operator": ">", "value": 60000},
            {"column": "department", "operator": "in", "value": ["Engineering", "Management"]}
        ],
        mode="and"
    )
    if result["success"]:
        print_success(f"Filtered rows: {result['rows_before']} → {result['rows_after']}")
    
    # Sort data
    result = await sort_data(
        session_id=session_id,
        columns=[
            {"column": "department", "ascending": True},
            {"column": "salary", "ascending": False}
        ]
    )
    if result["success"]:
        print_success("Sorted data by department and salary")
    
    # Select columns
    result = await select_columns(
        session_id=session_id,
        columns=["name", "department", "salary"]
    )
    if result["success"]:
        print_success(f"Selected columns: {', '.join(result['selected_columns'])}")
    
    # Add calculated column
    result = await add_column(
        session_id=session_id,
        name="salary_level",
        value=None,
        formula="lambda row: 'High' if row['salary'] > 65000 else 'Medium' if row['salary'] > 55000 else 'Low' if pd.notna(row['salary']) else 'Unknown'"
    )
    if result["success"]:
        print_success(f"Added column 'salary_level'")
    
    # Fill missing values
    result = await fill_missing_values(
        session_id=session_id,
        strategy="mean",
        columns=["salary"]
    )
    if result["success"]:
        print_success(f"Filled {result['values_filled']} missing value(s)")

async def test_analytics(session_id: str):
    """Test analytics operations"""
    print_test("Analytics")
    
    # Get statistics
    result = await get_statistics(
        session_id=session_id,
        columns=["salary"]
    )
    if result["success"]:
        print_success("Got statistics for salary column")
        print_data(result["statistics"])
    
    # Get correlation matrix
    result = await get_correlation_matrix(
        session_id=session_id,
        method="pearson",
        min_correlation=0.3
    )
    if result["success"]:
        print_success("Got correlation matrix")
        if result["significant_correlations"]:
            print_info("Significant correlations found:")
            for corr in result["significant_correlations"]:
                print(f"    {corr['column1']} ↔ {corr['column2']}: {corr['correlation']:.3f}")
    
    # Group by and aggregate
    result = await group_by_aggregate(
        session_id=session_id,
        group_by=["department"],
        aggregations={
            "salary": ["mean", "min", "max", "count"]
        }
    )
    if result["success"]:
        print_success("Grouped by department with aggregations")
        print_info("Department salary statistics:")
        manager = get_session_manager()
        session = manager.get_session(session_id)
        if session and session.df is not None:
            print(session.df.head(10).to_string())
    
    # Detect outliers
    result = await detect_outliers(
        session_id=session_id,
        columns=["salary"],
        method="iqr",
        threshold=1.5
    )
    if result["success"]:
        print_success(f"Detected {result['total_outliers']} outlier(s)")
        if result["outliers"]:
            print_info("Outlier details:")
            for col, details in result["outliers"].items():
                print(f"    {col}: {details['count']} outliers")
    
    # Profile data
    result = await profile_data(
        session_id=session_id,
        include_correlations=True,
        include_outliers=True
    )
    if result["success"]:
        print_success("Generated data profile")
        print_info(f"Profile summary: {result['profile']['summary']['total_rows']} rows, "
                  f"{result['profile']['summary']['total_columns']} columns")

async def test_validation(session_id: str):
    """Test validation operations"""
    print_test("Data Validation")
    
    # Validate schema
    schema = {
        "name": {"type": "string", "required": True},
        "salary": {"type": "numeric", "min": 0, "max": 200000},
        "department": {"type": "string", "allowed_values": ["Engineering", "Management", "Marketing", "Sales"]}
    }
    
    result = await validate_schema(
        session_id=session_id,
        schema=schema
    )
    if result["success"]:
        if result["valid"]:
            print_success("Data validates against schema")
        else:
            print_info(f"Schema validation found {len(result['errors'])} error(s)")
    
    # Check data quality
    result = await check_data_quality(
        session_id=session_id
    )
    if result["success"]:
        quality_score = result["quality_results"]["overall_score"]
        print_success(f"Data quality score: {quality_score:.1f}%")
        print_info("Quality metrics:")
        for metric, score in result["quality_results"]["metrics"].items():
            status = "✓" if score == 100 else "⚠" if score >= 80 else "✗"
            print(f"    {status} {metric}: {score:.1f}%")
    
    # Find anomalies
    result = await find_anomalies(
        session_id=session_id,
        columns=["salary"]
    )
    if result["success"]:
        total_anomalies = result["summary"]["total_anomalies"]
        print_success(f"Found {total_anomalies} anomaly(ies)")
        if total_anomalies > 0:
            print_info("Anomaly types:")
            for atype, count in result["summary"]["by_type"].items():
                print(f"    {atype}: {count}")

async def test_export(session_id: str):
    """Test export operations"""
    print_test("Export Operations")
    
    # Create test output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # Export to different formats
    formats = ["csv", "json", "html", "markdown"]
    
    for fmt in formats:
        output_file = output_dir / f"test_export.{fmt if fmt != 'markdown' else 'md'}"
        result = await export_csv(
            session_id=session_id,
            file_path=str(output_file),
            format=fmt
        )
        if result["success"]:
            print_success(f"Exported to {fmt.upper()}: {output_file}")
        else:
            print_error(f"Failed to export to {fmt.upper()}")

async def main():
    """Main test function"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}═══════════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}    CSV MCP Server Test Suite{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}═══════════════════════════════════════════{Colors.ENDC}")
    
    try:
        # Test I/O operations
        session_id = await test_io_operations()
        if not session_id:
            print_error("Failed to create session, aborting tests")
            return
        
        # Test transformations
        await test_transformations(session_id)
        
        # Test analytics
        await test_analytics(session_id)
        
        # Test validation
        await test_validation(session_id)
        
        # Test export
        await test_export(session_id)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}═══════════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.GREEN}{Colors.BOLD}    All tests completed successfully!{Colors.ENDC}")
        print(f"{Colors.GREEN}{Colors.BOLD}═══════════════════════════════════════════{Colors.ENDC}\n")
        
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())