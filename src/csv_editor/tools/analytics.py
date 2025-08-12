"""Analytics tools for CSV data analysis."""

from typing import Dict, Any, Optional, List, Union
from fastmcp import Context
import pandas as pd
import numpy as np
import logging
from datetime import datetime

from ..models.csv_session import get_session_manager
from ..models.data_models import OperationType

logger = logging.getLogger(__name__)


async def get_statistics(
    session_id: str, 
    columns: Optional[List[str]] = None,
    include_percentiles: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get statistical summary of numerical columns.
    
    Args:
        session_id: Session identifier
        columns: Specific columns to analyze (None for all numeric)
        include_percentiles: Include percentile values
        ctx: FastMCP context
        
    Returns:
        Dict with statistics for each column
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Select columns to analyze
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            numeric_df = df[columns].select_dtypes(include=[np.number])
        else:
            numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"success": False, "error": "No numeric columns found"}
        
        # Calculate statistics
        stats = {}
        percentiles = [0.25, 0.5, 0.75] if include_percentiles else []
        
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            
            col_stats = {
                "count": int(col_data.count()),
                "null_count": int(df[col].isna().sum()),
                "mean": float(col_data.mean()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "sum": float(col_data.sum()),
                "variance": float(col_data.var()),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurt())
            }
            
            if include_percentiles:
                col_stats["25%"] = float(col_data.quantile(0.25))
                col_stats["50%"] = float(col_data.quantile(0.50))
                col_stats["75%"] = float(col_data.quantile(0.75))
                col_stats["iqr"] = col_stats["75%"] - col_stats["25%"]
            
            stats[col] = col_stats
        
        session.record_operation(OperationType.ANALYZE, {
            "type": "statistics",
            "columns": list(stats.keys())
        })
        
        return {
            "success": True,
            "statistics": stats,
            "columns_analyzed": list(stats.keys()),
            "total_rows": len(df)
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_column_statistics(
    session_id: str,
    column: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific column.
    
    Args:
        session_id: Session identifier
        column: Column name to analyze
        ctx: FastMCP context
        
    Returns:
        Dict with detailed column statistics
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}
        
        col_data = df[column]
        result = {
            "column": column,
            "dtype": str(col_data.dtype),
            "total_count": len(col_data),
            "null_count": int(col_data.isna().sum()),
            "null_percentage": round(col_data.isna().sum() / len(col_data) * 100, 2),
            "unique_count": int(col_data.nunique()),
            "unique_percentage": round(col_data.nunique() / len(col_data) * 100, 2)
        }
        
        # Numeric column statistics
        if pd.api.types.is_numeric_dtype(col_data):
            non_null = col_data.dropna()
            result.update({
                "type": "numeric",
                "mean": float(non_null.mean()),
                "median": float(non_null.median()),
                "mode": float(non_null.mode()[0]) if len(non_null.mode()) > 0 else None,
                "std": float(non_null.std()),
                "variance": float(non_null.var()),
                "min": float(non_null.min()),
                "max": float(non_null.max()),
                "range": float(non_null.max() - non_null.min()),
                "sum": float(non_null.sum()),
                "skewness": float(non_null.skew()),
                "kurtosis": float(non_null.kurt()),
                "25%": float(non_null.quantile(0.25)),
                "50%": float(non_null.quantile(0.50)),
                "75%": float(non_null.quantile(0.75)),
                "iqr": float(non_null.quantile(0.75) - non_null.quantile(0.25)),
                "zero_count": int((col_data == 0).sum()),
                "positive_count": int((col_data > 0).sum()),
                "negative_count": int((col_data < 0).sum())
            })
        
        # Categorical column statistics
        else:
            value_counts = col_data.value_counts()
            top_values = value_counts.head(10).to_dict()
            
            result.update({
                "type": "categorical",
                "most_frequent": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                "most_frequent_count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                "top_10_values": {str(k): int(v) for k, v in top_values.items()}
            })
            
            # String-specific stats
            if col_data.dtype == 'object':
                str_data = col_data.dropna().astype(str)
                if len(str_data) > 0:
                    str_lengths = str_data.str.len()
                    result["string_stats"] = {
                        "min_length": int(str_lengths.min()),
                        "max_length": int(str_lengths.max()),
                        "mean_length": round(str_lengths.mean(), 2),
                        "empty_string_count": int((str_data == "").sum())
                    }
        
        session.record_operation(OperationType.ANALYZE, {
            "type": "column_statistics",
            "column": column
        })
        
        return {
            "success": True,
            "statistics": result
        }
        
    except Exception as e:
        logger.error(f"Error getting column statistics: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_correlation_matrix(
    session_id: str,
    method: str = "pearson",
    columns: Optional[List[str]] = None,
    min_correlation: Optional[float] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Calculate correlation matrix for numeric columns.
    
    Args:
        session_id: Session identifier
        method: Correlation method ('pearson', 'spearman', 'kendall')
        columns: Specific columns to include (None for all numeric)
        min_correlation: Filter to show only correlations above this threshold
        ctx: FastMCP context
        
    Returns:
        Dict with correlation matrix
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Select columns
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            numeric_df = df[columns].select_dtypes(include=[np.number])
        else:
            numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"success": False, "error": "No numeric columns found"}
        
        if len(numeric_df.columns) < 2:
            return {"success": False, "error": "Need at least 2 numeric columns for correlation"}
        
        # Calculate correlation
        if method not in ['pearson', 'spearman', 'kendall']:
            return {"success": False, "error": f"Invalid method: {method}"}
        
        corr_matrix = numeric_df.corr(method=method)
        
        # Convert to dict format
        correlations = {}
        for col1 in corr_matrix.columns:
            correlations[col1] = {}
            for col2 in corr_matrix.columns:
                value = corr_matrix.loc[col1, col2]
                if not pd.isna(value):
                    if min_correlation is None or abs(value) >= min_correlation or col1 == col2:
                        correlations[col1][col2] = round(float(value), 4)
        
        # Find highly correlated pairs
        high_correlations = []
        for i, col1 in enumerate(corr_matrix.columns):
            for col2 in corr_matrix.columns[i+1:]:
                corr_value = corr_matrix.loc[col1, col2]
                if not pd.isna(corr_value) and abs(corr_value) >= 0.7:
                    high_correlations.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": round(float(corr_value), 4)
                    })
        
        high_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        session.record_operation(OperationType.ANALYZE, {
            "type": "correlation",
            "method": method,
            "columns": list(corr_matrix.columns)
        })
        
        return {
            "success": True,
            "method": method,
            "correlation_matrix": correlations,
            "high_correlations": high_correlations,
            "columns_analyzed": list(corr_matrix.columns)
        }
        
    except Exception as e:
        logger.error(f"Error calculating correlation: {str(e)}")
        return {"success": False, "error": str(e)}


async def group_by_aggregate(
    session_id: str,
    group_by: List[str],
    aggregations: Dict[str, Union[str, List[str]]],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Group data and apply aggregation functions.
    
    Args:
        session_id: Session identifier
        group_by: Columns to group by
        aggregations: Dict mapping column names to aggregation functions
                     e.g., {"sales": ["sum", "mean"], "quantity": "sum"}
        ctx: FastMCP context
        
    Returns:
        Dict with grouped data
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Validate group by columns
        missing_cols = [col for col in group_by if col not in df.columns]
        if missing_cols:
            return {"success": False, "error": f"Group by columns not found: {missing_cols}"}
        
        # Validate aggregation columns
        agg_cols = list(aggregations.keys())
        missing_agg_cols = [col for col in agg_cols if col not in df.columns]
        if missing_agg_cols:
            return {"success": False, "error": f"Aggregation columns not found: {missing_agg_cols}"}
        
        # Prepare aggregation dict
        agg_dict = {}
        for col, funcs in aggregations.items():
            if isinstance(funcs, str):
                agg_dict[col] = [funcs]
            else:
                agg_dict[col] = funcs
        
        # Perform groupby
        grouped = df.groupby(group_by).agg(agg_dict)
        
        # Flatten column names
        grouped.columns = ['_'.join(col).strip() if col[1] else col[0] 
                          for col in grouped.columns.values]
        
        # Reset index to make group columns regular columns
        result_df = grouped.reset_index()
        
        # Convert to dict for response
        result = {
            "data": result_df.to_dict(orient='records'),
            "shape": {
                "rows": len(result_df),
                "columns": len(result_df.columns)
            },
            "columns": result_df.columns.tolist()
        }
        
        # Store grouped data in session
        session.df = result_df
        session.record_operation(OperationType.GROUP_BY, {
            "group_by": group_by,
            "aggregations": aggregations,
            "result_shape": result["shape"]
        })
        
        return {
            "success": True,
            "grouped_data": result,
            "group_by": group_by,
            "aggregations": aggregations
        }
        
    except Exception as e:
        logger.error(f"Error in group by aggregate: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_value_counts(
    session_id: str,
    column: str,
    normalize: bool = False,
    sort: bool = True,
    ascending: bool = False,
    top_n: Optional[int] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get value counts for a column.
    
    Args:
        session_id: Session identifier
        column: Column name to count values
        normalize: Return proportions instead of counts
        sort: Sort by frequency
        ascending: Sort order
        top_n: Return only top N values
        ctx: FastMCP context
        
    Returns:
        Dict with value counts
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found"}
        
        # Get value counts
        value_counts = df[column].value_counts(
            normalize=normalize,
            sort=sort,
            ascending=ascending,
            dropna=False
        )
        
        # Apply top_n if specified
        if top_n:
            value_counts = value_counts.head(top_n)
        
        # Convert to dict
        counts_dict = {}
        for value, count in value_counts.items():
            key = str(value) if not pd.isna(value) else "NaN"
            counts_dict[key] = float(count) if normalize else int(count)
        
        # Calculate additional statistics
        unique_count = df[column].nunique(dropna=False)
        null_count = df[column].isna().sum()
        
        session.record_operation(OperationType.ANALYZE, {
            "type": "value_counts",
            "column": column,
            "normalize": normalize,
            "top_n": top_n
        })
        
        return {
            "success": True,
            "column": column,
            "value_counts": counts_dict,
            "unique_values": int(unique_count),
            "null_count": int(null_count),
            "total_count": len(df),
            "normalized": normalize
        }
        
    except Exception as e:
        logger.error(f"Error getting value counts: {str(e)}")
        return {"success": False, "error": str(e)}


async def detect_outliers(
    session_id: str,
    columns: Optional[List[str]] = None,
    method: str = "iqr",
    threshold: float = 1.5,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Detect outliers in numeric columns.
    
    Args:
        session_id: Session identifier
        columns: Columns to check (None for all numeric)
        method: Detection method ('iqr', 'zscore', 'isolation_forest')
        threshold: Threshold for outlier detection (1.5 for IQR, 3 for z-score)
        ctx: FastMCP context
        
    Returns:
        Dict with outlier information
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        # Select numeric columns
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            numeric_df = df[columns].select_dtypes(include=[np.number])
        else:
            numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"success": False, "error": "No numeric columns found"}
        
        outliers = {}
        
        if method == "iqr":
            for col in numeric_df.columns:
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outlier_mask = (numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)
                outlier_indices = df.index[outlier_mask].tolist()
                
                outliers[col] = {
                    "method": "IQR",
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                    "outlier_count": len(outlier_indices),
                    "outlier_percentage": round(len(outlier_indices) / len(df) * 100, 2),
                    "outlier_indices": outlier_indices[:100],  # Limit to first 100
                    "q1": float(Q1),
                    "q3": float(Q3),
                    "iqr": float(IQR)
                }
                
        elif method == "zscore":
            for col in numeric_df.columns:
                z_scores = np.abs((numeric_df[col] - numeric_df[col].mean()) / numeric_df[col].std())
                outlier_mask = z_scores > threshold
                outlier_indices = df.index[outlier_mask].tolist()
                
                outliers[col] = {
                    "method": "Z-Score",
                    "threshold": threshold,
                    "outlier_count": len(outlier_indices),
                    "outlier_percentage": round(len(outlier_indices) / len(df) * 100, 2),
                    "outlier_indices": outlier_indices[:100],  # Limit to first 100
                    "mean": float(numeric_df[col].mean()),
                    "std": float(numeric_df[col].std())
                }
                
        else:
            return {"success": False, "error": f"Unknown method: {method}"}
        
        # Summary statistics
        total_outliers = sum(info["outlier_count"] for info in outliers.values())
        
        session.record_operation(OperationType.ANALYZE, {
            "type": "outlier_detection",
            "method": method,
            "threshold": threshold,
            "columns": list(outliers.keys())
        })
        
        return {
            "success": True,
            "method": method,
            "threshold": threshold,
            "outliers": outliers,
            "total_outliers": total_outliers,
            "columns_analyzed": list(outliers.keys())
        }
        
    except Exception as e:
        logger.error(f"Error detecting outliers: {str(e)}")
        return {"success": False, "error": str(e)}


async def profile_data(
    session_id: str,
    include_correlations: bool = True,
    include_outliers: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Generate comprehensive data profile.
    
    Args:
        session_id: Session identifier
        include_correlations: Include correlation analysis
        include_outliers: Include outlier detection
        ctx: FastMCP context
        
    Returns:
        Dict with complete data profile
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        profile = {
            "overview": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "duplicate_rows": df.duplicated().sum(),
                "duplicate_percentage": round(df.duplicated().sum() / len(df) * 100, 2)
            },
            "columns": {}
        }
        
        # Analyze each column
        for col in df.columns:
            col_data = df[col]
            col_profile = {
                "dtype": str(col_data.dtype),
                "null_count": int(col_data.isna().sum()),
                "null_percentage": round(col_data.isna().sum() / len(df) * 100, 2),
                "unique_count": int(col_data.nunique()),
                "unique_percentage": round(col_data.nunique() / len(df) * 100, 2)
            }
            
            # Numeric column analysis
            if pd.api.types.is_numeric_dtype(col_data):
                col_profile["type"] = "numeric"
                col_profile["statistics"] = {
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "25%": float(col_data.quantile(0.25)),
                    "50%": float(col_data.quantile(0.50)),
                    "75%": float(col_data.quantile(0.75)),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurt())
                }
                col_profile["zeros"] = int((col_data == 0).sum())
                col_profile["negative_count"] = int((col_data < 0).sum())
                
            # Datetime column analysis
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                col_profile["type"] = "datetime"
                non_null = col_data.dropna()
                if len(non_null) > 0:
                    col_profile["date_range"] = {
                        "min": str(non_null.min()),
                        "max": str(non_null.max()),
                        "range_days": (non_null.max() - non_null.min()).days
                    }
                    
            # Categorical/text column analysis
            else:
                col_profile["type"] = "categorical"
                value_counts = col_data.value_counts()
                col_profile["most_frequent"] = {
                    "value": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "count": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0
                }
                
                # String-specific analysis
                if col_data.dtype == 'object':
                    str_lengths = col_data.dropna().astype(str).str.len()
                    if len(str_lengths) > 0:
                        col_profile["string_stats"] = {
                            "min_length": int(str_lengths.min()),
                            "max_length": int(str_lengths.max()),
                            "mean_length": round(str_lengths.mean(), 2)
                        }
            
            profile["columns"][col] = col_profile
        
        # Add correlations if requested
        if include_correlations:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                corr_result = await get_correlation_matrix(session_id, ctx=ctx)
                if corr_result["success"]:
                    profile["correlations"] = corr_result["high_correlations"]
        
        # Add outlier detection if requested
        if include_outliers:
            outlier_result = await detect_outliers(session_id, ctx=ctx)
            if outlier_result["success"]:
                profile["outliers"] = {
                    col: {
                        "count": info["outlier_count"],
                        "percentage": info["outlier_percentage"]
                    }
                    for col, info in outlier_result["outliers"].items()
                }
        
        # Data quality score
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isna().sum().sum()
        quality_score = round((1 - missing_cells / total_cells) * 100, 2)
        profile["data_quality_score"] = quality_score
        
        session.record_operation(OperationType.PROFILE, {
            "include_correlations": include_correlations,
            "include_outliers": include_outliers
        })
        
        return {
            "success": True,
            "profile": profile
        }
        
    except Exception as e:
        logger.error(f"Error profiling data: {str(e)}")
        return {"success": False, "error": str(e)}