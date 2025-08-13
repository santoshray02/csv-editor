#!/usr/bin/env python3
"""Test that auto-save is enabled by default and works correctly."""

import asyncio
import tempfile
import os
import pandas as pd
from pathlib import Path

# Setup path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_editor.models.csv_session import CSVSession
from src.csv_editor.models.data_models import OperationType


async def test_default_autosave():
    """Test that auto-save is enabled by default."""
    
    print("=" * 60)
    print("Testing Default Auto-Save Configuration")
    print("=" * 60)
    
    # Create a temporary CSV file
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_data.csv")
    
    # Create initial data
    initial_data = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [100, 200, 300]
    })
    
    # Save initial data
    initial_data.to_csv(test_file, index=False)
    print(f"\n✓ Created test file: {test_file}")
    print(f"Initial content:\n{initial_data}")
    
    # Create session WITHOUT explicitly configuring auto-save
    session = CSVSession()  # Using defaults
    
    # Check default auto-save configuration
    print("\n" + "-" * 40)
    print("Default Auto-Save Configuration:")
    print("-" * 40)
    config = session.auto_save_config
    print(f"Enabled: {config.enabled}")
    print(f"Mode: {config.mode.value}")
    print(f"Strategy: {config.strategy.value}")
    
    # Verify defaults
    assert config.enabled == True, "Auto-save should be enabled by default"
    assert config.mode.value == "after_operation", "Mode should be 'after_operation' by default"
    assert config.strategy.value == "overwrite", "Strategy should be 'overwrite' by default"
    print("\n✅ All defaults are correct!")
    
    # Load the CSV file
    df = pd.read_csv(test_file)
    session.load_data(df, file_path=test_file)
    
    print("\n" + "-" * 40)
    print("Testing Auto-Save on Operations:")
    print("-" * 40)
    
    # Perform an operation
    print("\n1. Doubling all values...")
    session.df['value'] = session.df['value'] * 2
    session.record_operation(OperationType.TRANSFORM, {"operation": "double_values"})
    
    # Trigger auto-save (should happen automatically after operation)
    result = await session.trigger_auto_save_if_needed()
    print(f"   Auto-save triggered: {result is not None}")
    
    # Read the file to verify it was updated
    saved_df = pd.read_csv(test_file)
    print(f"   Values in file after operation: {saved_df['value'].tolist()}")
    assert saved_df['value'].tolist() == [200, 400, 600], "File should be auto-saved with new values"
    print("   ✓ File was automatically updated!")
    
    # Perform another operation
    print("\n2. Adding a new column...")
    session.df['status'] = 'active'
    session.record_operation(OperationType.ADD_COLUMN, {"column": "status"})
    
    # Trigger auto-save again
    result = await session.trigger_auto_save_if_needed()
    print(f"   Auto-save triggered: {result is not None}")
    
    # Verify the file has the new column
    saved_df = pd.read_csv(test_file)
    print(f"   Columns in file: {saved_df.columns.tolist()}")
    assert 'status' in saved_df.columns, "New column should be in the saved file"
    print("   ✓ New column was automatically saved!")
    
    # Show final file content
    print("\n" + "-" * 40)
    print("Final File Content:")
    print("-" * 40)
    print(saved_df)
    
    print("\n" + "=" * 60)
    print("✅ Default Auto-Save Test Passed!")
    print("=" * 60)
    print("\nSummary:")
    print("• Auto-save is ENABLED by default")
    print("• Mode is 'after_operation' by default")
    print("• Strategy is 'overwrite' by default")
    print("• Original file is automatically updated after each operation")
    print("• No manual configuration needed!")
    
    return test_file


async def main():
    """Run the test."""
    test_file = await test_default_autosave()
    print(f"\nTest file location: {test_file}")
    print("(File has been automatically saved with all changes)")


if __name__ == "__main__":
    asyncio.run(main())