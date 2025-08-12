"""Validation utilities for CSV Editor."""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from urllib.parse import urlparse


def validate_file_path(file_path: str, must_exist: bool = True) -> tuple[bool, str]:
    """Validate a file path for security and existence."""
    try:
        # Convert to Path object
        path = Path(file_path).resolve()
        
        # Security: Check for path traversal attempts
        if ".." in file_path or file_path.startswith("~"):
            return False, "Path traversal not allowed"
            
        # Check file existence if required
        if must_exist and not path.exists():
            return False, f"File not found: {file_path}"
            
        # Check if it's a file (not directory)
        if must_exist and not path.is_file():
            return False, f"Not a file: {file_path}"
            
        # Check file extension
        valid_extensions = ['.csv', '.tsv', '.txt', '.dat']
        if path.suffix.lower() not in valid_extensions:
            return False, f"Invalid file extension. Supported: {valid_extensions}"
            
        # Check file size (max 1GB)
        if must_exist:
            max_size = 1024 * 1024 * 1024  # 1GB
            if path.stat().st_size > max_size:
                return False, f"File too large. Maximum size: 1GB"
                
        return True, str(path)
        
    except Exception as e:
        return False, f"Error validating path: {str(e)}"


def validate_url(url: str) -> tuple[bool, str]:
    """Validate a URL for CSV download."""
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP/HTTPS URLs are supported"
            
        # Check if URL is valid
        if not parsed.netloc:
            return False, "Invalid URL format"
            
        return True, url
        
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def validate_column_name(column_name: str) -> tuple[bool, str]:
    """Validate a column name."""
    if not column_name or not isinstance(column_name, str):
        return False, "Column name must be a non-empty string"
        
    # Check for invalid characters
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name):
        return True, column_name
    else:
        return False, "Column name must start with letter/underscore and contain only letters, numbers, underscores"


def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate a DataFrame for common issues."""
    issues = {
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    # Check if empty
    if df.empty:
        issues["errors"].append("DataFrame is empty")
        return issues
        
    # Check shape
    issues["info"]["shape"] = df.shape
    issues["info"]["memory_usage_mb"] = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Check for duplicate columns
    if df.columns.duplicated().any():
        dupes = df.columns[df.columns.duplicated()].tolist()
        issues["errors"].append(f"Duplicate column names: {dupes}")
        
    # Check for completely null columns
    null_cols = df.columns[df.isnull().all()].tolist()
    if null_cols:
        issues["warnings"].append(f"Completely null columns: {null_cols}")
        
    # Check for mixed types in columns
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to infer if it's mixed types
            unique_types = df[col].dropna().apply(type).unique()
            if len(unique_types) > 1:
                issues["warnings"].append(f"Column '{col}' has mixed types: {[t.__name__ for t in unique_types]}")
                
    # Check for high cardinality in string columns
    for col in df.select_dtypes(include=['object']).columns:
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.9:
            issues["info"][f"{col}_high_cardinality"] = True
            
    # Check for potential datetime columns
    for col in df.select_dtypes(include=['object']).columns:
        sample = df[col].dropna().head(100)
        if sample.empty:
            continue
        try:
            pd.to_datetime(sample, errors='raise')
            issues["info"][f"{col}_potential_datetime"] = True
        except:
            pass
            
    return issues


def validate_expression(expression: str, allowed_vars: List[str]) -> tuple[bool, str]:
    """Validate a calculation expression for safety."""
    # Remove whitespace
    expr = expression.replace(" ", "")
    
    # Check for dangerous operations
    dangerous_patterns = [
        '__', 'import', 'exec', 'eval', 'compile', 'open',
        'file', 'input', 'raw_input', 'globals', 'locals'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in expr.lower():
            return False, f"Dangerous operation '{pattern}' not allowed"
            
    # Check if only allowed variables and safe operations are used
    # This is a simplified check - in production use ast module for proper parsing
    safe_chars = set('0123456789+-*/().,<>=! ')
    safe_functions = {'abs', 'min', 'max', 'sum', 'len', 'round', 'int', 'float', 'str'}
    
    # Extract potential variable/function names
    tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*', expr)
    
    for token in tokens:
        if token not in allowed_vars and token not in safe_functions:
            return False, f"Unknown variable or function: {token}"
            
    return True, expression


def validate_sql_query(query: str) -> tuple[bool, str]:
    """Validate SQL query for safety (basic check)."""
    query_lower = query.lower()
    
    # Only allow SELECT queries
    if not query_lower.strip().startswith('select'):
        return False, "Only SELECT queries are allowed"
        
    # Check for dangerous keywords
    dangerous = ['drop', 'delete', 'insert', 'update', 'alter', 'create', 'exec', 'execute']
    for keyword in dangerous:
        if keyword in query_lower:
            return False, f"Dangerous operation '{keyword}' not allowed"
            
    return True, query


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file operations."""
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove/replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
        
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext