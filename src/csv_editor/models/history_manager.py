"""History management for CSV operations with persistence and undo/redo capabilities."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import pickle
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class HistoryStorage(str, Enum):
    """History storage strategies."""
    
    MEMORY = "memory"  # In-memory only (lost on session end)
    JSON = "json"  # Save as JSON file
    PICKLE = "pickle"  # Save as pickle (preserves DataFrames)
    SQLITE = "sqlite"  # Save in SQLite database (future)


class OperationHistory:
    """Represents a single operation in history."""
    
    def __init__(
        self,
        operation_id: str,
        operation_type: str,
        timestamp: datetime,
        details: Dict[str, Any],
        data_snapshot: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize operation history entry."""
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.timestamp = timestamp
        self.details = details
        self.data_snapshot = data_snapshot
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "metadata": self.metadata,
            "has_snapshot": self.data_snapshot is not None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], data_snapshot: Optional[pd.DataFrame] = None) -> "OperationHistory":
        """Create from dictionary."""
        return cls(
            operation_id=data["operation_id"],
            operation_type=data["operation_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            details=data["details"],
            data_snapshot=data_snapshot,
            metadata=data.get("metadata", {})
        )


class HistoryManager:
    """Manages operation history with persistence and undo/redo capabilities."""
    
    def __init__(
        self,
        session_id: str,
        storage_type: HistoryStorage = HistoryStorage.MEMORY,
        history_dir: Optional[str] = None,
        max_history: int = 100,
        enable_snapshots: bool = True,
        snapshot_interval: int = 5  # Take snapshot every N operations
    ):
        """Initialize history manager."""
        self.session_id = session_id
        self.storage_type = storage_type
        self.history_dir = history_dir or os.path.join(os.getcwd(), ".csv_history")
        self.max_history = max_history
        self.enable_snapshots = enable_snapshots
        self.snapshot_interval = snapshot_interval
        
        # History tracking
        self.history: List[OperationHistory] = []
        self.current_index = -1  # Points to current position in history
        self.redo_stack: List[OperationHistory] = []  # For redo functionality
        
        # Create history directory if needed
        if storage_type != HistoryStorage.MEMORY:
            Path(self.history_dir).mkdir(parents=True, exist_ok=True)
            self._load_history()
    
    def _get_history_file_path(self, extension: str = "json") -> str:
        """Get the path for history file."""
        return os.path.join(self.history_dir, f"history_{self.session_id}.{extension}")
    
    def _get_snapshot_file_path(self, operation_id: str) -> str:
        """Get the path for snapshot file."""
        snapshot_dir = os.path.join(self.history_dir, "snapshots", self.session_id)
        Path(snapshot_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(snapshot_dir, f"snapshot_{operation_id}.pkl")
    
    def _load_history(self):
        """Load history from persistent storage."""
        try:
            if self.storage_type == HistoryStorage.JSON:
                history_file = self._get_history_file_path("json")
                if os.path.exists(history_file):
                    with open(history_file, 'r') as f:
                        data = json.load(f)
                        for entry in data.get("history", []):
                            # Load snapshot if available
                            snapshot = None
                            if entry.get("has_snapshot"):
                                snapshot_file = self._get_snapshot_file_path(entry["operation_id"])
                                if os.path.exists(snapshot_file):
                                    with open(snapshot_file, 'rb') as sf:
                                        snapshot = pickle.load(sf)
                            
                            self.history.append(OperationHistory.from_dict(entry, snapshot))
                        
                        self.current_index = data.get("current_index", -1)
                        logger.info(f"Loaded {len(self.history)} history entries for session {self.session_id}")
                        
            elif self.storage_type == HistoryStorage.PICKLE:
                history_file = self._get_history_file_path("pkl")
                if os.path.exists(history_file):
                    with open(history_file, 'rb') as f:
                        data = pickle.load(f)
                        self.history = data.get("history", [])
                        self.current_index = data.get("current_index", -1)
                        logger.info(f"Loaded {len(self.history)} history entries for session {self.session_id}")
                        
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
    
    def _save_history(self):
        """Save history to persistent storage."""
        try:
            if self.storage_type == HistoryStorage.JSON:
                history_file = self._get_history_file_path("json")
                data = {
                    "session_id": self.session_id,
                    "history": [h.to_dict() for h in self.history],
                    "current_index": self.current_index,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                with open(history_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Save snapshots separately
                for entry in self.history:
                    if entry.data_snapshot is not None:
                        snapshot_file = self._get_snapshot_file_path(entry.operation_id)
                        with open(snapshot_file, 'wb') as sf:
                            pickle.dump(entry.data_snapshot, sf)
                            
            elif self.storage_type == HistoryStorage.PICKLE:
                history_file = self._get_history_file_path("pkl")
                data = {
                    "session_id": self.session_id,
                    "history": self.history,
                    "current_index": self.current_index,
                    "timestamp": datetime.utcnow()
                }
                
                with open(history_file, 'wb') as f:
                    pickle.dump(data, f)
                    
            logger.debug(f"Saved {len(self.history)} history entries for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
    
    def add_operation(
        self,
        operation_type: str,
        details: Dict[str, Any],
        current_data: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new operation to history."""
        # Clear redo stack when new operation is added
        self.redo_stack.clear()
        
        # Remove operations after current index (for undo/redo consistency)
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Generate operation ID
        operation_id = f"{self.session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Determine if we should take a snapshot
        take_snapshot = (
            self.enable_snapshots and 
            current_data is not None and
            (len(self.history) % self.snapshot_interval == 0 or len(self.history) == 0)
        )
        
        # Create operation entry
        operation = OperationHistory(
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.utcnow(),
            details=details,
            data_snapshot=current_data.copy() if take_snapshot else None,
            metadata=metadata
        )
        
        # Add to history
        self.history.append(operation)
        self.current_index += 1
        
        # Trim history if exceeds max
        if len(self.history) > self.max_history:
            removed = self.history.pop(0)
            self.current_index -= 1
            
            # Clean up old snapshot file if exists
            if removed.data_snapshot is not None and self.storage_type != HistoryStorage.MEMORY:
                snapshot_file = self._get_snapshot_file_path(removed.operation_id)
                if os.path.exists(snapshot_file):
                    os.remove(snapshot_file)
        
        # Save to persistent storage
        if self.storage_type != HistoryStorage.MEMORY:
            self._save_history()
        
        logger.info(f"Added operation {operation_id}: {operation_type}")
        return operation_id
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0
    
    def undo(self) -> Tuple[Optional[OperationHistory], Optional[pd.DataFrame]]:
        """Undo the last operation and return the previous state."""
        if not self.can_undo():
            return None, None
        
        # Move current operation to redo stack
        current_op = self.history[self.current_index]
        self.redo_stack.append(current_op)
        
        # Move index back
        self.current_index -= 1
        
        # Find the most recent snapshot before current position
        snapshot = None
        for i in range(self.current_index, -1, -1):
            if self.history[i].data_snapshot is not None:
                snapshot = self.history[i].data_snapshot.copy()
                break
        
        # Save state
        if self.storage_type != HistoryStorage.MEMORY:
            self._save_history()
        
        logger.info(f"Undid operation: {current_op.operation_type}")
        
        # Return the operation that was undone and the data to restore
        return current_op, snapshot
    
    def redo(self) -> Tuple[Optional[OperationHistory], Optional[pd.DataFrame]]:
        """Redo the previously undone operation."""
        if not self.can_redo():
            return None, None
        
        # Get operation from redo stack
        operation = self.redo_stack.pop()
        
        # Move index forward
        self.current_index += 1
        
        # Get the snapshot at this position if available
        snapshot = None
        if self.current_index < len(self.history):
            snapshot = self.history[self.current_index].data_snapshot
            if snapshot is not None:
                snapshot = snapshot.copy()
        
        # Save state
        if self.storage_type != HistoryStorage.MEMORY:
            self._save_history()
        
        logger.info(f"Redid operation: {operation.operation_type}")
        
        return operation, snapshot
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get operation history."""
        history_list = []
        
        start = 0 if limit is None else max(0, len(self.history) - limit)
        
        for i, entry in enumerate(self.history[start:], start=start):
            history_dict = entry.to_dict()
            history_dict["index"] = i
            history_dict["is_current"] = (i == self.current_index)
            history_dict["can_restore"] = entry.data_snapshot is not None
            history_list.append(history_dict)
        
        return history_list
    
    def get_operation(self, operation_id: str) -> Optional[OperationHistory]:
        """Get a specific operation by ID."""
        for entry in self.history:
            if entry.operation_id == operation_id:
                return entry
        return None
    
    def restore_to_operation(self, operation_id: str) -> Optional[pd.DataFrame]:
        """Restore data to a specific operation point."""
        # Find the operation
        target_index = None
        for i, entry in enumerate(self.history):
            if entry.operation_id == operation_id:
                target_index = i
                break
        
        if target_index is None:
            logger.error(f"Operation {operation_id} not found")
            return None
        
        # Find the nearest snapshot at or before target
        snapshot = None
        for i in range(target_index, -1, -1):
            if self.history[i].data_snapshot is not None:
                snapshot = self.history[i].data_snapshot.copy()
                self.current_index = target_index
                
                # Clear redo stack since we're jumping to a specific point
                self.redo_stack.clear()
                
                # Save state
                if self.storage_type != HistoryStorage.MEMORY:
                    self._save_history()
                
                logger.info(f"Restored to operation {operation_id}")
                return snapshot
        
        logger.error(f"No snapshot available for operation {operation_id}")
        return None
    
    def clear_history(self):
        """Clear all history."""
        self.history.clear()
        self.redo_stack.clear()
        self.current_index = -1
        
        # Clean up files
        if self.storage_type != HistoryStorage.MEMORY:
            # Remove history file
            for ext in ["json", "pkl"]:
                history_file = self._get_history_file_path(ext)
                if os.path.exists(history_file):
                    os.remove(history_file)
            
            # Remove snapshot files
            snapshot_dir = os.path.join(self.history_dir, "snapshots", self.session_id)
            if os.path.exists(snapshot_dir):
                import shutil
                shutil.rmtree(snapshot_dir)
        
        logger.info(f"Cleared history for session {self.session_id}")
    
    def export_history(self, file_path: str, format: str = "json") -> bool:
        """Export history to a file."""
        try:
            if format == "json":
                data = {
                    "session_id": self.session_id,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_operations": len(self.history),
                    "current_position": self.current_index,
                    "operations": self.get_history()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format == "csv":
                # Export as CSV with operation details
                history_data = []
                for entry in self.history:
                    history_data.append({
                        "timestamp": entry.timestamp.isoformat(),
                        "operation_type": entry.operation_type,
                        "details": json.dumps(entry.details),
                        "has_snapshot": entry.data_snapshot is not None
                    })
                
                df = pd.DataFrame(history_data)
                df.to_csv(file_path, index=False)
            
            logger.info(f"Exported history to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting history: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get history statistics."""
        if not self.history:
            return {
                "total_operations": 0,
                "operation_types": {},
                "first_operation": None,
                "last_operation": None,
                "snapshots_count": 0
            }
        
        # Count operation types
        operation_types = {}
        snapshots_count = 0
        
        for entry in self.history:
            operation_types[entry.operation_type] = operation_types.get(entry.operation_type, 0) + 1
            if entry.data_snapshot is not None:
                snapshots_count += 1
        
        return {
            "total_operations": len(self.history),
            "current_position": self.current_index + 1,
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "redo_stack_size": len(self.redo_stack),
            "operation_types": operation_types,
            "first_operation": self.history[0].timestamp.isoformat() if self.history else None,
            "last_operation": self.history[-1].timestamp.isoformat() if self.history else None,
            "snapshots_count": snapshots_count,
            "storage_type": self.storage_type.value,
            "max_history": self.max_history
        }