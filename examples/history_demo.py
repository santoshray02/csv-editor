#!/usr/bin/env python3
"""Demonstration of history tracking with undo/redo functionality."""

import asyncio
import tempfile
import os
import pandas as pd
from pathlib import Path
import json

# Setup path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_editor.models.csv_session import CSVSession
from src.csv_editor.models.history_manager import HistoryStorage
from src.csv_editor.models.data_models import OperationType


async def demonstrate_history():
    """Demonstrate history tracking with undo/redo capabilities."""
    
    print("=" * 60)
    print("CSV Editor History & Undo/Redo Demonstration")
    print("=" * 60)
    
    # Create initial data
    initial_data = pd.DataFrame({
        'product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
        'price': [999.99, 29.99, 79.99, 299.99],
        'stock': [50, 200, 150, 75],
        'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics']
    })
    
    # Create session with history enabled (JSON persistence)
    session = CSVSession(
        enable_history=True,
        history_storage=HistoryStorage.JSON
    )
    
    # Load data
    temp_file = os.path.join(tempfile.gettempdir(), "demo_data.csv")
    initial_data.to_csv(temp_file, index=False)
    session.load_data(initial_data, file_path=temp_file)
    
    print(f"\n✓ Created session with history tracking")
    print(f"Initial data:\n{session.df}\n")
    
    # Perform a series of operations
    print("-" * 40)
    print("Performing operations...")
    print("-" * 40)
    
    # Operation 1: Increase prices
    print("\n1. Increasing all prices by 10%")
    session.df['price'] = session.df['price'] * 1.1
    session.record_operation(OperationType.TRANSFORM, {"operation": "price_increase_10%"})
    print(f"Prices after increase:\n{session.df['price'].tolist()}")
    
    # Operation 2: Filter low stock
    print("\n2. Filtering items with stock >= 100")
    session.df = session.df[session.df['stock'] >= 100]
    session.record_operation(OperationType.FILTER, {"condition": "stock >= 100"})
    print(f"Products after filter: {session.df['product'].tolist()}")
    
    # Operation 3: Add discount column
    print("\n3. Adding discount column")
    session.df['discount'] = 0.15
    session.record_operation(OperationType.ADD_COLUMN, {"column": "discount", "value": 0.15})
    print(f"Columns: {session.df.columns.tolist()}")
    
    # Operation 4: Sort by price
    print("\n4. Sorting by price (descending)")
    session.df = session.df.sort_values('price', ascending=False)
    session.record_operation(OperationType.SORT, {"column": "price", "ascending": False})
    print(f"Products after sort: {session.df['product'].tolist()}")
    
    # Show current history
    print("\n" + "=" * 60)
    print("Current History")
    print("=" * 60)
    history_result = session.get_history()
    if history_result["success"]:
        print(f"Total operations: {history_result['statistics']['total_operations']}")
        print(f"Current position: {history_result['statistics']['current_position']}")
        print(f"Can undo: {history_result['statistics']['can_undo']}")
        print(f"Can redo: {history_result['statistics']['can_redo']}")
        
        print("\nOperations:")
        for op in history_result['history']:
            print(f"  [{op['index']}] {op['operation_type']} - {op['timestamp']}")
            if op['is_current']:
                print(f"      ^ Current position")
    
    # Demonstrate undo
    print("\n" + "=" * 60)
    print("Undo Operations")
    print("=" * 60)
    
    print("\n1. Undoing last operation (sort)...")
    undo_result = await session.undo()
    if undo_result["success"]:
        print(f"✓ {undo_result['message']}")
        print(f"Products order: {session.df['product'].tolist() if session.df is not None else 'N/A'}")
    
    print("\n2. Undoing again (add discount column)...")
    undo_result = await session.undo()
    if undo_result["success"]:
        print(f"✓ {undo_result['message']}")
        print(f"Columns: {session.df.columns.tolist() if session.df is not None else 'N/A'}")
    
    print("\n3. Undoing once more (filter)...")
    undo_result = await session.undo()
    if undo_result["success"]:
        print(f"✓ {undo_result['message']}")
        print(f"Row count: {len(session.df) if session.df is not None else 0}")
        print(f"Products: {session.df['product'].tolist() if session.df is not None else 'N/A'}")
    
    # Show history after undo
    history_result = session.get_history()
    print(f"\nCurrent position after undos: {history_result['statistics']['current_position']}")
    print(f"Can redo: {history_result['statistics']['can_redo']}")
    
    # Demonstrate redo
    print("\n" + "=" * 60)
    print("Redo Operations")
    print("=" * 60)
    
    print("\n1. Redoing (re-apply filter)...")
    redo_result = await session.redo()
    if redo_result["success"]:
        print(f"✓ {redo_result['message']}")
        print(f"Row count: {len(session.df) if session.df is not None else 0}")
    
    print("\n2. Redoing again (re-add discount column)...")
    redo_result = await session.redo()
    if redo_result["success"]:
        print(f"✓ {redo_result['message']}")
        print(f"Columns: {session.df.columns.tolist() if session.df is not None else 'N/A'}")
    
    # Perform a new operation (clears redo stack)
    print("\n" + "=" * 60)
    print("New Operation (clears redo stack)")
    print("=" * 60)
    
    print("\nAdding a new column 'in_stock'...")
    session.df['in_stock'] = True
    session.record_operation(OperationType.ADD_COLUMN, {"column": "in_stock", "value": True})
    print(f"Columns: {session.df.columns.tolist()}")
    
    history_result = session.get_history()
    print(f"\nCan still redo? {history_result['statistics']['can_redo']} (should be False)")
    
    # Demonstrate restore to specific operation
    print("\n" + "=" * 60)
    print("Restore to Specific Operation")
    print("=" * 60)
    
    # Get first operation ID
    history_result = session.get_history()
    if history_result["success"] and history_result["history"]:
        first_op = history_result["history"][0]
        print(f"\nRestoring to first operation: {first_op['operation_type']}")
        
        restore_result = await session.restore_to_operation(first_op['operation_id'])
        if restore_result["success"]:
            print(f"✓ {restore_result['message']}")
            print(f"Data shape: {restore_result['shape']}")
            print(f"Current data:\n{session.df}")
    
    # Export history
    print("\n" + "=" * 60)
    print("Export History")
    print("=" * 60)
    
    # Export as JSON
    history_file = os.path.join(tempfile.gettempdir(), "history_export.json")
    if session.history_manager:
        success = session.history_manager.export_history(history_file, "json")
        if success:
            print(f"✓ History exported to: {history_file}")
            
            # Show exported content
            with open(history_file, 'r') as f:
                history_data = json.load(f)
            print(f"  Total operations: {history_data['total_operations']}")
            print(f"  Exported at: {history_data['exported_at']}")
    
    # Show history statistics
    print("\n" + "=" * 60)
    print("History Statistics")
    print("=" * 60)
    
    if session.history_manager:
        stats = session.history_manager.get_statistics()
        print(f"Total operations: {stats['total_operations']}")
        print(f"Current position: {stats['current_position']}")
        print(f"Snapshots saved: {stats['snapshots_count']}")
        print(f"Storage type: {stats['storage_type']}")
        print("\nOperation breakdown:")
        for op_type, count in stats['operation_types'].items():
            print(f"  {op_type}: {count}")
    
    # Show persistence
    print("\n" + "=" * 60)
    print("History Persistence")
    print("=" * 60)
    
    history_dir = session.history_manager.history_dir if session.history_manager else None
    if history_dir:
        print(f"History directory: {history_dir}")
        
        # List history files
        history_files = list(Path(history_dir).glob(f"*{session.session_id}*"))
        print(f"History files created: {len(history_files)}")
        for hf in history_files:
            print(f"  - {hf.name}")
        
        # Check snapshot directory
        snapshot_dir = Path(history_dir) / "snapshots" / session.session_id
        if snapshot_dir.exists():
            snapshots = list(snapshot_dir.glob("*.pkl"))
            print(f"Snapshots saved: {len(snapshots)}")
    
    print("\n✅ History demonstration completed!")
    
    return session


async def demonstrate_history_recovery():
    """Demonstrate recovering history from a previous session."""
    
    print("\n" + "=" * 60)
    print("History Recovery from Previous Session")
    print("=" * 60)
    
    # Create a session and perform operations
    print("\n1. Creating initial session with operations...")
    session1 = CSVSession(
        session_id="demo-recovery-session",
        enable_history=True,
        history_storage=HistoryStorage.JSON
    )
    
    data = pd.DataFrame({
        'item': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })
    
    session1.load_data(data)
    
    # Perform operations
    session1.df['value'] = session1.df['value'] * 2
    session1.record_operation(OperationType.TRANSFORM, {"operation": "double_values"})
    
    session1.df['status'] = 'active'
    session1.record_operation(OperationType.ADD_COLUMN, {"column": "status"})
    
    print(f"  Operations performed: 2")
    print(f"  Final data:\n{session1.df}")
    
    # Simulate session end
    session1_id = session1.session_id
    del session1
    
    print("\n2. Session ended. Creating new session with same ID...")
    
    # Create new session with same ID - should load history
    session2 = CSVSession(
        session_id=session1_id,
        enable_history=True,
        history_storage=HistoryStorage.JSON
    )
    
    # Load the data (in real scenario, would load from file)
    session2.load_data(data)
    
    # Check if history was recovered
    history_result = session2.get_history()
    if history_result["success"]:
        print(f"✓ History recovered! Found {history_result['statistics']['total_operations']} operations")
        
        # Can we undo operations from previous session?
        print("\n3. Testing undo on recovered history...")
        if history_result['statistics']['can_undo']:
            undo_result = await session2.undo()
            if undo_result["success"]:
                print(f"✓ Successfully undid operation from previous session!")
                print(f"  Operation: {undo_result['operation']['operation_type']}")
    
    print("\n✅ History recovery demonstration completed!")


async def main():
    """Run all history demonstrations."""
    
    # Demo 1: Basic history with undo/redo
    session = await demonstrate_history()
    
    # Demo 2: History recovery
    await demonstrate_history_recovery()
    
    print("\n" + "=" * 60)
    print("Key Features Demonstrated")
    print("=" * 60)
    print("✓ Operation history tracking with timestamps")
    print("✓ Persistent history storage (JSON/Pickle)")
    print("✓ Undo/Redo functionality")
    print("✓ Restore to any previous operation")
    print("✓ History export (JSON/CSV)")
    print("✓ History recovery across sessions")
    print("✓ Automatic snapshots for data recovery")
    print("✓ History statistics and analysis")


if __name__ == "__main__":
    asyncio.run(main())