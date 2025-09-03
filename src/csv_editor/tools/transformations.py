"""Data transformation tools for CSV manipulation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

import pandas as pd

from ..models.csv_session import get_session_manager
from ..models.data_models import OperationType

if TYPE_CHECKING:
    from fastmcp import Context

logger = logging.getLogger(__name__)


async def filter_rows(
    session_id: str,
    conditions: list[dict[str, Any]],
    mode: str = "and",
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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

            mask = mask & condition_mask if mode == "and" else mask | condition_mask

        session.df = df[mask].reset_index(drop=True)
        session.record_operation(
            OperationType.FILTER,
            {
                "conditions": conditions,
                "mode": mode,
                "rows_before": len(df),
                "rows_after": len(session.df),
            },
        )

        return {
            "success": True,
            "rows_before": len(df),
            "rows_after": len(session.df),
            "rows_filtered": len(df) - len(session.df),
        }

    except Exception as e:
        logger.error(f"Error filtering rows: {e!s}")
        return {"success": False, "error": str(e)}


async def sort_data(
    session_id: str, columns: list[str | dict[str, str]], ctx: Context | None = None  # noqa: ARG001
) -> dict[str, Any]:
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
        sort_columns: list[str] = []
        ascending: list[bool] = []

        for col in columns:
            if isinstance(col, str):
                sort_columns.append(col)
                ascending.append(True)
            elif isinstance(col, dict):
                sort_columns.append(col["column"])
                ascending.append(bool(col.get("ascending", True)))
            else:
                return {"success": False, "error": f"Invalid column specification: {col}"}

        # Validate columns exist
        for col in sort_columns:
            if col not in df.columns:
                return {"success": False, "error": f"Column '{col}' not found"}

        session.df = df.sort_values(by=sort_columns, ascending=ascending).reset_index(drop=True)
        session.record_operation(
            OperationType.SORT, {"columns": sort_columns, "ascending": ascending}
        )

        return {"success": True, "sorted_by": sort_columns, "ascending": ascending}

    except Exception as e:
        logger.error(f"Error sorting data: {e!s}")
        return {"success": False, "error": str(e)}


async def select_columns(
    session_id: str, columns: list[str], ctx: Context | None = None  # noqa: ARG001
) -> dict[str, Any]:
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
        session.record_operation(
            OperationType.SELECT,
            {"columns": columns, "columns_before": df.columns.tolist(), "columns_after": columns},
        )

        return {
            "success": True,
            "selected_columns": columns,
            "columns_removed": [col for col in df.columns if col not in columns],
        }

    except Exception as e:
        logger.error(f"Error selecting columns: {e!s}")
        return {"success": False, "error": str(e)}


async def rename_columns(
    session_id: str, mapping: dict[str, str], ctx: Context | None = None  # noqa: ARG001
) -> dict[str, Any]:
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
        missing_cols = [col for col in mapping if col not in df.columns]
        if missing_cols:
            return {"success": False, "error": f"Columns not found: {missing_cols}"}

        session.df = df.rename(columns=mapping)
        session.record_operation(OperationType.RENAME, {"mapping": mapping})

        return {"success": True, "renamed": mapping, "columns": session.df.columns.tolist()}

    except Exception as e:
        logger.error(f"Error renaming columns: {e!s}")
        return {"success": False, "error": str(e)}


async def add_column(
    session_id: str,
    name: str,
    value: Any = None,
    formula: str | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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
                return {"success": False, "error": f"Formula evaluation failed: {e!s}"}
        elif isinstance(value, list):
            if len(value) != len(df):
                return {
                    "success": False,
                    "error": f"Value list length ({len(value)}) doesn't match row count ({len(df)})",
                }
            session.df[name] = value
        else:
            # Scalar value or None
            session.df[name] = value

        session.record_operation(
            OperationType.ADD_COLUMN,
            {"name": name, "value": str(value) if value is not None else None, "formula": formula},
        )

        return {"success": True, "column_added": name, "columns": session.df.columns.tolist()}

    except Exception as e:
        logger.error(f"Error adding column: {e!s}")
        return {"success": False, "error": str(e)}


async def remove_columns(
    session_id: str, columns: list[str], ctx: Context | None = None  # noqa: ARG001
) -> dict[str, Any]:
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
        session.record_operation(OperationType.REMOVE_COLUMN, {"columns": columns})

        return {
            "success": True,
            "removed_columns": columns,
            "remaining_columns": session.df.columns.tolist(),
        }

    except Exception as e:
        logger.error(f"Error removing columns: {e!s}")
        return {"success": False, "error": str(e)}


async def change_column_type(
    session_id: str,
    column: str,
    dtype: str,
    errors: Literal["raise", "coerce"] = "coerce",
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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
            session.df[column] = pd.to_numeric(df[column], errors=errors).astype("Int64")
        elif dtype == "float":
            session.df[column] = pd.to_numeric(df[column], errors=errors)
        elif dtype == "str":
            session.df[column] = df[column].astype(str)
        elif dtype == "bool":
            session.df[column] = df[column].astype(bool)
        elif dtype == "datetime":
            session.df[column] = pd.to_datetime(df[column], errors=errors)
        elif dtype == "category":
            session.df[column] = df[column].astype("category")
        else:
            return {"success": False, "error": f"Unsupported dtype: {dtype}"}

        null_count_after = session.df[column].isna().sum()

        session.record_operation(
            OperationType.CHANGE_TYPE,
            {"column": column, "from_type": original_dtype, "to_type": dtype, "errors": errors},
        )

        return {
            "success": True,
            "column": column,
            "original_type": original_dtype,
            "new_type": str(session.df[column].dtype),
            "null_count_before": int(null_count_before),
            "null_count_after": int(null_count_after),
            "conversion_errors": int(null_count_after - null_count_before),
        }

    except Exception as e:
        logger.error(f"Error changing column type: {e!s}")
        return {"success": False, "error": str(e)}


async def fill_missing_values(
    session_id: str,
    strategy: str = "drop",
    value: Any = None,
    columns: list[str] | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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
            session.df[target_cols] = df[target_cols].ffill()
        elif strategy == "backward":
            session.df[target_cols] = df[target_cols].bfill()
        elif strategy == "mean":
            for col in target_cols:
                if df[col].dtype in ["int64", "float64"]:
                    session.df[col] = df[col].fillna(df[col].mean())
        elif strategy == "median":
            for col in target_cols:
                if df[col].dtype in ["int64", "float64"]:
                    session.df[col] = df[col].fillna(df[col].median())
        elif strategy == "mode":
            for col in target_cols:
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    session.df[col] = df[col].fillna(mode_val[0])
        else:
            return {"success": False, "error": f"Unknown strategy: {strategy}"}

        null_counts_after = session.df.isnull().sum().to_dict()

        session.record_operation(
            OperationType.FILL_MISSING,
            {
                "strategy": strategy,
                "value": str(value) if value is not None else None,
                "columns": target_cols,
            },
        )

        return {
            "success": True,
            "strategy": strategy,
            "rows_before": len(df),
            "rows_after": len(session.df),
            "null_counts_before": null_counts_before,
            "null_counts_after": null_counts_after,
        }

    except Exception as e:
        logger.error(f"Error filling missing values: {e!s}")
        return {"success": False, "error": str(e)}


async def update_column(
    session_id: str,
    column: str,
    operation: str,
    value: Any | None = None,
    pattern: str | None = None,
    replacement: str | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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
                return {
                    "success": False,
                    "error": "Pattern and replacement required for replace operation",
                }
            session.df[column] = (
                df[column].astype(str).str.replace(pattern, replacement, regex=True)
            )

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

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "column": column,
                "operation": operation,
                "pattern": pattern,
                "replacement": replacement,
                "value": str(value) if value is not None else None,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": operation,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error updating column: {e!s}")
        return {"success": False, "error": str(e)}


async def remove_duplicates(
    session_id: str,
    subset: list[str] | None = None,
    keep: Literal["first", "last", "none"] = "first",
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
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
        keep_param: Literal["first", "last"] | Literal[False] = keep if keep != "none" else False

        session.df = df.drop_duplicates(subset=subset, keep=keep_param).reset_index(drop=True)
        rows_after = len(session.df)

        session.record_operation(
            OperationType.REMOVE_DUPLICATES,
            {"subset": subset, "keep": keep, "rows_removed": rows_before - rows_after},
        )

        return {
            "success": True,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "duplicates_removed": rows_before - rows_after,
            "subset": subset,
            "keep": keep,
        }

    except Exception as e:
        logger.error(f"Error removing duplicates: {e!s}")
        return {"success": False, "error": str(e)}


# ============================================================================
# CELL-LEVEL ACCESS METHODS
# ============================================================================


async def get_cell_value(
    session_id: str,
    row_index: int,
    column: str | int,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Get the value of a specific cell.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        column: Column name (str) or column index (int, 0-based)
        ctx: FastMCP context

    Returns:
        Dict with success status and cell value

    Example:
        get_cell_value("session123", 0, "name") -> {"success": True, "value": "John", "coordinates": {"row": 0, "column": "name"}}
        get_cell_value("session123", 2, 1) -> {"success": True, "value": 25, "coordinates": {"row": 2, "column": "age"}}
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}

        df = session.df

        # Validate row index
        if row_index < 0 or row_index >= len(df):
            return {
                "success": False,
                "error": f"Row index {row_index} out of range (0-{len(df)-1})",
            }

        # Handle column specification
        if isinstance(column, int):
            # Column index
            if column < 0 or column >= len(df.columns):
                return {
                    "success": False,
                    "error": f"Column index {column} out of range (0-{len(df.columns)-1})",
                }
            column_name = df.columns[column]
        else:
            # Column name
            if column not in df.columns:
                return {"success": False, "error": f"Column '{column}' not found"}
            column_name = column

        # Get the cell value
        cell_value = df.iloc[row_index][column_name]

        # Handle pandas/numpy types for JSON serialization
        if pd.isna(cell_value):
            cell_value = None
        elif hasattr(cell_value, 'item'):
            cell_value = cell_value.item()

        return {
            "success": True,
            "value": cell_value,
            "coordinates": {"row": row_index, "column": column_name},
            "data_type": str(df.dtypes[column_name]),
        }

    except Exception as e:
        logger.error(f"Error getting cell value: {e!s}")
        return {"success": False, "error": str(e)}


async def set_cell_value(
    session_id: str,
    row_index: int,
    column: str | int,
    value: Any,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Set the value of a specific cell.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        column: Column name (str) or column index (int, 0-based)
        value: New value for the cell
        ctx: FastMCP context

    Returns:
        Dict with success status and update info

    Example:
        set_cell_value("session123", 0, "name", "Jane") -> {"success": True, "old_value": "John", "new_value": "Jane"}
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}

        df = session.df

        # Validate row index
        if row_index < 0 or row_index >= len(df):
            return {
                "success": False,
                "error": f"Row index {row_index} out of range (0-{len(df)-1})",
            }

        # Handle column specification
        if isinstance(column, int):
            # Column index
            if column < 0 or column >= len(df.columns):
                return {
                    "success": False,
                    "error": f"Column index {column} out of range (0-{len(df.columns)-1})",
                }
            column_name = df.columns[column]
        else:
            # Column name
            if column not in df.columns:
                return {"success": False, "error": f"Column '{column}' not found"}
            column_name = column

        # Get old value
        old_value = df.iloc[row_index][column_name]
        if pd.isna(old_value):
            old_value = None
        elif hasattr(old_value, 'item'):
            old_value = old_value.item()

        # Set new value
        session.df.iloc[row_index, session.df.columns.get_loc(column_name)] = value

        # Record operation
        session.record_operation(
            OperationType.UPDATE_COLUMN,  # Reuse existing operation type
            {
                "operation": "set_cell",
                "coordinates": {"row": row_index, "column": column_name},
                "old_value": str(old_value) if old_value is not None else None,
                "new_value": str(value) if value is not None else None,
            },
        )

        return {
            "success": True,
            "coordinates": {"row": row_index, "column": column_name},
            "old_value": old_value,
            "new_value": value,
            "data_type": str(df.dtypes[column_name]),
        }

    except Exception as e:
        logger.error(f"Error setting cell value: {e!s}")
        return {"success": False, "error": str(e)}


async def get_row_data(
    session_id: str,
    row_index: int,
    columns: list[str] | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Get data from a specific row.

    Args:
        session_id: Session identifier
        row_index: Row index (0-based)
        columns: Optional list of column names to include (None for all columns)
        ctx: FastMCP context

    Returns:
        Dict with success status and row data

    Example:
        get_row_data("session123", 0) -> {"success": True, "data": {"name": "John", "age": 30}, "row_index": 0}
        get_row_data("session123", 1, ["name", "age"]) -> {"success": True, "data": {"name": "Jane", "age": 25}}
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}

        df = session.df

        # Validate row index
        if row_index < 0 or row_index >= len(df):
            return {
                "success": False,
                "error": f"Row index {row_index} out of range (0-{len(df)-1})",
            }

        # Get row data
        if columns is None:
            row_data = df.iloc[row_index].to_dict()
        else:
            # Validate columns exist
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            
            row_data = df.iloc[row_index][columns].to_dict()

        # Handle pandas/numpy types for JSON serialization
        for key, value in row_data.items():
            if pd.isna(value):
                row_data[key] = None
            elif hasattr(value, 'item'):
                row_data[key] = value.item()

        return {
            "success": True,
            "row_index": row_index,
            "data": row_data,
            "columns_included": list(row_data.keys()),
        }

    except Exception as e:
        logger.error(f"Error getting row data: {e!s}")
        return {"success": False, "error": str(e)}


async def get_column_data(
    session_id: str,
    column: str,
    start_row: int | None = None,
    end_row: int | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Get data from a specific column, optionally sliced by row range.

    Args:
        session_id: Session identifier
        column: Column name
        start_row: Starting row index (0-based, inclusive). None for beginning
        end_row: Ending row index (0-based, exclusive). None for end
        ctx: FastMCP context

    Returns:
        Dict with success status and column data

    Example:
        get_column_data("session123", "age") -> {"success": True, "data": [30, 25, 35], "column": "age"}
        get_column_data("session123", "name", 0, 2) -> {"success": True, "data": ["John", "Jane"]}
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}

        df = session.df

        # Validate column exists
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}

        # Validate and set row range
        total_rows = len(df)
        if start_row is None:
            start_row = 0
        if end_row is None:
            end_row = total_rows

        if start_row < 0 or start_row >= total_rows:
            return {
                "success": False,
                "error": f"Start row {start_row} out of range (0-{total_rows-1})",
            }

        if end_row < start_row or end_row > total_rows:
            return {
                "success": False,
                "error": f"End row {end_row} invalid (must be > start_row and <= {total_rows})",
            }

        # Get column data slice
        column_data = df[column].iloc[start_row:end_row].tolist()

        # Handle pandas/numpy types for JSON serialization
        for i, value in enumerate(column_data):
            if pd.isna(value):
                column_data[i] = None
            elif hasattr(value, 'item'):
                column_data[i] = value.item()

        return {
            "success": True,
            "column": column,
            "data": column_data,
            "start_row": start_row,
            "end_row": end_row,
            "count": len(column_data),
            "data_type": str(df.dtypes[column]),
        }

    except Exception as e:
        logger.error(f"Error getting column data: {e!s}")
        return {"success": False, "error": str(e)}


# ============================================================================
# FOCUSED COLUMN UPDATE METHODS (Replacing operation-parameter pattern)
# ============================================================================


async def replace_in_column(
    session_id: str,
    column: str,
    pattern: str,
    replacement: str,
    regex: bool = True,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Replace patterns in a column with replacement text.

    Args:
        session_id: Session identifier
        column: Column name to update
        pattern: Pattern to search for (regex or literal string)
        replacement: Replacement string
        regex: Whether to treat pattern as regex (default: True)
        ctx: FastMCP context

    Returns:
        Dict with success status and replacement info

    Example:
        replace_in_column("session123", "name", "Mr\\.", "Mister") -> Replace "Mr." with "Mister"
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

        # Perform replacement
        session.df[column] = df[column].astype(str).str.replace(pattern, replacement, regex=regex)

        updated_values_sample = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "replace",
                "column": column,
                "pattern": pattern,
                "replacement": replacement,
                "regex": regex,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": "replace",
            "pattern": pattern,
            "replacement": replacement,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error replacing in column: {e!s}")
        return {"success": False, "error": str(e)}


async def extract_from_column(
    session_id: str,
    column: str,
    pattern: str,
    expand: bool = False,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Extract patterns from a column using regex.

    Args:
        session_id: Session identifier
        column: Column name to update
        pattern: Regex pattern to extract (use capturing groups)
        expand: Whether to expand to multiple columns if multiple groups
        ctx: FastMCP context

    Returns:
        Dict with success status and extraction info

    Example:
        extract_from_column("session123", "email", r"(.+)@(.+)") -> Extract username and domain
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

        # Perform extraction
        session.df[column] = df[column].astype(str).str.extract(pattern, expand=expand)

        updated_values_sample = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "extract",
                "column": column,
                "pattern": pattern,
                "expand": expand,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": "extract",
            "pattern": pattern,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error extracting from column: {e!s}")
        return {"success": False, "error": str(e)}


async def split_column(
    session_id: str,
    column: str,
    delimiter: str = " ",
    part_index: int | None = None,
    expand_to_columns: bool = False,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Split column values by delimiter.

    Args:
        session_id: Session identifier
        column: Column name to update
        delimiter: String to split on (default: space)
        part_index: Which part to keep (0-based index). None keeps first part
        expand_to_columns: Whether to expand splits into multiple columns
        ctx: FastMCP context

    Returns:
        Dict with success status and split info

    Example:
        split_column("session123", "name", " ", 0) -> Keep first part of name
        split_column("session123", "full_name", " ", expand_to_columns=True) -> Split into multiple columns
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

        # Perform split
        if expand_to_columns:
            # Split into multiple columns
            split_data = df[column].astype(str).str.split(delimiter, expand=True)
            # Replace original column with split columns
            for i, col_data in enumerate(split_data.columns):
                session.df[f"{column}_{i}"] = split_data[col_data]
            # Drop original column
            session.df = session.df.drop(columns=[column])
            updated_info = f"Expanded to {len(split_data.columns)} columns"
        else:
            # Keep specific part
            if part_index is not None:
                session.df[column] = df[column].astype(str).str.split(delimiter).str[part_index]
            else:
                # Keep first part by default
                session.df[column] = df[column].astype(str).str.split(delimiter).str[0]
            updated_info = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "split",
                "column": column,
                "delimiter": delimiter,
                "part_index": part_index,
                "expand_to_columns": expand_to_columns,
            },
        )

        result = {
            "success": True,
            "column": column,
            "operation": "split",
            "delimiter": delimiter,
            "original_sample": original_values_sample,
            "rows_updated": len(session.df),
        }

        if expand_to_columns:
            result["expanded_columns"] = [f"{column}_{i}" for i in range(len(split_data.columns))]
            result["info"] = updated_info
        else:
            result["part_index"] = part_index if part_index is not None else 0
            result["updated_sample"] = updated_info

        return result

    except Exception as e:
        logger.error(f"Error splitting column: {e!s}")
        return {"success": False, "error": str(e)}


async def transform_column_case(
    session_id: str,
    column: str,
    transform: Literal["upper", "lower", "title", "capitalize"],
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Transform the case of text in a column.

    Args:
        session_id: Session identifier
        column: Column name to update
        transform: Type of case transformation
        ctx: FastMCP context

    Returns:
        Dict with success status and transformation info

    Example:
        transform_column_case("session123", "name", "title") -> "john doe" becomes "John Doe"
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

        # Perform case transformation
        if transform == "upper":
            session.df[column] = df[column].astype(str).str.upper()
        elif transform == "lower":
            session.df[column] = df[column].astype(str).str.lower()
        elif transform == "title":
            session.df[column] = df[column].astype(str).str.title()
        elif transform == "capitalize":
            session.df[column] = df[column].astype(str).str.capitalize()
        else:
            return {"success": False, "error": f"Unknown transform: {transform}"}

        updated_values_sample = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "transform_case",
                "column": column,
                "transform": transform,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": "transform_case",
            "transform": transform,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error transforming column case: {e!s}")
        return {"success": False, "error": str(e)}


async def strip_column(
    session_id: str,
    column: str,
    chars: str | None = None,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Strip whitespace or specified characters from column values.

    Args:
        session_id: Session identifier
        column: Column name to update
        chars: Characters to strip (None for whitespace)
        ctx: FastMCP context

    Returns:
        Dict with success status and strip info

    Example:
        strip_column("session123", "name") -> Remove leading/trailing whitespace
        strip_column("session123", "code", "()") -> Remove parentheses from ends
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

        # Perform strip
        if chars is None:
            session.df[column] = df[column].astype(str).str.strip()
        else:
            session.df[column] = df[column].astype(str).str.strip(chars)

        updated_values_sample = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "strip",
                "column": column,
                "chars": chars,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": "strip",
            "chars": chars,
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error stripping column: {e!s}")
        return {"success": False, "error": str(e)}


async def fill_column_nulls(
    session_id: str,
    column: str,
    value: Any,
    ctx: Context | None = None,  # noqa: ARG001
) -> dict[str, Any]:
    """
    Fill null/NaN values in a column with a specified value.

    Args:
        session_id: Session identifier
        column: Column name to update
        value: Value to use for filling nulls
        ctx: FastMCP context

    Returns:
        Dict with success status and fill info

    Example:
        fill_column_nulls("session123", "age", 0) -> Replace NaN ages with 0
        fill_column_nulls("session123", "name", "Unknown") -> Replace missing names with "Unknown"
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)

        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}

        df = session.df

        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}

        # Count null values before
        nulls_before = df[column].isna().sum()
        original_values_sample = df[column].head(5).tolist()

        # Fill nulls
        session.df[column] = df[column].fillna(value)

        # Count nulls after
        nulls_after = session.df[column].isna().sum()
        updated_values_sample = session.df[column].head(5).tolist()

        session.record_operation(
            OperationType.UPDATE_COLUMN,
            {
                "operation": "fill_nulls",
                "column": column,
                "value": str(value),
                "nulls_filled": nulls_before - nulls_after,
            },
        )

        return {
            "success": True,
            "column": column,
            "operation": "fill_nulls",
            "value": value,
            "nulls_before": int(nulls_before),
            "nulls_after": int(nulls_after),
            "nulls_filled": int(nulls_before - nulls_after),
            "original_sample": original_values_sample,
            "updated_sample": updated_values_sample,
            "rows_updated": len(session.df),
        }

    except Exception as e:
        logger.error(f"Error filling column nulls: {e!s}")
        return {"success": False, "error": str(e)}
