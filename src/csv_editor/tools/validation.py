"""Data validation tools for CSV data quality checks."""

from typing import Dict, Any, Optional, List, Union
from fastmcp import Context
import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime

from ..models.csv_session import get_session_manager
from ..models.data_models import OperationType

logger = logging.getLogger(__name__)


async def validate_schema(
    session_id: str,
    schema: Dict[str, Dict[str, Any]],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Validate data against a schema definition.
    
    Args:
        session_id: Session identifier
        schema: Schema definition with column rules
                Example: {
                    "column_name": {
                        "type": "int",  # int, float, str, bool, datetime
                        "nullable": False,
                        "min": 0,
                        "max": 100,
                        "pattern": "^[A-Z]+$",
                        "values": ["A", "B", "C"],  # allowed values
                        "unique": True
                    }
                }
        ctx: FastMCP context
        
    Returns:
        Dict with validation results
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        validation_errors = {}
        validation_summary = {
            "total_columns": len(schema),
            "valid_columns": 0,
            "invalid_columns": 0,
            "missing_columns": [],
            "extra_columns": []
        }
        
        # Check for missing and extra columns
        schema_columns = set(schema.keys())
        df_columns = set(df.columns)
        
        validation_summary["missing_columns"] = list(schema_columns - df_columns)
        validation_summary["extra_columns"] = list(df_columns - schema_columns)
        
        # Validate each column in schema
        for col_name, rules in schema.items():
            if col_name not in df.columns:
                validation_errors[col_name] = [{
                    "error": "column_missing",
                    "message": f"Column '{col_name}' not found in data"
                }]
                validation_summary["invalid_columns"] += 1
                continue
            
            col_errors = []
            col_data = df[col_name]
            
            # Type validation
            expected_type = rules.get("type")
            if expected_type:
                type_valid = False
                if expected_type == "int":
                    type_valid = pd.api.types.is_integer_dtype(col_data)
                elif expected_type == "float":
                    type_valid = pd.api.types.is_float_dtype(col_data)
                elif expected_type == "str":
                    type_valid = pd.api.types.is_string_dtype(col_data) or col_data.dtype == object
                elif expected_type == "bool":
                    type_valid = pd.api.types.is_bool_dtype(col_data)
                elif expected_type == "datetime":
                    type_valid = pd.api.types.is_datetime64_any_dtype(col_data)
                
                if not type_valid:
                    col_errors.append({
                        "error": "type_mismatch",
                        "message": f"Expected type '{expected_type}', got '{col_data.dtype}'",
                        "actual_type": str(col_data.dtype)
                    })
            
            # Nullable validation
            if not rules.get("nullable", True):
                null_count = col_data.isna().sum()
                if null_count > 0:
                    col_errors.append({
                        "error": "null_values",
                        "message": f"Column contains {null_count} null values",
                        "null_count": int(null_count),
                        "null_indices": df[col_data.isna()].index.tolist()[:100]
                    })
            
            # Min/Max validation for numeric columns
            if pd.api.types.is_numeric_dtype(col_data):
                if "min" in rules:
                    min_val = rules["min"]
                    violations = col_data[col_data < min_val]
                    if len(violations) > 0:
                        col_errors.append({
                            "error": "min_violation",
                            "message": f"{len(violations)} values below minimum {min_val}",
                            "violation_count": len(violations),
                            "min_found": float(violations.min())
                        })
                
                if "max" in rules:
                    max_val = rules["max"]
                    violations = col_data[col_data > max_val]
                    if len(violations) > 0:
                        col_errors.append({
                            "error": "max_violation",
                            "message": f"{len(violations)} values above maximum {max_val}",
                            "violation_count": len(violations),
                            "max_found": float(violations.max())
                        })
            
            # Pattern validation for string columns
            if "pattern" in rules and (col_data.dtype == object or pd.api.types.is_string_dtype(col_data)):
                pattern = rules["pattern"]
                try:
                    non_null = col_data.dropna()
                    if len(non_null) > 0:
                        matches = non_null.astype(str).str.match(pattern)
                        violations = non_null[~matches]
                        if len(violations) > 0:
                            col_errors.append({
                                "error": "pattern_violation",
                                "message": f"{len(violations)} values don't match pattern '{pattern}'",
                                "violation_count": len(violations),
                                "sample_violations": violations.head(10).tolist()
                            })
                except Exception as e:
                    col_errors.append({
                        "error": "pattern_error",
                        "message": f"Invalid regex pattern: {str(e)}"
                    })
            
            # Allowed values validation
            if "values" in rules:
                allowed = set(rules["values"])
                actual = set(col_data.dropna().unique())
                invalid = actual - allowed
                if invalid:
                    col_errors.append({
                        "error": "invalid_values",
                        "message": f"Found {len(invalid)} invalid values",
                        "invalid_values": list(invalid)[:50]
                    })
            
            # Uniqueness validation
            if rules.get("unique", False):
                duplicates = col_data.duplicated()
                if duplicates.any():
                    col_errors.append({
                        "error": "duplicate_values",
                        "message": f"Column contains {duplicates.sum()} duplicate values",
                        "duplicate_count": int(duplicates.sum())
                    })
            
            # Length validation for strings
            if col_data.dtype == object or pd.api.types.is_string_dtype(col_data):
                if "min_length" in rules:
                    min_len = rules["min_length"]
                    str_data = col_data.dropna().astype(str)
                    short = str_data[str_data.str.len() < min_len]
                    if len(short) > 0:
                        col_errors.append({
                            "error": "min_length_violation",
                            "message": f"{len(short)} values shorter than {min_len} characters",
                            "violation_count": len(short)
                        })
                
                if "max_length" in rules:
                    max_len = rules["max_length"]
                    str_data = col_data.dropna().astype(str)
                    long = str_data[str_data.str.len() > max_len]
                    if len(long) > 0:
                        col_errors.append({
                            "error": "max_length_violation",
                            "message": f"{len(long)} values longer than {max_len} characters",
                            "violation_count": len(long)
                        })
            
            if col_errors:
                validation_errors[col_name] = col_errors
                validation_summary["invalid_columns"] += 1
            else:
                validation_summary["valid_columns"] += 1
        
        is_valid = len(validation_errors) == 0 and len(validation_summary["missing_columns"]) == 0
        
        session.record_operation(OperationType.VALIDATE, {
            "type": "schema_validation",
            "is_valid": is_valid,
            "errors_count": len(validation_errors)
        })
        
        return {
            "success": True,
            "is_valid": is_valid,
            "summary": validation_summary,
            "validation_errors": validation_errors
        }
        
    except Exception as e:
        logger.error(f"Error validating schema: {str(e)}")
        return {"success": False, "error": str(e)}


async def check_data_quality(
    session_id: str,
    rules: Optional[List[Dict[str, Any]]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Check data quality based on predefined or custom rules.
    
    Args:
        session_id: Session identifier
        rules: Custom quality rules to check. If None, uses default rules.
               Example: [
                   {"type": "completeness", "threshold": 0.95},
                   {"type": "uniqueness", "column": "id"},
                   {"type": "consistency", "columns": ["start_date", "end_date"]}
               ]
        ctx: FastMCP context
        
    Returns:
        Dict with quality check results
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        quality_results = {
            "overall_score": 100.0,
            "checks": [],
            "issues": [],
            "recommendations": []
        }
        
        # Default rules if none provided
        if not rules:
            rules = [
                {"type": "completeness", "threshold": 0.95},
                {"type": "duplicates", "threshold": 0.01},
                {"type": "data_types"},
                {"type": "outliers", "threshold": 0.05},
                {"type": "consistency"}
            ]
        
        total_score = 0
        score_count = 0
        
        for rule in rules:
            rule_type = rule.get("type")
            
            if rule_type == "completeness":
                # Check data completeness
                threshold = rule.get("threshold", 0.95)
                columns = rule.get("columns", df.columns.tolist())
                
                for col in columns:
                    if col in df.columns:
                        completeness = 1 - (df[col].isna().sum() / len(df))
                        passed = completeness >= threshold
                        score = completeness * 100
                        
                        quality_results["checks"].append({
                            "type": "completeness",
                            "column": col,
                            "completeness": round(completeness, 4),
                            "threshold": threshold,
                            "passed": passed,
                            "score": round(score, 2)
                        })
                        
                        if not passed:
                            quality_results["issues"].append({
                                "type": "incomplete_data",
                                "column": col,
                                "message": f"Column '{col}' is only {round(completeness*100, 2)}% complete",
                                "severity": "high" if completeness < 0.5 else "medium"
                            })
                        
                        total_score += score
                        score_count += 1
            
            elif rule_type == "duplicates":
                # Check for duplicate rows
                threshold = rule.get("threshold", 0.01)
                subset = rule.get("columns")
                
                duplicates = df.duplicated(subset=subset)
                duplicate_ratio = duplicates.sum() / len(df)
                passed = duplicate_ratio <= threshold
                score = (1 - duplicate_ratio) * 100
                
                quality_results["checks"].append({
                    "type": "duplicates",
                    "duplicate_rows": int(duplicates.sum()),
                    "duplicate_ratio": round(duplicate_ratio, 4),
                    "threshold": threshold,
                    "passed": passed,
                    "score": round(score, 2)
                })
                
                if not passed:
                    quality_results["issues"].append({
                        "type": "duplicate_rows",
                        "message": f"Found {duplicates.sum()} duplicate rows ({round(duplicate_ratio*100, 2)}%)",
                        "severity": "high" if duplicate_ratio > 0.1 else "medium"
                    })
                    quality_results["recommendations"].append(
                        "Consider removing duplicate rows using the remove_duplicates tool"
                    )
                
                total_score += score
                score_count += 1
            
            elif rule_type == "uniqueness":
                # Check column uniqueness
                column = rule.get("column")
                if column and column in df.columns:
                    unique_ratio = df[column].nunique() / len(df)
                    expected_unique = rule.get("expected_unique", True)
                    
                    if expected_unique:
                        passed = unique_ratio >= 0.99
                        score = unique_ratio * 100
                    else:
                        passed = True
                        score = 100
                    
                    quality_results["checks"].append({
                        "type": "uniqueness",
                        "column": column,
                        "unique_values": int(df[column].nunique()),
                        "unique_ratio": round(unique_ratio, 4),
                        "passed": passed,
                        "score": round(score, 2)
                    })
                    
                    if not passed and expected_unique:
                        quality_results["issues"].append({
                            "type": "non_unique_values",
                            "column": column,
                            "message": f"Column '{column}' expected to be unique but has duplicates",
                            "severity": "high"
                        })
                    
                    total_score += score
                    score_count += 1
            
            elif rule_type == "data_types":
                # Check data type consistency
                for col in df.columns:
                    col_data = df[col].dropna()
                    if len(col_data) > 0:
                        # Check for mixed types
                        types = col_data.apply(type).unique()
                        mixed_types = len(types) > 1
                        
                        # Check for numeric strings
                        if col_data.dtype == object:
                            numeric_strings = col_data.astype(str).str.match(r'^-?\d+\.?\d*$').sum()
                            numeric_ratio = numeric_strings / len(col_data)
                        else:
                            numeric_ratio = 0
                        
                        score = 100 if not mixed_types else 50
                        
                        quality_results["checks"].append({
                            "type": "data_type_consistency",
                            "column": col,
                            "dtype": str(df[col].dtype),
                            "mixed_types": mixed_types,
                            "numeric_strings": numeric_ratio > 0.9,
                            "score": score
                        })
                        
                        if numeric_ratio > 0.9:
                            quality_results["recommendations"].append(
                                f"Column '{col}' appears to contain numeric data stored as strings. "
                                f"Consider converting to numeric type using change_column_type tool"
                            )
                        
                        total_score += score
                        score_count += 1
            
            elif rule_type == "outliers":
                # Check for outliers in numeric columns
                threshold = rule.get("threshold", 0.05)
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                    outlier_ratio = outliers / len(df)
                    passed = outlier_ratio <= threshold
                    score = (1 - min(outlier_ratio, 1)) * 100
                    
                    quality_results["checks"].append({
                        "type": "outliers",
                        "column": col,
                        "outlier_count": int(outliers),
                        "outlier_ratio": round(outlier_ratio, 4),
                        "threshold": threshold,
                        "passed": passed,
                        "score": round(score, 2)
                    })
                    
                    if not passed:
                        quality_results["issues"].append({
                            "type": "outliers",
                            "column": col,
                            "message": f"Column '{col}' has {outliers} outliers ({round(outlier_ratio*100, 2)}%)",
                            "severity": "medium"
                        })
                    
                    total_score += score
                    score_count += 1
            
            elif rule_type == "consistency":
                # Check data consistency
                columns = rule.get("columns", [])
                
                # Date consistency check
                date_cols = df.select_dtypes(include=['datetime64']).columns
                if len(date_cols) >= 2 and not columns:
                    columns = date_cols.tolist()
                
                if len(columns) >= 2:
                    col1, col2 = columns[0], columns[1]
                    if col1 in df.columns and col2 in df.columns:
                        # Check if col1 should be before col2 (e.g., start_date < end_date)
                        if pd.api.types.is_datetime64_any_dtype(df[col1]) and pd.api.types.is_datetime64_any_dtype(df[col2]):
                            inconsistent = (df[col1] > df[col2]).sum()
                            consistency_ratio = 1 - (inconsistent / len(df))
                            passed = consistency_ratio >= 0.99
                            score = consistency_ratio * 100
                            
                            quality_results["checks"].append({
                                "type": "consistency",
                                "columns": [col1, col2],
                                "consistent_rows": len(df) - inconsistent,
                                "inconsistent_rows": int(inconsistent),
                                "consistency_ratio": round(consistency_ratio, 4),
                                "passed": passed,
                                "score": round(score, 2)
                            })
                            
                            if not passed:
                                quality_results["issues"].append({
                                    "type": "data_inconsistency",
                                    "columns": [col1, col2],
                                    "message": f"Found {inconsistent} rows where {col1} > {col2}",
                                    "severity": "high"
                                })
                            
                            total_score += score
                            score_count += 1
        
        # Calculate overall score
        if score_count > 0:
            quality_results["overall_score"] = round(total_score / score_count, 2)
        
        # Determine quality level
        overall_score = quality_results["overall_score"]
        if overall_score >= 95:
            quality_results["quality_level"] = "Excellent"
        elif overall_score >= 85:
            quality_results["quality_level"] = "Good"
        elif overall_score >= 70:
            quality_results["quality_level"] = "Fair"
        else:
            quality_results["quality_level"] = "Poor"
        
        # Add general recommendations
        if not quality_results["recommendations"]:
            if overall_score < 85:
                quality_results["recommendations"].append(
                    "Consider running profile_data to get a comprehensive overview of data issues"
                )
        
        session.record_operation(OperationType.QUALITY_CHECK, {
            "rules_count": len(rules),
            "overall_score": overall_score,
            "issues_count": len(quality_results["issues"])
        })
        
        return {
            "success": True,
            "quality_results": quality_results
        }
        
    except Exception as e:
        logger.error(f"Error checking data quality: {str(e)}")
        return {"success": False, "error": str(e)}


async def find_anomalies(
    session_id: str,
    columns: Optional[List[str]] = None,
    sensitivity: float = 0.95,
    methods: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Find anomalies in the data using multiple detection methods.
    
    Args:
        session_id: Session identifier
        columns: Columns to check (None for all)
        sensitivity: Detection sensitivity (0.0 to 1.0, higher = more sensitive)
        methods: Detection methods to use (default: ["statistical", "pattern"])
        ctx: FastMCP context
        
    Returns:
        Dict with anomaly detection results
    """
    try:
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session or session.df is None:
            return {"success": False, "error": "Invalid session or no data loaded"}
        
        df = session.df
        
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return {"success": False, "error": f"Columns not found: {missing_cols}"}
            target_cols = columns
        else:
            target_cols = df.columns.tolist()
        
        if not methods:
            methods = ["statistical", "pattern", "missing"]
        
        anomalies = {
            "summary": {
                "total_anomalies": 0,
                "affected_rows": set(),
                "affected_columns": []
            },
            "by_column": {},
            "by_method": {}
        }
        
        # Statistical anomalies (outliers)
        if "statistical" in methods:
            numeric_cols = df[target_cols].select_dtypes(include=[np.number]).columns
            statistical_anomalies = {}
            
            for col in numeric_cols:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    # Z-score method
                    z_scores = np.abs((col_data - col_data.mean()) / col_data.std())
                    z_threshold = 3 * (1 - sensitivity + 0.5)  # Adjust threshold based on sensitivity
                    z_anomalies = df.index[z_scores > z_threshold].tolist()
                    
                    # IQR method
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    iqr_factor = 1.5 * (2 - sensitivity)  # Adjust factor based on sensitivity
                    lower = Q1 - iqr_factor * IQR
                    upper = Q3 + iqr_factor * IQR
                    iqr_anomalies = df.index[(df[col] < lower) | (df[col] > upper)].tolist()
                    
                    # Combine both methods
                    combined_anomalies = list(set(z_anomalies) | set(iqr_anomalies))
                    
                    if combined_anomalies:
                        statistical_anomalies[col] = {
                            "anomaly_count": len(combined_anomalies),
                            "anomaly_indices": combined_anomalies[:100],
                            "anomaly_values": df.loc[combined_anomalies[:10], col].tolist(),
                            "mean": float(col_data.mean()),
                            "std": float(col_data.std()),
                            "lower_bound": float(lower),
                            "upper_bound": float(upper)
                        }
                        
                        anomalies["summary"]["total_anomalies"] += len(combined_anomalies)
                        anomalies["summary"]["affected_rows"].update(combined_anomalies)
                        anomalies["summary"]["affected_columns"].append(col)
            
            if statistical_anomalies:
                anomalies["by_method"]["statistical"] = statistical_anomalies
        
        # Pattern anomalies
        if "pattern" in methods:
            pattern_anomalies = {}
            
            for col in target_cols:
                if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
                    col_data = df[col].dropna()
                    if len(col_data) > 0:
                        # Detect unusual patterns
                        value_counts = col_data.value_counts()
                        total_count = len(col_data)
                        
                        # Find rare values (appearing less than threshold)
                        threshold = (1 - sensitivity) * 0.01  # Adjust threshold
                        rare_values = value_counts[value_counts / total_count < threshold]
                        
                        if len(rare_values) > 0:
                            rare_indices = df[df[col].isin(rare_values.index)].index.tolist()
                            
                            # Check for format anomalies (e.g., different case, special characters)
                            common_pattern = None
                            if len(value_counts) > 10:
                                # Detect common pattern from frequent values
                                top_values = value_counts.head(10).index
                                
                                # Check if most values are uppercase/lowercase
                                upper_count = sum(1 for v in top_values if str(v).isupper())
                                lower_count = sum(1 for v in top_values if str(v).islower())
                                
                                if upper_count > 7:
                                    common_pattern = "uppercase"
                                elif lower_count > 7:
                                    common_pattern = "lowercase"
                            
                            format_anomalies = []
                            if common_pattern:
                                for idx, val in col_data.items():
                                    if common_pattern == "uppercase" and not str(val).isupper():
                                        format_anomalies.append(idx)
                                    elif common_pattern == "lowercase" and not str(val).islower():
                                        format_anomalies.append(idx)
                            
                            all_pattern_anomalies = list(set(rare_indices + format_anomalies))
                            
                            if all_pattern_anomalies:
                                pattern_anomalies[col] = {
                                    "anomaly_count": len(all_pattern_anomalies),
                                    "rare_values": rare_values.head(10).to_dict(),
                                    "anomaly_indices": all_pattern_anomalies[:100],
                                    "common_pattern": common_pattern
                                }
                                
                                anomalies["summary"]["total_anomalies"] += len(all_pattern_anomalies)
                                anomalies["summary"]["affected_rows"].update(all_pattern_anomalies)
                                if col not in anomalies["summary"]["affected_columns"]:
                                    anomalies["summary"]["affected_columns"].append(col)
            
            if pattern_anomalies:
                anomalies["by_method"]["pattern"] = pattern_anomalies
        
        # Missing value anomalies
        if "missing" in methods:
            missing_anomalies = {}
            
            for col in target_cols:
                null_mask = df[col].isna()
                null_count = null_mask.sum()
                
                if null_count > 0:
                    null_ratio = null_count / len(df)
                    
                    # Check for suspicious missing patterns
                    if 0 < null_ratio < 0.5:  # Partially missing
                        # Check if missing values are clustered
                        null_indices = df.index[null_mask].tolist()
                        
                        # Check for sequential missing values
                        sequential_missing = []
                        if len(null_indices) > 1:
                            for i in range(len(null_indices) - 1):
                                if null_indices[i+1] - null_indices[i] == 1:
                                    if not sequential_missing or null_indices[i] - sequential_missing[-1][-1] == 1:
                                        if sequential_missing:
                                            sequential_missing[-1].append(null_indices[i+1])
                                        else:
                                            sequential_missing.append([null_indices[i], null_indices[i+1]])
                        
                        # Flag as anomaly if there are suspicious patterns
                        is_anomaly = len(sequential_missing) > 0 and len(sequential_missing) > len(null_indices) * 0.3
                        
                        if is_anomaly or (null_ratio > 0.1 and null_ratio < 0.3):
                            missing_anomalies[col] = {
                                "missing_count": int(null_count),
                                "missing_ratio": round(null_ratio, 4),
                                "missing_indices": null_indices[:100],
                                "sequential_clusters": len(sequential_missing),
                                "pattern": "clustered" if sequential_missing else "random"
                            }
                            
                            anomalies["summary"]["affected_columns"].append(col)
            
            if missing_anomalies:
                anomalies["by_method"]["missing"] = missing_anomalies
        
        # Organize anomalies by column
        for method_name, method_anomalies in anomalies["by_method"].items():
            for col, col_anomalies in method_anomalies.items():
                if col not in anomalies["by_column"]:
                    anomalies["by_column"][col] = {}
                anomalies["by_column"][col][method_name] = col_anomalies
        
        # Convert set to list for JSON serialization
        anomalies["summary"]["affected_rows"] = list(anomalies["summary"]["affected_rows"])[:1000]
        anomalies["summary"]["affected_columns"] = list(set(anomalies["summary"]["affected_columns"]))
        
        # Calculate anomaly score
        total_cells = len(df) * len(target_cols)
        anomaly_cells = len(anomalies["summary"]["affected_rows"]) * len(anomalies["summary"]["affected_columns"])
        anomaly_score = min(anomaly_cells / total_cells, 1.0) * 100
        
        anomalies["summary"]["anomaly_score"] = round(anomaly_score, 2)
        anomalies["summary"]["severity"] = (
            "high" if anomaly_score > 10
            else "medium" if anomaly_score > 5
            else "low"
        )
        
        session.record_operation(OperationType.ANOMALY_DETECTION, {
            "methods": methods,
            "sensitivity": sensitivity,
            "anomalies_found": anomalies["summary"]["total_anomalies"]
        })
        
        return {
            "success": True,
            "anomalies": anomalies,
            "columns_analyzed": target_cols,
            "methods_used": methods,
            "sensitivity": sensitivity
        }
        
    except Exception as e:
        logger.error(f"Error finding anomalies: {str(e)}")
        return {"success": False, "error": str(e)}