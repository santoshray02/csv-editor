#!/usr/bin/env python3
"""Example showing auto-save that overwrites the original file."""

import asyncio
import tempfile
import os
import pandas as pd
from pathlib import Path

# Setup path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_editor.models.csv_session import CSVSession
from src.csv_editor.models.auto_save import AutoSaveConfig, AutoSaveMode, AutoSaveStrategy
from src.csv_editor.models.data_models import OperationType


async def overwrite_same_file_example():
    """Demonstrate auto-save that updates the same file."""
    
    print("=" * 60)
    print("Auto-Save: Overwrite Same File Example")
    print("=" * 60)
    
    # Create a temporary CSV file
    temp_dir = tempfile.mkdtemp()
    original_file = os.path.join(temp_dir, "data.csv")
    
    # Create initial data
    initial_data = pd.DataFrame({
        'product': ['Laptop', 'Mouse', 'Keyboard'],
        'price': [999.99, 29.99, 79.99],
        'stock': [50, 200, 150]
    })
    
    # Save initial data to file
    initial_data.to_csv(original_file, index=False)
    print(f"\n✓ Created file: {original_file}")
    print(f"Initial content:\n{initial_data}")
    
    # Configure auto-save to OVERWRITE the same file
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,  # Save after each operation
        strategy=AutoSaveStrategy.OVERWRITE,  # Overwrite the original file
    )
    
    # Create session with auto-save config
    session = CSVSession(auto_save_config=config)
    
    # Load the CSV file
    df = pd.read_csv(original_file)
    session.load_data(df, file_path=original_file)  # Pass the original file path
    
    print(f"\n✓ Loaded data into session from: {original_file}")
    
    # Modify the data
    print("\n--- Making changes to the data ---")
    
    # Change 1: Increase all prices by 10%
    session.df['price'] = session.df['price'] * 1.1
    session.record_operation(OperationType.TRANSFORM, {"operation": "price_increase_10%"})
    await session.trigger_auto_save_if_needed()
    print("✓ Increased prices by 10% and auto-saved to same file")
    
    # Verify the file was updated
    df_check1 = pd.read_csv(original_file)
    print(f"File content after price increase:\n{df_check1}")
    
    # Change 2: Add a new product
    new_row = pd.DataFrame({
        'product': ['Monitor'],
        'price': [329.989],  # Will be rounded when saved
        'stock': [75]
    })
    session.df = pd.concat([session.df, new_row], ignore_index=True)
    session.record_operation(OperationType.ADD_COLUMN, {"operation": "add_monitor"})
    await session.trigger_auto_save_if_needed()
    print("\n✓ Added new product and auto-saved to same file")
    
    # Verify the file was updated again
    df_check2 = pd.read_csv(original_file)
    print(f"File content after adding product:\n{df_check2}")
    
    # Change 3: Filter out low stock items (this removes data)
    session.df = session.df[session.df['stock'] >= 100]
    session.record_operation(OperationType.FILTER, {"condition": "stock >= 100"})
    await session.trigger_auto_save_if_needed()
    print("\n✓ Filtered low stock items and auto-saved to same file")
    
    # Final verification
    df_final = pd.read_csv(original_file)
    print(f"Final file content:\n{df_final}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"✓ Original file: {original_file}")
    print("✓ Same file was overwritten after each operation")
    print("✓ No backup copies were created")
    print(f"✓ Final file has {len(df_final)} rows (started with {len(initial_data)})")
    
    # Show that only one file exists (no backups)
    files_in_dir = list(Path(temp_dir).glob("*.csv"))
    print(f"\nFiles in directory: {[f.name for f in files_in_dir]}")
    print(f"Total CSV files: {len(files_in_dir)} (only the original, no backups)")
    
    return original_file


async def hybrid_example_with_overwrite():
    """Example showing overwrite with periodic saves."""
    
    print("\n" + "=" * 60)
    print("Hybrid Mode with Overwrite Example")
    print("=" * 60)
    
    # Create a temporary CSV file
    temp_dir = tempfile.mkdtemp()
    original_file = os.path.join(temp_dir, "periodic_data.csv")
    
    # Create initial data
    data = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [100, 200, 300]
    })
    data.to_csv(original_file, index=False)
    print(f"\n✓ Created file: {original_file}")
    
    # Configure hybrid mode with overwrite
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.HYBRID,  # Both periodic and after-operation
        strategy=AutoSaveStrategy.OVERWRITE,
        interval_seconds=2  # Save every 2 seconds
    )
    
    session = CSVSession(auto_save_config=config)
    df = pd.read_csv(original_file)
    session.load_data(df, file_path=original_file)
    
    # Start periodic saves
    await session.auto_save_manager.start_periodic_save(session._save_callback)
    print("✓ Started periodic auto-save (every 2 seconds)")
    
    # Make some changes
    print("\nMaking gradual changes...")
    
    # Change 1
    session.df['value'] = session.df['value'] + 10
    print("  Added 10 to all values")
    
    # Wait for periodic save
    await asyncio.sleep(2.5)
    
    # Change 2
    session.df['value'] = session.df['value'] * 2
    session.record_operation(OperationType.TRANSFORM, {"operation": "double_values"})
    await session.trigger_auto_save_if_needed()
    print("  Doubled all values (triggered immediate save)")
    
    # Wait for another periodic save
    await asyncio.sleep(2.5)
    
    # Stop periodic saves
    await session.auto_save_manager.stop_periodic_save()
    print("\n✓ Stopped periodic saves")
    
    # Check final file
    df_final = pd.read_csv(original_file)
    print(f"\nFinal file content:\n{df_final}")
    
    return original_file


async def main():
    """Run all examples."""
    
    # Example 1: Simple overwrite
    file1 = await overwrite_same_file_example()
    
    # Example 2: Hybrid mode with overwrite
    file2 = await hybrid_example_with_overwrite()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("• Use strategy='overwrite' to update the same file")
    print("• Original file path must be provided when loading data")
    print("• No backup copies are created with overwrite strategy")
    print("• Works with all modes: after_operation, periodic, hybrid")
    print("\nFor production use, consider:")
    print("• Backup strategy for safety (creates copies)")
    print("• Overwrite strategy for direct updates")
    print("• Hybrid mode for maximum protection")


if __name__ == "__main__":
    asyncio.run(main())