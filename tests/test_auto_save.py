"""Tests for auto-save functionality."""

import pytest
import asyncio
import os
import tempfile
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime

from src.csv_editor.models.csv_session import CSVSession, SessionManager
from src.csv_editor.models.auto_save import AutoSaveConfig, AutoSaveMode, AutoSaveStrategy
from src.csv_editor.models.data_models import ExportFormat


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'city': ['New York', 'London', 'Paris']
    })


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_auto_save_config_creation():
    """Test creating auto-save configuration."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP,
        interval_seconds=60,
        max_backups=5
    )
    
    assert config.enabled is True
    assert config.mode == AutoSaveMode.AFTER_OPERATION
    assert config.strategy == AutoSaveStrategy.BACKUP
    assert config.interval_seconds == 60
    assert config.max_backups == 5


@pytest.mark.asyncio
async def test_auto_save_config_from_dict():
    """Test creating auto-save config from dictionary."""
    config_dict = {
        "enabled": True,
        "mode": "periodic",
        "strategy": "versioned",
        "interval_seconds": 120,
        "max_backups": 10
    }
    
    config = AutoSaveConfig.from_dict(config_dict)
    
    assert config.enabled is True
    assert config.mode == AutoSaveMode.PERIODIC
    assert config.strategy == AutoSaveStrategy.VERSIONED
    assert config.interval_seconds == 120
    assert config.max_backups == 10


@pytest.mark.asyncio
async def test_session_with_auto_save_disabled(sample_df):
    """Test session with auto-save disabled."""
    config = AutoSaveConfig(enabled=False)
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Perform an operation
    session.record_operation("test_op", {"test": "data"})
    
    # Auto-save should not trigger
    result = await session.trigger_auto_save_if_needed()
    assert result is None


@pytest.mark.asyncio
async def test_session_with_auto_save_after_operation(sample_df, temp_dir):
    """Test auto-save after each operation."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Perform an operation
    session.record_operation("test_op", {"test": "data"})
    
    # Trigger auto-save
    result = await session.trigger_auto_save_if_needed()
    
    assert result is not None
    assert result["success"] is True
    assert result["trigger"] == "after_operation"
    
    # Check that backup file was created
    backup_files = list(Path(temp_dir).glob(f"*{session.session_id}*"))
    assert len(backup_files) == 1


@pytest.mark.asyncio
async def test_manual_save(sample_df, temp_dir):
    """Test manual save trigger."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.DISABLED,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Trigger manual save
    result = await session.manual_save()
    
    assert result["success"] is True
    assert result["trigger"] == "manual"
    
    # Check that backup file was created
    backup_files = list(Path(temp_dir).glob(f"*{session.session_id}*"))
    assert len(backup_files) == 1


@pytest.mark.asyncio
async def test_versioned_save_strategy(sample_df, temp_dir):
    """Test versioned save strategy."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.VERSIONED,
        backup_dir=temp_dir
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Trigger multiple saves
    for i in range(3):
        session.record_operation(f"test_op_{i}", {"index": i})
        await session.trigger_auto_save_if_needed()
    
    # Check that versioned files were created
    backup_files = sorted(Path(temp_dir).glob(f"version_{session.session_id}_v*.csv"))
    assert len(backup_files) == 3
    assert "v0001" in str(backup_files[0])
    assert "v0002" in str(backup_files[1])
    assert "v0003" in str(backup_files[2])


@pytest.mark.asyncio
async def test_max_backups_cleanup(sample_df, temp_dir):
    """Test that old backups are cleaned up when max_backups is exceeded."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir,
        max_backups=3
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Trigger more saves than max_backups
    for i in range(5):
        session.record_operation(f"test_op_{i}", {"index": i})
        await session.trigger_auto_save_if_needed()
        await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
    
    # Check that only max_backups files remain
    backup_files = list(Path(temp_dir).glob(f"*{session.session_id}*"))
    assert len(backup_files) <= config.max_backups


@pytest.mark.asyncio
async def test_periodic_save(sample_df, temp_dir):
    """Test periodic auto-save."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.PERIODIC,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir,
        interval_seconds=1  # 1 second for testing
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Start periodic save
    await session.auto_save_manager.start_periodic_save(session._save_callback)
    
    # Wait for periodic save to trigger
    await asyncio.sleep(1.5)
    
    # Stop periodic save
    await session.auto_save_manager.stop_periodic_save()
    
    # Check that backup file was created
    backup_files = list(Path(temp_dir).glob(f"*{session.session_id}*"))
    assert len(backup_files) >= 1


@pytest.mark.asyncio
async def test_hybrid_mode(sample_df, temp_dir):
    """Test hybrid mode (both periodic and after-operation)."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.HYBRID,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir,
        interval_seconds=2
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    # Start periodic save
    await session.auto_save_manager.start_periodic_save(session._save_callback)
    
    # Trigger operation-based save
    session.record_operation("test_op", {"test": "data"})
    result = await session.trigger_auto_save_if_needed()
    assert result["success"] is True
    
    # Wait for periodic save
    await asyncio.sleep(2.5)
    
    # Stop periodic save
    await session.auto_save_manager.stop_periodic_save()
    
    # Should have multiple backup files
    backup_files = list(Path(temp_dir).glob(f"*{session.session_id}*"))
    assert len(backup_files) >= 2


@pytest.mark.asyncio
async def test_different_export_formats(sample_df, temp_dir):
    """Test auto-save with different export formats."""
    formats = [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.TSV]
    
    for format in formats:
        config = AutoSaveConfig(
            enabled=True,
            mode=AutoSaveMode.AFTER_OPERATION,
            strategy=AutoSaveStrategy.BACKUP,
            backup_dir=temp_dir,
            format=format
        )
        
        session = CSVSession(auto_save_config=config)
        session.load_data(sample_df)
        
        # Trigger save
        session.record_operation("test_op", {"format": format.value})
        result = await session.trigger_auto_save_if_needed()
        
        assert result["success"] is True
        
        # Check file was created with correct extension
        pattern = f"*{session.session_id}*.{format.value}"
        files = list(Path(temp_dir).glob(pattern))
        assert len(files) == 1


@pytest.mark.asyncio
async def test_enable_disable_auto_save(sample_df, temp_dir):
    """Test enabling and disabling auto-save."""
    session = CSVSession()
    session.load_data(sample_df)
    
    # Initially disabled
    assert session.auto_save_config.enabled is False
    
    # Enable auto-save
    config_dict = {
        "enabled": True,
        "mode": "after_operation",
        "strategy": "backup",
        "backup_dir": temp_dir
    }
    result = await session.enable_auto_save(config_dict)
    assert result["success"] is True
    assert session.auto_save_config.enabled is True
    
    # Trigger save
    session.record_operation("test_op", {"test": "data"})
    save_result = await session.trigger_auto_save_if_needed()
    assert save_result["success"] is True
    
    # Disable auto-save
    result = await session.disable_auto_save()
    assert result["success"] is True
    assert session.auto_save_config.enabled is False
    
    # Save should not trigger
    session.record_operation("test_op_2", {"test": "data"})
    save_result = await session.trigger_auto_save_if_needed()
    assert save_result is None


@pytest.mark.asyncio
async def test_get_auto_save_status(sample_df):
    """Test getting auto-save status."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.AFTER_OPERATION,
        strategy=AutoSaveStrategy.BACKUP
    )
    
    session = CSVSession(auto_save_config=config)
    session.load_data(sample_df)
    
    status = session.get_auto_save_status()
    
    assert status["enabled"] is True
    assert status["mode"] == "after_operation"
    assert status["strategy"] == "backup"
    assert status["save_count"] == 0
    assert status["periodic_active"] is False
    
    # Trigger a save
    await session.manual_save()
    
    status = session.get_auto_save_status()
    assert status["save_count"] == 1


@pytest.mark.asyncio
async def test_session_manager_cleanup(sample_df, temp_dir):
    """Test that auto-save is stopped when session is removed."""
    config = AutoSaveConfig(
        enabled=True,
        mode=AutoSaveMode.PERIODIC,
        strategy=AutoSaveStrategy.BACKUP,
        backup_dir=temp_dir,
        interval_seconds=1
    )
    
    manager = SessionManager()
    session_id = manager.create_session()
    session = manager.get_session(session_id)
    
    # Enable auto-save
    await session.enable_auto_save(config.to_dict())
    session.load_data(sample_df)
    
    # Start periodic save
    await session.auto_save_manager.start_periodic_save(session._save_callback)
    
    # Remove session (should stop auto-save)
    removed = await manager.remove_session(session_id)
    assert removed is True
    
    # Verify periodic task was cancelled
    assert session.auto_save_manager.periodic_task is None or session.auto_save_manager.periodic_task.done()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])