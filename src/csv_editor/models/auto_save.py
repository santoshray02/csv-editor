"""Auto-save functionality for CSV sessions."""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Literal
from enum import Enum
import logging
import pandas as pd
from ..models.data_models import ExportFormat

logger = logging.getLogger(__name__)


class AutoSaveMode(str, Enum):
    """Auto-save trigger modes."""
    
    DISABLED = "disabled"
    AFTER_OPERATION = "after_operation"  # Save after each operation
    PERIODIC = "periodic"  # Save at regular intervals
    HYBRID = "hybrid"  # Both after operation and periodic


class AutoSaveStrategy(str, Enum):
    """Auto-save file strategies."""
    
    OVERWRITE = "overwrite"  # Overwrite original file
    BACKUP = "backup"  # Create backup files with timestamp
    VERSIONED = "versioned"  # Keep numbered versions
    CUSTOM = "custom"  # Save to custom path


class AutoSaveConfig:
    """Configuration for auto-save functionality."""
    
    def __init__(
        self,
        enabled: bool = True,  # Changed to True by default
        mode: AutoSaveMode = AutoSaveMode.AFTER_OPERATION,  # Changed to save after each operation
        strategy: AutoSaveStrategy = AutoSaveStrategy.OVERWRITE,  # Changed to overwrite same file
        interval_seconds: int = 300,  # 5 minutes default
        max_backups: int = 10,
        backup_dir: Optional[str] = None,
        custom_path: Optional[str] = None,
        format: ExportFormat = ExportFormat.CSV,
        encoding: str = "utf-8"
    ):
        """Initialize auto-save configuration."""
        self.enabled = enabled
        self.mode = mode
        self.strategy = strategy
        self.interval_seconds = interval_seconds
        self.max_backups = max_backups
        self.backup_dir = backup_dir or os.path.join(os.getcwd(), ".csv_backups")
        self.custom_path = custom_path
        self.format = format
        self.encoding = encoding
        
        # Create backup directory if needed
        if self.enabled and self.strategy in [AutoSaveStrategy.BACKUP, AutoSaveStrategy.VERSIONED]:
            Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "enabled": self.enabled,
            "mode": self.mode.value,
            "strategy": self.strategy.value,
            "interval_seconds": self.interval_seconds,
            "max_backups": self.max_backups,
            "backup_dir": self.backup_dir,
            "custom_path": self.custom_path,
            "format": self.format.value,
            "encoding": self.encoding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AutoSaveConfig":
        """Create config from dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            mode=AutoSaveMode(data.get("mode", "disabled")),
            strategy=AutoSaveStrategy(data.get("strategy", "backup")),
            interval_seconds=data.get("interval_seconds", 300),
            max_backups=data.get("max_backups", 10),
            backup_dir=data.get("backup_dir"),
            custom_path=data.get("custom_path"),
            format=ExportFormat(data.get("format", "csv")),
            encoding=data.get("encoding", "utf-8")
        )


class AutoSaveManager:
    """Manages auto-save operations for a CSV session."""
    
    def __init__(self, session_id: str, config: AutoSaveConfig, original_file_path: Optional[str] = None):
        """Initialize auto-save manager."""
        self.session_id = session_id
        self.config = config
        self.original_file_path = original_file_path
        self.last_save = datetime.utcnow()
        self.save_count = 0
        self.periodic_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
    async def start_periodic_save(self, save_callback):
        """Start periodic auto-save task."""
        if self.config.mode in [AutoSaveMode.PERIODIC, AutoSaveMode.HYBRID]:
            self.periodic_task = asyncio.create_task(
                self._periodic_save_loop(save_callback)
            )
            logger.info(f"Started periodic auto-save for session {self.session_id}")
    
    async def stop_periodic_save(self):
        """Stop periodic auto-save task."""
        if self.periodic_task:
            self.periodic_task.cancel()
            try:
                await self.periodic_task
            except asyncio.CancelledError:
                pass
            self.periodic_task = None
            logger.info(f"Stopped periodic auto-save for session {self.session_id}")
    
    async def _periodic_save_loop(self, save_callback):
        """Periodic save loop."""
        while True:
            try:
                await asyncio.sleep(self.config.interval_seconds)
                await self.trigger_save(save_callback, "periodic")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic save: {str(e)}")
    
    async def trigger_save(self, save_callback, trigger: str = "manual") -> Dict[str, Any]:
        """Trigger an auto-save operation."""
        async with self._lock:
            try:
                # Determine save path based on strategy
                save_path = self._get_save_path()
                
                # Perform the save
                result = await save_callback(save_path, self.config.format, self.config.encoding)
                
                if result.get("success"):
                    self.last_save = datetime.utcnow()
                    self.save_count += 1
                    
                    # Clean up old backups if needed
                    if self.config.strategy in [AutoSaveStrategy.BACKUP, AutoSaveStrategy.VERSIONED]:
                        await self._cleanup_old_backups()
                    
                    logger.info(f"Auto-save successful for session {self.session_id} (trigger: {trigger})")
                    
                    return {
                        "success": True,
                        "save_path": save_path,
                        "trigger": trigger,
                        "save_count": self.save_count,
                        "timestamp": self.last_save.isoformat()
                    }
                else:
                    logger.error(f"Auto-save failed for session {self.session_id}: {result.get('error')}")
                    return {
                        "success": False,
                        "error": result.get("error"),
                        "trigger": trigger
                    }
                    
            except Exception as e:
                logger.error(f"Auto-save error for session {self.session_id}: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "trigger": trigger
                }
    
    def _get_save_path(self) -> str:
        """Determine the save path based on strategy."""
        if self.config.strategy == AutoSaveStrategy.CUSTOM:
            return self.config.custom_path or f"session_{self.session_id}.csv"
            
        elif self.config.strategy == AutoSaveStrategy.OVERWRITE:
            # Use the original file path if available, otherwise fall back
            if self.original_file_path:
                return self.original_file_path
            return f"session_{self.session_id}_autosave.csv"
            
        elif self.config.strategy == AutoSaveStrategy.BACKUP:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{self.session_id}_{timestamp}.{self.config.format.value}"
            return os.path.join(self.config.backup_dir, filename)
            
        elif self.config.strategy == AutoSaveStrategy.VERSIONED:
            version = self.save_count + 1
            filename = f"version_{self.session_id}_v{version:04d}.{self.config.format.value}"
            return os.path.join(self.config.backup_dir, filename)
            
        else:
            return f"session_{self.session_id}.{self.config.format.value}"
    
    async def _cleanup_old_backups(self):
        """Remove old backup files beyond max_backups limit."""
        if not os.path.exists(self.config.backup_dir):
            return
            
        try:
            # List all backup files for this session
            backup_pattern = f"*{self.session_id}*"
            backup_files = []
            
            for file_path in Path(self.config.backup_dir).glob(backup_pattern):
                if file_path.is_file():
                    backup_files.append({
                        "path": file_path,
                        "mtime": file_path.stat().st_mtime
                    })
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x["mtime"])
            
            # Remove excess backups
            while len(backup_files) > self.config.max_backups:
                oldest = backup_files.pop(0)
                oldest["path"].unlink()
                logger.info(f"Removed old backup: {oldest['path']}")
                
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
    
    def should_save_after_operation(self) -> bool:
        """Check if auto-save should trigger after an operation."""
        return (
            self.config.enabled and
            self.config.mode in [AutoSaveMode.AFTER_OPERATION, AutoSaveMode.HYBRID]
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get auto-save status."""
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode.value,
            "strategy": self.config.strategy.value,
            "last_save": self.last_save.isoformat() if self.last_save else None,
            "save_count": self.save_count,
            "periodic_active": self.periodic_task is not None and not self.periodic_task.done(),
            "config": self.config.to_dict()
        }