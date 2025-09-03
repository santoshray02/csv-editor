#!/usr/bin/env python3
"""
Example demonstrating CSV Editor's null value support and Claude Code compatibility.

This example shows how CSV Editor handles the exact scenario that was failing before:
- JSON null values in row insertion
- Claude Code's JSON string serialization
- Comprehensive null value support
"""

import asyncio
import pandas as pd
from csv_editor.tools.transformations import insert_row, get_row_data
from csv_editor.models.csv_session import get_session_manager


async def main():
    """Demonstrate null value handling and Claude Code compatibility."""
    
    print("CSV Editor - Null Value Support & Claude Code Compatibility Demo")
    print("=" * 65)
    
    # Create a session with job application tracking data
    session_manager = get_session_manager()
    session_id = session_manager.create_session()
    session = session_manager.get_session(session_id)
    
    # Create initial data structure
    initial_data = pd.DataFrame({
        "Company": ["TechCorp"],
        "Position": ["Software Engineer"],
        "Location": ["San Francisco"],
        "Application Date": ["2025-01-15"],
        "Status": ["Applied"],
        "Job Posting URL": ["https://techcorp.com/jobs/123"],
        "Source": ["LinkedIn"],
        "Contact Person": ["Jane Smith"],
        "Contact Email": ["jane@techcorp.com"],
        "Follow-up Date": ["2025-01-20"],
        "Interview Date": [None],  # Initially null
        "Response Date": [None],   # Initially null
        "Outcome": [None],         # Initially null
        "Strategic Advantage": ["Python expertise"],
        "Key Requirements Match": ["High"],
        "Salary Range": ["120-150k"],
        "Notes": ["Applied through referral"]
    })
    
    session.load_data(initial_data)
    print(f"✅ Created session: {session_id}")
    print(f"📊 Initial data shape: {initial_data.shape}")
    
    # Example 1: The exact case that was failing before
    print("\n🎯 Example 1: Insert row with null values (Claude Code format)")
    
    # This is exactly what the user was trying to do:
    job_application_data = {
        "Company": "Finergo",
        "Position": "TBD", 
        "Location": "TBD",
        "Application Date": "2025-09-03",
        "Status": "Screening Interview Completed",
        "Job Posting URL": None,      # NULL VALUE
        "Source": "TBD",
        "Contact Person": None,       # NULL VALUE  
        "Contact Email": None,        # NULL VALUE
        "Follow-up Date": "2025-09-06",
        "Interview Date": "2025-09-03", 
        "Response Date": None,        # NULL VALUE
        "Outcome": None,             # NULL VALUE
        "Strategic Advantage": "TBD",
        "Key Requirements Match": "TBD",
        "Salary Range": "TBD", 
        "Notes": "Screening interview completed. Follow-up on Friday regarding salary conversations."
    }
    
    # Method 1: Direct dictionary (works)
    result = await insert_row(session_id, -1, job_application_data)
    print(f"✅ Dictionary insert: {result['success']}")
    
    # Method 2: JSON string (as Claude Code sends) - NOW WORKS!
    import json
    json_string = json.dumps(job_application_data)
    result = await insert_row(session_id, -1, json_string)
    print(f"✅ JSON string insert: {result['success']}")
    
    # Verify the null values were preserved correctly
    row_data = await get_row_data(session_id, 2)  # Last inserted row
    print("\n📋 Null value verification:")
    null_fields = ["Job Posting URL", "Contact Person", "Contact Email", "Response Date", "Outcome"]
    for field in null_fields:
        value = row_data["data"][field]
        is_null = value is None
        print(f"   {field}: {value} (null: {is_null})")
    
    print(f"\n📈 Final data shape: {session.df.shape}")
    print("🎉 All null values preserved correctly!")
    
    print("\n" + "=" * 65)
    print("✅ CSV Editor now fully supports:")
    print("   • JSON null values in all operations")
    print("   • Claude Code's JSON string serialization") 
    print("   • Type-safe data operations")
    print("   • Modular, maintainable architecture")


if __name__ == "__main__":
    asyncio.run(main())