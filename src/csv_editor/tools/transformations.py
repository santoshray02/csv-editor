"""Data transformation tools for CSV manipulation."""

from typing import Dict, Any, Optional, List, Union
from fastmcp import Context
import pandas as pd
import numpy as np
import logging

from ..models.csv_session import get_session_manager
from ..models.data_models import OperationType

logger = logging.getLogger(__name__)


async def filter_rows(
    session_id: str, 
    conditions: List[Dict[str, Any]], 
    mode: str = "and",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Filter rows based on conditions.
    
    Args:
        session_id: Session identifier
        conditions: List of filter conditions, each with:
            - column: Column name
            - operator: One of '==', '!=', '>', '<', '>=', '<=', 'contains', 'starts_with', 'ends_with', 'in', 'not_in', 'is_null', 'not_null'
            - value: Value to compare (not needed for is_null/not_null)
        mode: 'and' or 'or' to combine multiple conditions
        ctx: FastMCP context
        
    Returns:
        Dict with success status and filtered row count
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        mask = pd.Series([True] * len(df))
        
        for condition in conditions:
            column = condition.get("column")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if column not in df.columns:
                return {"success": False, "error": f"Column '{column}' not found"}
            
            col_data = df[column]
            
            if operator == "==":
                condition_mask = col_data == value
            elif operator == "!=":
                condition_mask = col_data != value
            elif operator == ">":
                condition_mask = col_data > value
            elif operator == "<":
                condition_mask = col_data < value
            elif operator == ">=":
                condition_mask = col_data >= value
            elif operator == "<=":
                condition_mask = col_data <= value
            elif operator == "contains":
                condition_mask = col_data.astype(str).str.contains(str(value), na=False)
            elif operator == "starts_with":
                condition_mask = col_data.astype(str).str.startswith(str(value), na=False)
            elif operator == "ends_with":
                condition_mask = col_data.astype(str).str.endswith(str(value), na=False)
            elif operator == "in":
                condition_mask = col_data.isin(value if isinstance(value, list) else [value])
            elif operator == "not_in":
                condition_mask = ~col_data.isin(value if isinstance(value, list) else [value])
            elif operator == "is_null":
                condition_mask = col_data.isna()
            elif operator == "not_null":
                condition_mask = col_data.notna()
            else:
                return {"success": False, "error": f"Unknown operator: {operator}"}
            
            if mode == "and":
                mask = mask & condition_mask
            else:
                mask = mask | condition_mask
        
        session.df = df[mask].reset_index(drop=True)
        session.record_operation(OperationType.FILTER, {
            "conditions": conditions,
            "mode": mode,
            "rows_before": len(df),
            "rows_after": len(session.df)
        })
        
        return {
            "success": True,
            "rows_before": len(df),
            "rows_after": len(session.df),
            "rows_filtered": len(df) - len(session.df)
        }
        
    except Exception as e:
        logger.error(f"Error filtering rows: {str(e)}")
        return {"success": False, "error": str(e)}


async def sort_data(
    session_id: str, 
    columns: List[Union[str, Dict[str, str]]], 
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Sort data by one or more columns.
    
    Args:
        session_id: Session identifier
        columns: List of column names or dicts with 'column' and 'ascending' keys
        ctx: FastMCP context
        
    Returns:
        Dict with success status
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Parse columns into names and ascending flags
        sort_columns = []
        ascending = []
        
        for col in columns:
            if isinstance(col, str):
                sort_columns.append(col)
                ascending.append(True)
            elif isinstance(col, dict):
                sort_columns.append(col["column"])
                ascending.append(col.get("ascending", True))
            else:
                return {"success": False, "error": f"Invalid column specification: {col}"}
        
        # Validate columns exist
        for col in sort_columns:
            if col not in df.columns:
                return {"success": False, "error": f"Column '{col}' not found"}
        
        session.df = df.sort_values(by=sort_columns, ascending=ascending).reset_index(drop=True)
        session.record_operation(OperationType.SORT, {
            "columns": sort_columns,
            "ascending": ascending
        })
        
        return {
            "success": True,
            "sorted_by": sort_columns,
            "ascending": ascending
        }
        
    except Exception as e:
        logger.error(f"Error sorting data: {str(e)}")
        return {"success": False, "error": str(e)}


async def select_columns(
    session_id: str, 
    columns: List[str], 
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Select specific columns from the dataframe.
    
    Args:
        session_id: Session identifier
        columns: List of column names to keep
        ctx: FastMCP context
        
    Returns:
        Dict with success status and selected columns
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            return {"success": False, "error": f"Columns not found: {missing_cols}"}
        
        session.df = df[columns].copy()
        session.record_operation(OperationType.SELECT, {
            "columns": columns,
            "columns_before": df.columns.tolist(),
            "columns_after": columns
        })
        
        return {
            "success": True,
            "selected_columns": columns,
            "columns_removed": [col for col in df.columns if col not in columns]
        }
        
    except Exception as e:
        logger.error(f"Error selecting columns: {str(e)}")
        return {"success": False, "error": str(e)}


async def rename_columns(
    session_id: str, 
    mapping: Dict[str, str], 
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Rename columns in the dataframe.
    
    Args:
        session_id: Session identifier
        mapping: Dict mapping old column names to new names
        ctx: FastMCP context
        
    Returns:
        Dict with success status and renamed columns
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Validate columns exist
        missing_cols = [col for col in mapping.keys() if col not in df.columns]
        if missing_cols:
            return {"success": False, "error": f"Columns not found: {missing_cols}"}
        
        session.df = df.rename(columns=mapping)
        session.record_operation(OperationType.RENAME, {
            "mapping": mapping
        })
        
        return {
            "success": True,
            "renamed": mapping,
            "columns": session.df.columns.tolist()
        }
        
    except Exception as e:
        logger.error(f"Error renaming columns: {str(e)}")
        return {"success": False, "error": str(e)}


async def add_column(
    session_id: str, 
    name: str,
    value: Any = None,
    formula: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Add a new column to the dataframe.
    
    Args:
        session_id: Session identifier
        name: Name for the new column
        value: Default value for all rows (scalar or list)
        formula: Python expression to calculate values (e.g., "col1 + col2")
        ctx: FastMCP context
        
    Returns:
        Dict with success status
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if name in df.columns:
            return {"success": False, "error": f"Column '{name}' already exists"}
        
        if formula:
            # Evaluate formula in the context of the dataframe
            try:
                session.df[name] = df.eval(formula)
            except Exception as e:
                return {"success": False, "error": f"Formula evaluation failed: {str(e)}"}
        elif isinstance(value, list):
            if len(value) != len(df):
                return {"success": False, "error": f"Value list length ({len(value)}) doesn't match row count ({len(df)})"}
            session.df[name] = value
        else:
            # Scalar value or None
            session.df[name] = value
        
        session.record_operation(OperationType.ADD_COLUMN, {
            "name": name,
            "value": str(value) if value is not None else None,
            "formula": formula
        })
        
        return {
            "success": True,
            "column_added": name,
            "columns": session.df.columns.tolist()
        }
        
    except Exception as e:
        logger.error(f"Error adding column: {str(e)}")
        return {"success": False, "error": str(e)}


async def remove_columns(
    session_id: str, 
    columns: List[str], 
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Remove columns from the dataframe.
    
    Args:
        session_id: Session identifier
        columns: List of column names to remove
        ctx: FastMCP context
        
    Returns:
        Dict with success status and removed columns
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            return {"success": False, "error": f"Columns not found: {missing_cols}"}
        
        session.df = df.drop(columns=columns)
        session.record_operation(OperationType.REMOVE_COLUMN, {
            "columns": columns
        })
        
        return {
            "success": True,
            "removed_columns": columns,
            "remaining_columns": session.df.columns.tolist()
        }
        
    except Exception as e:
        logger.error(f"Error removing columns: {str(e)}")
        return {"success": False, "error": str(e)}


async def change_column_type(
    session_id: str, 
    column: str, 
    dtype: str,
    errors: str = "coerce",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Change the data type of a column.
    
    Args:
        session_id: Session identifier
        column: Column name to change
        dtype: Target data type ('int', 'float', 'str', 'bool', 'datetime', 'category')
        errors: How to handle conversion errors ('raise', 'coerce', 'ignore')
        ctx: FastMCP context
        
    Returns:
        Dict with success status and conversion info
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}
        
        original_dtype = str(df[column].dtype)
        null_count_before = df[column].isna().sum()
        
        # Convert based on target dtype
        if dtype == "int":
            session.df[column] = pd.to_numeric(df[column], errors=errors).astype('Int64')
        elif dtype == "float":
            session.df[column] = pd.to_numeric(df[column], errors=errors)
        elif dtype == "str":
            session.df[column] = df[column].astype(str)
        elif dtype == "bool":
            session.df[column] = df[column].astype(bool)
        elif dtype == "datetime":
            session.df[column] = pd.to_datetime(df[column], errors=errors)
        elif dtype == "category":
            session.df[column] = df[column].astype('category')
        else:
            return {"success": False, "error": f"Unsupported dtype: {dtype}"}
        
        null_count_after = session.df[column].isna().sum()
        
        session.record_operation(OperationType.CHANGE_TYPE, {
            "column": column,
            "from_type": original_dtype,
            "to_type": dtype,
            "errors": errors
        })
        
        return {
            "success": True,
            "column": column,
            "original_type": original_dtype,
            "new_type": str(session.df[column].dtype),
            "null_count_before": int(null_count_before),
            "null_count_after": int(null_count_after),
            "conversion_errors": int(null_count_after - null_count_before)
        }
        
    except Exception as e:
        logger.error(f"Error changing column type: {str(e)}")
        return {"success": False, "error": str(e)}


async def fill_missing_values(
    session_id: str,
    strategy: str = "drop",
    value: Any = None,
    columns: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Fill or remove missing values.
    
    Args:
        session_id: Session identifier
        strategy: One of 'drop', 'fill', 'forward', 'backward', 'mean', 'median', 'mode'
        value: Value to fill with (for 'fill' strategy)
        columns: Specific columns to apply to (None for all)
        ctx: FastMCP context
        
    Returns:
        Dict with success status and fill info
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        null_counts_before = df.isnull().sum().to_dict()
        
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            target_cols = columns
        else:
            target_cols = df.columns.tolist()
        
        if strategy == "drop":
            session.df = df.dropna(subset=target_cols)
        elif strategy == "fill":
            if value is None:
                return {"success": False, "error": "Value required for 'fill' strategy"}
            session.df[target_cols] = df[target_cols].fillna(value)
        elif strategy == "forward":
            session.df[target_cols] = df[target_cols].fillna(method='ffill')
        elif strategy == "backward":
            session.df[target_cols] = df[target_cols].fillna(method='bfill')
        elif strategy == "mean":
            for col in target_cols:
                if df[col].dtype in ['int64', 'float64']:
                    session.df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            for col in target_cols:
                if df[col].dtype in ['int64', 'float64']:
                    session.df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            for col in target_cols:
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    session.df[col] = df[col].fillna(mode_val[0])
        else:
            return {"success": False, "error": f"Unknown strategy: {strategy}"}
        
        null_counts_after = session.df.isnull().sum().to_dict()
        
        session.record_operation(OperationType.FILL_MISSING, {
            "strategy": strategy,
            "value": str(value) if value is not None else None,
            "columns": target_cols
        })
        
        return {
            "success": True,
            "strategy": strategy,
            "rows_before": len(df),
            "rows_after": len(session.df),
            "null_counts_before": null_counts_before,
            "null_counts_after": null_counts_after
        }
        
    except Exception as e:
        logger.error(f"Error filling missing values: {str(e)}")
        return {"success": False, "error": str(e)}


async def update_column(
    session_id: str,
    column: str,
    operation: str,
    value: Optional[Any] = None,
    pattern: Optional[str] = None,
    replacement: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Update values in a specific column with simple operations.
    
    Args:
        session_id: Session identifier
        column: Column name to update
        operation: Operation type - 'replace', 'extract', 'split', 'strip', 'upper', 'lower', 'fill'
        value: Value for certain operations (e.g., fill value)
        pattern: Pattern for replace/extract operations (regex supported)
        replacement: Replacement string for replace operation
        ctx: FastMCP context
        
    Returns:
        Dict with success status and update info
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}
        
        original_values_sample = df[column].head(5).tolist()
        
        if operation == "replace":
            if pattern is None or replacement is None:
                return {"success": False, "error": "Pattern and replacement required for replace operation"}
            session.df[column] = df[column].astype(str).str.replace(pattern, replacement, regex=True)
            
        elif operation == "extract":
            if pattern is None:
                return {"success": False, "error": "Pattern required for extract operation"}
            session.df[column] = df[column].astype(str).str.extract(pattern, expand=False)
            
        elif operation == "split":
            if pattern is None:
                pattern = " "
            if value is not None and isinstance(value, int):
                # Extract specific part after split
                session.df[column] = df[column].astype(str).str.split(pattern).str[value]
            else:
                # Just do the split, take first part
                session.df[column] = df[column].astype(str).str.split(pattern).str[0]
                
        elif operation == "strip":
            session.df[column] = df[column].astype(str).str.strip()
            
        elif operation == "upper":
            session.df[column] = df[column].astype(str).str.upper()
            
        elif operation == "lower":
            session.df[column] = df[column].astype(str).str.lower()
            
        elif operation == "fill":
            if value is None:
                return {"success": False, "error": "Value required for fill operation"}
            session.df[column] = df[column].fillna(value)
            
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}
        
        updated_values_sample = session.df[column].head(5).tolist()
        
        session.record_operation(OperationType.UPDATE_COLUMN, {
            "column": column,
            "operation": operation,
            "pattern": pattern,
            "replacement": replacement,
            "value": str(value) if value is not None else None
        })
        
        return {
            "success": True,
            "column": column,
            "operation": operation,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df)
        }
        
    except Exception as e:
        logger.error(f"Error updating column: {str(e)}")
        return {"success": False, "error": str(e)}


async def remove_duplicates(
    session_id: str,
    subset: Optional[List[str]] = None,
    keep: str = "first",
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Remove duplicate rows.
    
    Args:
        session_id: Session identifier
        subset: Column names to consider for duplicates (None for all)
        keep: Which duplicates to keep ('first', 'last', False to drop all)
        ctx: FastMCP context
        
    Returns:
        Dict with success status and duplicate info
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        rows_before = len(df)
        
        if subset:
            missing_cols = [col for col in subset if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
        
        # Convert keep parameter
        keep_param = keep if keep != "none" else False
        
        session.df = df.drop_duplicates(subset=subset, keep=keep_param).reset_index(drop=True)
        rows_after = len(session.df)
        
        session.record_operation(OperationType.REMOVE_DUPLICATES, {
            "subset": subset,
            "keep": keep,
            "rows_removed": rows_before - rows_after
        })
        
        return {
            "success": True,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "duplicates_removed": rows_before - rows_after,
            "subset": subset,
            "keep": keep
        }
        
    except Exception as e:
        logger.error(f"Error removing duplicates: {str(e)}")
        return {"success": False, "error": str(e)}