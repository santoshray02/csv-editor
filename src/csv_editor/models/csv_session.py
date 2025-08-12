"""Session management for CSV Editor MCP Server."""

import pandas as pd
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from pathlib import Path
import json

from .data_models import SessionInfo, OperationType

logger = logging.getLogger(__name__)


class CSVSession:
    """Represents a single CSV editing session."""
    
    def __init__(self, session_id: Optional[str] = None, ttl_minutes: int = 60):
        """Initialize a new CSV session."""
        self.session_id = session_id or str(uuid4())
        self.created_at = datetime.utcnow()
        self.last_accessed = datetime.utcnow()
        self.ttl = timedelta(minutes=ttl_minutes)
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.operations_history: List[Dict[str, Any]] = []
        self.file_path: Optional[str] = None
        
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
        self.operations_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": operation_type.value,
            "details": details
        })
        self.update_access_time()
        
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
        
    def clear(self):
        """Clear session data to free memory."""
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
            self.remove_session(session_id)
        return None
        
    def remove_session(self, session_id: str) -> bool:
        """Remove a session."""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            del self.sessions[session_id]
            logger.info(f"Removed session: {session_id}")
            return True
        return False
        
    def list_sessions(self) -> List[SessionInfo]:
        """List all active sessions."""
        self._cleanup_expired()
        return [session.get_info() for session in self.sessions.values() if session.df is not None]
        
    def _cleanup_expired(self):
        """Remove expired sessions."""
        expired = [sid for sid, session in self.sessions.items() if session.is_expired()]
        for sid in expired:
            self.remove_session(sid)
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
            
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