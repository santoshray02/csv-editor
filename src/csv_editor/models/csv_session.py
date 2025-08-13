"""Session management for CSV Editor MCP Server."""

import pandas as pd
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from pathlib import Path
import json
import asyncio

from .data_models import SessionInfo, OperationType, ExportFormat
from .auto_save import AutoSaveConfig, AutoSaveManager, AutoSaveStrategy
from .history_manager import HistoryManager, HistoryStorage

logger = logging.getLogger(__name__)


class CSVSession:
    """Represents a single CSV editing session."""
    
    def __init__(
        self, 
        session_id: Optional[str] = None, 
        ttl_minutes: int = 60, 
        auto_save_config: Optional[AutoSaveConfig] = None,
        enable_history: bool = True,
        history_storage: HistoryStorage = HistoryStorage.JSON
    ):
        """Initialize a new CSV session."""
        self.session_id = session_id or str(uuid4())
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.ttl = timedelta(minutes=ttl_minutes)
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.operations_history: List[Dict[str, Any]] = []  # Keep for backward compatibility
        self.file_path: Optional[str] = None
        
        # Auto-save configuration
        self.auto_save_config = auto_save_config or AutoSaveConfig()
        self.auto_save_manager = AutoSaveManager(self.session_id, self.auto_save_config)
        
        # History management
        self.enable_history = enable_history
        self.history_manager = HistoryManager(
            session_id=self.session_id,
            storage_type=history_storage if enable_history else HistoryStorage.MEMORY,
            enable_snapshots=True,
            snapshot_interval=5  # Take snapshot every 5 operations
        ) if enable_history else None
        
    def update_access_time(self):
        """Update the last accessed time."""
        self.last_accessed = datetime.utcnow()
        
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() - self.last_accessed > self.ttl
        
    def load_data(self, df: pd.DataFrame, file_path: Optional[str] = None):
        """Load data into the session."""
        self.df = df.copy()
        self.original_df = df.copy()
        self.file_path = file_path
        self.update_access_time()
        self.record_operation(OperationType.LOAD, {"file_path": file_path, "shape": df.shape})
        
        # Update auto-save manager with original file path
        if file_path:
            self.auto_save_manager.original_file_path = file_path
        
    def get_info(self) -> SessionInfo:
        """Get session information."""
        if self.df is None:
            raise ValueError("No data loaded in session")
            
        memory_usage = self.df.memory_usage(deep=True).sum() / (1024 * 1024)  # Convert to MB
        
        return SessionInfo(
            session_id=self.session_id,
            created_at=self.created_at,
            last_accessed=self.last_accessed,
            row_count=len(self.df),
            column_count=len(self.df.columns),
            columns=self.df.columns.tolist(),
            memory_usage_mb=round(memory_usage, 2),
            operations_count=len(self.operations_history),
            file_path=self.file_path
        )
        
    def record_operation(self, operation_type: OperationType, details: Dict[str, Any]):
        """Record an operation in history."""
        # Legacy history (backward compatibility)
        self.operations_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": operation_type.value,
            "details": details
        })
        self.update_access_time()
        
        # New persistent history
        if self.history_manager and self.df is not None:
            self.history_manager.add_operation(
                operation_type=operation_type.value,
                details=details,
                current_data=self.df,
                metadata={
                    "file_path": self.file_path,
                    "shape": self.df.shape if self.df is not None else None
                }
            )
        
        # Mark that auto-save is needed
        self.metadata["needs_autosave"] = True
    
    async def trigger_auto_save_if_needed(self) -> Optional[Dict[str, Any]]:
        """Trigger auto-save after operation if configured."""
        if self.auto_save_manager.should_save_after_operation() and self.metadata.get("needs_autosave"):
            result = await self.auto_save_manager.trigger_save(self._save_callback, "after_operation")
            if result.get("success"):
                self.metadata["needs_autosave"] = False
            return result
        return None
    
    async def _save_callback(self, file_path: str, format: ExportFormat, encoding: str) -> Dict[str, Any]:
        """Callback for auto-save operations."""
        try:
            if self.df is None:
                return {"success": False, "error": "No data to save"}
            
            # Handle different export formats
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == ExportFormat.CSV:
                self.df.to_csv(file_path, index=False, encoding=encoding)
            elif format == ExportFormat.TSV:
                self.df.to_csv(file_path, sep='\t', index=False, encoding=encoding)
            elif format == ExportFormat.JSON:
                self.df.to_json(file_path, orient='records', indent=2)
            elif format == ExportFormat.EXCEL:
                self.df.to_excel(file_path, index=False)
            elif format == ExportFormat.PARQUET:
                self.df.to_parquet(file_path, index=False)
            else:
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            return {
                "success": True,
                "file_path": str(file_path),
                "rows": len(self.df),
                "columns": len(self.df.columns)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def rollback(self, steps: int = 1) -> bool:
        """Rollback operations by specified number of steps."""
        if self.original_df is None:
            return False
            
        if steps >= len(self.operations_history):
            # Rollback to original state
            self.df = self.original_df.copy()
            self.operations_history = []
            return True
            
        # This is a simplified rollback - in production, you'd replay operations
        logger.warning("Partial rollback not fully implemented")
        return False
        
    async def enable_auto_save(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enable or update auto-save configuration."""
        try:
            # Update configuration
            self.auto_save_config = AutoSaveConfig.from_dict(config)
            self.auto_save_manager = AutoSaveManager(
                self.session_id, 
                self.auto_save_config,
                self.file_path  # Pass the original file path
            )
            
            # Start periodic save if needed
            if self.auto_save_config.enabled:
                await self.auto_save_manager.start_periodic_save(self._save_callback)
            
            return {
                "success": True,
                "message": "Auto-save configuration updated",
                "config": self.auto_save_config.to_dict()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def disable_auto_save(self) -> Dict[str, Any]:
        """Disable auto-save."""
        try:
            await self.auto_save_manager.stop_periodic_save()
            self.auto_save_config.enabled = False
            return {"success": True, "message": "Auto-save disabled"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_auto_save_status(self) -> Dict[str, Any]:
        """Get current auto-save status."""
        return self.auto_save_manager.get_status()
    
    async def manual_save(self) -> Dict[str, Any]:
        """Manually trigger a save."""
        return await self.auto_save_manager.trigger_save(self._save_callback, "manual")
    
    async def undo(self) -> Dict[str, Any]:
        """Undo the last operation."""
        if not self.history_manager:
            return {"success": False, "error": "History is not enabled"}
        
        if not self.history_manager.can_undo():
            return {"success": False, "error": "No operations to undo"}
        
        try:
            operation, data_snapshot = self.history_manager.undo()
            
            if data_snapshot is not None:
                self.df = data_snapshot
                
                # Trigger auto-save if configured
                if self.auto_save_manager.should_save_after_operation():
                    await self.auto_save_manager.trigger_save(self._save_callback, "undo")
                
                return {
                    "success": True,
                    "message": f"Undid operation: {operation.operation_type}",
                    "operation": operation.to_dict(),
                    "can_undo": self.history_manager.can_undo(),
                    "can_redo": self.history_manager.can_redo()
                }
            else:
                return {
                    "success": False,
                    "error": "No snapshot available for undo"
                }
                
        except Exception as e:
            logger.error(f"Error during undo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def redo(self) -> Dict[str, Any]:
        """Redo the previously undone operation."""
        if not self.history_manager:
            return {"success": False, "error": "History is not enabled"}
        
        if not self.history_manager.can_redo():
            return {"success": False, "error": "No operations to redo"}
        
        try:
            operation, data_snapshot = self.history_manager.redo()
            
            if data_snapshot is not None:
                self.df = data_snapshot
                
                # Trigger auto-save if configured
                if self.auto_save_manager.should_save_after_operation():
                    await self.auto_save_manager.trigger_save(self._save_callback, "redo")
                
                return {
                    "success": True,
                    "message": f"Redid operation: {operation.operation_type}",
                    "operation": operation.to_dict(),
                    "can_undo": self.history_manager.can_undo(),
                    "can_redo": self.history_manager.can_redo()
                }
            else:
                return {
                    "success": False,
                    "error": "No snapshot available for redo"
                }
                
        except Exception as e:
            logger.error(f"Error during redo: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_history(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get operation history."""
        if not self.history_manager:
            # Return legacy history if new history is not enabled
            return {
                "success": True,
                "history": self.operations_history[-limit:] if limit else self.operations_history,
                "total": len(self.operations_history)
            }
        
        try:
            history = self.history_manager.get_history(limit)
            stats = self.history_manager.get_statistics()
            
            return {
                "success": True,
                "history": history,
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def restore_to_operation(self, operation_id: str) -> Dict[str, Any]:
        """Restore data to a specific operation point."""
        if not self.history_manager:
            return {"success": False, "error": "History is not enabled"}
        
        try:
            data_snapshot = self.history_manager.restore_to_operation(operation_id)
            
            if data_snapshot is not None:
                self.df = data_snapshot
                
                # Trigger auto-save if configured
                if self.auto_save_manager.should_save_after_operation():
                    await self.auto_save_manager.trigger_save(self._save_callback, "restore")
                
                return {
                    "success": True,
                    "message": f"Restored to operation {operation_id}",
                    "shape": self.df.shape
                }
            else:
                return {
                    "success": False,
                    "error": f"Could not restore to operation {operation_id}"
                }
                
        except Exception as e:
            logger.error(f"Error during restore: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def clear(self):
        """Clear session data to free memory."""
        # Stop auto-save if running
        await self.auto_save_manager.stop_periodic_save()
        
        # Clear history if enabled
        if self.history_manager:
            self.history_manager.clear_history()
        
        self.df = None
        self.original_df = None
        self.metadata.clear()
        self.operations_history.clear()


class SessionManager:
    """Manages multiple CSV sessions."""
    
    def __init__(self, max_sessions: int = 100, ttl_minutes: int = 60):
        """Initialize the session manager."""
        self.sessions: Dict[str, CSVSession] = {}
        self.max_sessions = max_sessions
        self.ttl_minutes = ttl_minutes
        self.sessions_to_cleanup: set = set()
        
    def create_session(self) -> str:
        """Create a new session."""
        self._cleanup_expired()
        
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest = min(self.sessions.values(), key=lambda s: s.last_accessed)
            del self.sessions[oldest.session_id]
            
        session = CSVSession(ttl_minutes=self.ttl_minutes)
        self.sessions[session.session_id] = session
        logger.info(f"Created new session: {session.session_id}")
        return session.session_id
        
    def get_session(self, session_id: str) -> Optional[CSVSession]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            session.update_access_time()
            return session
        elif session and session.is_expired():
            # Mark for cleanup but don't remove synchronously
            self.sessions_to_cleanup.add(session_id)
        return None
        
    async def remove_session(self, session_id: str) -> bool:
        """Remove a session."""
        if session_id in self.sessions:
            await self.sessions[session_id].clear()
            del self.sessions[session_id]
            logger.info(f"Removed session: {session_id}")
            return True
        return False
        
    def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions."""
        self._cleanup_expired()
        return [session.get_info() for session in self.sessions.values() if session.df is not None]
        
    def _cleanup_expired(self):
        """Mark expired sessions for cleanup."""
        expired = [sid for sid, session in self.sessions.items() if session.is_expired()]
        self.sessions_to_cleanup.update(expired)
        if expired:
            logger.info(f"Marked {len(expired)} expired sessions for cleanup")
    
    async def cleanup_marked_sessions(self):
        """Clean up sessions marked for removal."""
        for session_id in list(self.sessions_to_cleanup):
            await self.remove_session(session_id)
            self.sessions_to_cleanup.discard(session_id)
            
    def get_or_create_session(self, session_id: Optional[str] = None) -> CSVSession:
        """Get existing session or create new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        new_session_id = self.create_session()
        return self.sessions[new_session_id]
        
    def export_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session history as JSON."""
        session = self.get_session(session_id)
        if not session:
            return None
            
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "operations": session.operations_history,
            "metadata": session.metadata
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager