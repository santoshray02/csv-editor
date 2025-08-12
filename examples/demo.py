#!/usr/bin/env python
"""
CSV MCP Server Demo

Demonstrates the full capabilities of the CSV MCP Server.
Run this to see all features in action.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.csv_editor.tools.io_operations import load_csv_from_content
from src.csv_editor.tools.transformations import filter_rows, sort_data
from src.csv_editor.tools.analytics import get_statistics, profile_data
from src.csv_editor.tools.validation import check_data_quality

# Demo data
DEMO_CSV = """employee_id,name,department,salary,years_experience,performance_rating
1001,Alice Johnson,Engineering,95000,5,4.5
1002,Bob Smith,Marketing,65000,3,3.8
1003,Charlie Davis,Engineering,105000,7,4.7
1004,Diana Wilson,Sales,72000,4,4.2
1005,Eve Martinez,Engineering,88000,4,4.1
1006,Frank Brown,Marketing,58000,2,3.5
1007,Grace Lee,Sales,78000,5,4.4
1008,Henry Taylor,Engineering,115000,10,4.9
1009,Iris Chen,Marketing,70000,4,4.0
1010,Jack White,Sales,68000,3,3.9
"""

class Demo:
    @staticmethod
    def header(title: str):
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
    
    @staticmethod
    def success(msg: str):
        print(f"✅ {msg}")
    
    @staticmethod
    def info(msg: str):
        print(f"ℹ️  {msg}")
    
    @staticmethod
    def result(label: str, value: any):
        print(f"   {label}: {value}")

async def run_demo():
    Demo.header("CSV MCP Server - Feature Demo")
    
    # Load data
    Demo.info("Loading employee data...")
    result = await load_csv_from_content(content=DEMO_CSV)
    
    if not result["success"]:
        print(f"Error loading data: {result.get('error')}")
        return
    
    session_id = result["session_id"]
    Demo.success(f"Loaded {result['rows_affected']} employees")
    
    # Data Quality Check
    Demo.header("Data Quality Assessment")
    quality = await check_data_quality(session_id=session_id)
    
    if quality["success"]:
        metrics = quality["quality_results"]["metrics"]
        Demo.result("Overall Score", f"{quality['quality_results']['overall_score']:.1f}%")
        Demo.result("Completeness", f"{metrics['completeness']:.1f}%")
        Demo.result("Uniqueness", f"{metrics['uniqueness']:.1f}%")
        Demo.result("Consistency", f"{metrics['consistency']:.1f}%")
    
    # Statistics
    Demo.header("Salary Statistics by Department")
    stats = await get_statistics(
        session_id=session_id,
        columns=["salary", "years_experience", "performance_rating"]
    )
    
    if stats["success"]:
        salary_stats = stats["statistics"].get("salary", {})
        Demo.result("Average Salary", f"${salary_stats.get('mean', 0):,.2f}")
        Demo.result("Salary Range", f"${salary_stats.get('min', 0):,.0f} - ${salary_stats.get('max', 0):,.0f}")
        Demo.result("Median Salary", f"${salary_stats.get('50%', 0):,.2f}")
    
    # Filter high performers
    Demo.header("High Performers Analysis")
    filtered = await filter_rows(
        session_id=session_id,
        conditions=[
            {"column": "performance_rating", "operator": ">=", "value": 4.0},
            {"column": "salary", "operator": ">", "value": 70000}
        ],
        mode="and"
    )
    
    if filtered["success"]:
        Demo.success(f"Found {filtered['rows_after']} high performers")
        Demo.info(f"({filtered['rows_after']}/{filtered['rows_before']} = {filtered['rows_after']/filtered['rows_before']*100:.1f}% of employees)")
    
    # Profile the data
    Demo.header("Data Profile Summary")
    profile = await profile_data(
        session_id=session_id,
        include_correlations=True,
        include_outliers=False
    )
    
    if profile["success"]:
        summary = profile["profile"]["summary"]
        Demo.result("Total Rows", summary["total_rows"])
        Demo.result("Total Columns", summary["total_columns"])
        Demo.result("Numeric Columns", summary["numeric_columns"])
        Demo.result("Text Columns", summary["text_columns"])
        
        # Show correlations if any
        if "correlations" in profile["profile"]:
            correlations = profile["profile"]["correlations"]
            if "significant_correlations" in correlations:
                Demo.info("\nSignificant Correlations:")
                for corr in correlations["significant_correlations"][:3]:
                    Demo.result(
                        f"{corr['column1']} ↔ {corr['column2']}",
                        f"{corr['correlation']:.3f}"
                    )
    
    Demo.header("Demo Complete!")
    Demo.success("All features demonstrated successfully")
    Demo.info(f"Session ID: {session_id}")
    print()

if __name__ == "__main__":
    print("\n🚀 Starting CSV MCP Server Demo...\n")
    asyncio.run(run_demo())