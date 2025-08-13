#!/usr/bin/env python3
"""Example showing how to update the consignee name field using the new update_column function."""

import asyncio
from mcp_client import MCPClient


async def update_consignee_example():
    """Example of updating consignee field to keep only the company name."""
    
    # Initialize MCP client
    client = MCPClient()
    await client.connect("csv-editor")
    
    # Load the CSV file
    print("Loading CSV file...")
    result = await client.call_tool(
        "load_csv",
        {
            "file_path": "/home/santosh/projects/csv-editor/tests/sample_data/123456/1753698447530_BOL_Lubecon USA LLC_GHY 1.csv"
        }
    )
    session_id = result["session_id"]
    print(f"Session created: {session_id}")
    print(f"Loaded {result['row_count']} rows with {result['column_count']} columns")
    
    # Get current consignee value
    print("\nGetting current consignee value...")
    info_result = await client.call_tool(
        "get_session_info",
        {"session_id": session_id}
    )
    print(f"Columns: {info_result['columns'][:10]}...")  # Show first 10 columns
    
    # Method 1: Using 'split' operation to extract company name
    print("\n--- Method 1: Using 'split' operation ---")
    print("Extracting company name (everything before the dash)...")
    
    result = await client.call_tool(
        "update_column",
        {
            "session_id": session_id,
            "column": "Consignee Name",
            "operation": "split",
            "pattern": " -",  # Split on " -" (space and dash)
            "value": 0  # Take the first part (index 0)
        }
    )
    
    if result["success"]:
        print(f"✓ Column updated successfully!")
        print(f"  Original: {result['original_sample'][0] if result['original_sample'] else 'N/A'}")
        print(f"  Updated:  {result['updated_sample'][0] if result['updated_sample'] else 'N/A'}")
    
    # Export the result
    print("\nExporting updated CSV...")
    export_result = await client.call_tool(
        "export_csv",
        {
            "session_id": session_id,
            "file_path": "/tmp/updated_bol_method1.csv",
            "format": "csv"
        }
    )
    print(f"✓ Exported to: {export_result['file_path']}")
    
    # Close session
    await client.call_tool("close_session", {"session_id": session_id})
    
    # Method 2: Using 'replace' operation with regex
    print("\n--- Method 2: Using 'replace' with regex ---")
    
    # Load the file again
    result = await client.call_tool(
        "load_csv",
        {
            "file_path": "/home/santosh/projects/csv-editor/tests/sample_data/123456/1753698447530_BOL_Lubecon USA LLC_GHY 1.csv"
        }
    )
    session_id = result["session_id"]
    
    print("Removing location information using regex...")
    result = await client.call_tool(
        "update_column",
        {
            "session_id": session_id,
            "column": "Consignee Name",
            "operation": "replace",
            "pattern": r"\s*-.*$",  # Match everything from " -" to end of string
            "replacement": ""  # Replace with empty string
        }
    )
    
    if result["success"]:
        print(f"✓ Column updated successfully!")
        print(f"  Original: {result['original_sample'][0] if result['original_sample'] else 'N/A'}")
        print(f"  Updated:  {result['updated_sample'][0] if result['updated_sample'] else 'N/A'}")
    
    # Export the result
    export_result = await client.call_tool(
        "export_csv",
        {
            "session_id": session_id,
            "file_path": "/tmp/updated_bol_method2.csv",
            "format": "csv"
        }
    )
    print(f"✓ Exported to: {export_result['file_path']}")
    
    # Close session
    await client.call_tool("close_session", {"session_id": session_id})
    
    # Method 3: Using 'extract' operation
    print("\n--- Method 3: Using 'extract' with regex ---")
    
    # Load the file again
    result = await client.call_tool(
        "load_csv",
        {
            "file_path": "/home/santosh/projects/csv-editor/tests/sample_data/123456/1753698447530_BOL_Lubecon USA LLC_GHY 1.csv"
        }
    )
    session_id = result["session_id"]
    
    print("Extracting company name using regex...")
    result = await client.call_tool(
        "update_column",
        {
            "session_id": session_id,
            "column": "Consignee Name",
            "operation": "extract",
            "pattern": r"^([^-]+)",  # Extract everything before the first dash
        }
    )
    
    if result["success"]:
        print(f"✓ Column updated successfully!")
        print(f"  Original: {result['original_sample'][0] if result['original_sample'] else 'N/A'}")
        print(f"  Updated:  {result['updated_sample'][0] if result['updated_sample'] else 'N/A'}")
        
        # Also clean up any trailing spaces
        print("\nCleaning up whitespace...")
        result = await client.call_tool(
            "update_column",
            {
                "session_id": session_id,
                "column": "Consignee Name",
                "operation": "strip"
            }
        )
        print(f"✓ Whitespace cleaned")
    
    # Export the result
    export_result = await client.call_tool(
        "export_csv",
        {
            "session_id": session_id,
            "file_path": "/tmp/updated_bol_method3.csv",
            "format": "csv"
        }
    )
    print(f"✓ Exported to: {export_result['file_path']}")
    
    # Close session
    await client.call_tool("close_session", {"session_id": session_id})
    
    await client.disconnect()
    
    print("\n✅ All methods completed successfully!")
    print("\nThe new 'update_column' function makes it simple to:")
    print("  • Extract parts of text (split, extract)")
    print("  • Clean up text (strip, replace)")
    print("  • Transform text (upper, lower)")
    print("  • Fill missing values")
    print("\nCheck the exported files in /tmp/ to see the results.")


if __name__ == "__main__":
    asyncio.run(update_consignee_example())