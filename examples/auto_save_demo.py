#!/usr/bin/env python3
"""Demonstration of auto-save functionality in CSV Editor MCP Server."""

import asyncio
import tempfile
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# This would normally be done through the MCP client
# For demo purposes, we'll use the internal modules directly
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_editor.models.csv_session import CSVSession
from src.csv_editor.models.auto_save import AutoSaveConfig, AutoSaveMode, AutoSaveStrategy
from src.csv_editor.models.data_models import OperationType


async def demonstrate_auto_save():
    """Demonstrate various auto-save configurations and use cases."""
    
    print("=" * 60)
    print("CSV Editor Auto-Save Feature Demonstration")
    print("=" * 60)
    
    # Create sample data
    df = pd.DataFrame({
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
        'price': [999.99, 29.99, 79.99, 299.99, 149.99],
        'stock': [50, 200, 150, 75, 100],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Audio']
    })
    
    # Create a temporary directory for our backups
    backup_dir = tempfile.mkdtemp(prefix="csv_backup_")
    print(f"\nBackup directory: {backup_dir}")
    
    # Demo 1: Auto-save after each operation
    print("\n" + "-" * 40)
    print("Demo 1: Auto-save after each operation")
    print("-" * 40)
    
    config1 = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=backup_dir
    )
    
    session1 = CSVSession(auto_save_config=config1)
    session1.load_data(df)
    
    print("Performing operations that trigger auto-save...")
    
    # Simulate operations
    session1.record_operation(OperationType.FILTER, {"condition": "price > 50"})
    await session1.trigger_auto_save_if_needed()
    print("✓ Auto-saved after filter operation")
    
    session1.record_operation(OperationType.SORT, {"column": "price"})
    await session1.trigger_auto_save_if_needed()
    print("✓ Auto-saved after sort operation")
    
    # Check backup files
    backup_files = list(Path(backup_dir).glob(f"*{session1.session_id}*"))
    print(f"Created {len(backup_files)} backup files")
    
    # Demo 2: Versioned saves
    print("\n" + "-" * 40)
    print("Demo 2: Versioned saves")
    print("-" * 40)
    
    config2 = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.VERSIONED,
        backup_dir=backup_dir
    )
    
    session2 = CSVSession(auto_save_config=config2)
    session2.load_data(df)
    
    print("Creating versioned saves...")
    for i in range(3):
        session2.df['price'] = session2.df['price'] * (1 + i * 0.1)  # Simulate price changes
        session2.record_operation(OperationType.TRANSFORM, {"operation": f"price_increase_{i}"})
        await session2.trigger_auto_save_if_needed()
        print(f"✓ Created version {i+1}")
    
    # List versioned files
    version_files = sorted(Path(backup_dir).glob(f"version_{session2.session_id}_v*.csv"))
    for vf in version_files:
        print(f"  - {vf.name}")
    
    # Demo 3: Periodic auto-save
    print("\n" + "-" * 40)
    print("Demo 3: Periodic auto-save (every 2 seconds)")
    print("-" * 40)
    
    config3 = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.PERIODIC,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=backup_dir,
        interval_seconds=2  # Short interval for demo
    )
    
    session3 = CSVSession(auto_save_config=config3)
    session3.load_data(df)
    
    # Start periodic save
    await session3.auto_save_manager.start_periodic_save(session3._save_callback)
    print("Started periodic auto-save...")
    
    # Wait for a few saves
    for i in range(3):
        await asyncio.sleep(2.5)
        print(f"✓ Periodic save {i+1} should have triggered")
    
    # Stop periodic save
    await session3.auto_save_manager.stop_periodic_save()
    print("Stopped periodic auto-save")
    
    # Demo 4: Manual save trigger
    print("\n" + "-" * 40)
    print("Demo 4: Manual save trigger")
    print("-" * 40)
    
    session4 = CSVSession()  # Default config (disabled)
    session4.load_data(df)
    
    # Enable auto-save
    await session4.enable_auto_save({
        "enabled": True,
        "mode": "disabled",  # Only manual saves
        "strategy": "backup",
        "backup_dir": backup_dir
    })
    
    print("Triggering manual save...")
    result = await session4.manual_save()
    if result["success"]:
        print(f"✓ Manual save completed: {result['save_path']}")
    
    # Demo 5: Auto-save with max backups limit
    print("\n" + "-" * 40)
    print("Demo 5: Auto-save with backup rotation")
    print("-" * 40)
    
    config5 = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=backup_dir,
        max_backups=3  # Keep only last 3 backups
    )
    
    session5 = CSVSession(auto_save_config=config5)
    session5.load_data(df)
    
    print("Creating multiple saves (max 3 will be kept)...")
    for i in range(5):
        session5.record_operation(OperationType.ANALYZE, {"step": i})
        await session5.trigger_auto_save_if_needed()
        await asyncio.sleep(0.1)  # Small delay for different timestamps
        print(f"✓ Save {i+1} completed")
    
    # Check remaining files
    session5_files = list(Path(backup_dir).glob(f"*{session5.session_id}*"))
    print(f"Kept {len(session5_files)} backup files (max was 3)")
    
    # Summary
    print("\n" + "=" * 60)
    print("Auto-Save Feature Summary")
    print("=" * 60)
    
    print("\nKey Features Demonstrated:")
    print("✓ Auto-save after each operation")
    print("✓ Versioned saves for tracking changes")
    print("✓ Periodic auto-save at intervals")
    print("✓ Manual save triggers")
    print("✓ Backup rotation with max limit")
    
    print("\nConfiguration Options:")
    print("• Modes: disabled, after_operation, periodic, hybrid")
    print("• Strategies: overwrite, backup, versioned, custom")
    print("• Customizable intervals and backup limits")
    print("• Support for multiple export formats")
    
    # List all created files
    print(f"\nTotal files created in {backup_dir}:")
    all_files = list(Path(backup_dir).glob("*.csv"))
    print(f"Found {len(all_files)} CSV files")
    
    # Cleanup sessions
    await session3.clear()  # Important to stop any running tasks
    
    print("\n✅ Auto-save demonstration completed!")
    print(f"\nBackup files saved in: {backup_dir}")
    print("(Directory will be preserved for inspection)")


if __name__ == "__main__":
    asyncio.run(demonstrate_auto_save())