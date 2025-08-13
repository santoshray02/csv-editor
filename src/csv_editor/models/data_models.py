"""Data models for CSV Editor MCP Server."""

from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import pandas as pd


class DataType(str, Enum):
    """Supported data types for columns."""
    
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    MIXED = "mixed"


class OperationType(str, Enum):
    """Types of operations that can be performed."""
    
    LOAD = "load"
    FILTER = "filter"
    SORT = "sort"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"
    EXPORT = "export"
    ANALYZE = "analyze"
    UPDATE_COLUMN = "update_column"
    ADD_COLUMN = "add_column"
    REMOVE_COLUMN = "remove_column"
    RENAME = "rename"
    SELECT = "select"
    CHANGE_TYPE = "change_type"
    FILL_MISSING = "fill_missing"
    REMOVE_DUPLICATES = "remove_duplicates"


class ComparisonOperator(str, Enum):
    """Comparison operators for filtering."""
    
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN_OR_EQUALS = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class AggregateFunction(str, Enum):
    """Aggregate functions for data analysis."""
    
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    STD = "std"
    VAR = "var"
    FIRST = "first"
    LAST = "last"


class ExportFormat(str, Enum):
    """Supported export formats."""
    
    CSV = "csv"
    TSV = "tsv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"
    HTML = "html"
    MARKDOWN = "markdown"


class FilterCondition(BaseModel):
    """A single filter condition."""
    
    column: str = Field(..., description="Column name to filter on")
    operator: ComparisonOperator = Field(..., description="Comparison operator")
    value: Any = Field(None, description="Value to compare against")
    
    @field_validator("value", mode='before')
    def validate_value(cls, v, info):
        """Validate value based on operator."""
        operator = info.data.get("operator") if hasattr(info, 'data') else None
        if operator in [ComparisonOperator.IS_NULL, ComparisonOperator.IS_NOT_NULL]:
            return None
        if operator in [ComparisonOperator.IN, ComparisonOperator.NOT_IN]:
            if not isinstance(v, list):
                return [v]
        return v


class SortSpec(BaseModel):
    """Specification for sorting data."""
    
    column: str = Field(..., description="Column to sort by")
    ascending: bool = Field(True, description="Sort in ascending order")


class ColumnSchema(BaseModel):
    """Schema definition for a column."""
    
    name: str = Field(..., description="Column name")
    dtype: DataType = Field(..., description="Data type")
    nullable: bool = Field(True, description="Whether column can contain null values")
    unique: bool = Field(False, description="Whether values must be unique")
    min_value: Optional[Union[float, int, str]] = Field(None, description="Minimum value")
    max_value: Optional[Union[float, int, str]] = Field(None, description="Maximum value")
    allowed_values: Optional[List[Any]] = Field(None, description="List of allowed values")
    pattern: Optional[str] = Field(None, description="Regex pattern for validation")


class DataSchema(BaseModel):
    """Complete schema for a dataset."""
    
    columns: List[ColumnSchema] = Field(..., description="Column definitions")
    row_count: Optional[int] = Field(None, description="Expected number of rows")
    primary_key: Optional[List[str]] = Field(None, description="Primary key columns")
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate a DataFrame against this schema."""
        errors = []
        warnings = []
        
        # Check columns
        expected_cols = {col.name for col in self.columns}
        actual_cols = set(df.columns)
        
        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols
        
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        if extra_cols:
            warnings.append(f"Extra columns: {extra_cols}")
        
        # Validate each column
        for col_schema in self.columns:
            if col_schema.name not in df.columns:
                continue
                
            col_data = df[col_schema.name]
            
            # Check nullability
            if not col_schema.nullable and col_data.isnull().any():
                errors.append(f"Column {col_schema.name} contains null values")
            
            # Check uniqueness
            if col_schema.unique and col_data.duplicated().any():
                errors.append(f"Column {col_schema.name} contains duplicate values")
            
            # Check allowed values
            if col_schema.allowed_values:
                invalid = ~col_data.isin(col_schema.allowed_values)
                if invalid.any():
                    errors.append(f"Column {col_schema.name} contains invalid values")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class DataQualityRule(BaseModel):
    """A data quality rule to check."""
    
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    column: Optional[str] = Field(None, description="Column to check (if applicable)")
    rule_type: Literal["completeness", "uniqueness", "validity", "consistency", "accuracy"] = Field(
        ..., description="Type of quality check"
    )
    expression: Optional[str] = Field(None, description="Expression to evaluate")
    threshold: Optional[float] = Field(None, description="Threshold for pass/fail")


class OperationResult(BaseModel):
    """Result of a data operation."""
    
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Result message")
    session_id: Optional[str] = Field(None, description="Session ID")
    rows_affected: Optional[int] = Field(None, description="Number of rows affected")
    columns_affected: Optional[List[str]] = Field(None, description="Columns affected")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional result data")
    error: Optional[str] = Field(None, description="Error message if failed")
    warnings: Optional[List[str]] = Field(None, description="Warning messages")


class SessionInfo(BaseModel):
    """Information about a data session."""
    
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation time")
    last_accessed: datetime = Field(..., description="Last access time")
    row_count: int = Field(..., description="Number of rows in dataset")
    column_count: int = Field(..., description="Number of columns")
    columns: List[str] = Field(..., description="Column names")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    operations_count: int = Field(0, description="Number of operations performed")
    file_path: Optional[str] = Field(None, description="Source file path")


class DataStatistics(BaseModel):
    """Statistical summary of data."""
    
    column: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type")
    count: int = Field(..., description="Non-null count")
    null_count: int = Field(..., description="Null count")
    unique_count: int = Field(..., description="Unique value count")
    mean: Optional[float] = Field(None, description="Mean (numeric only)")
    std: Optional[float] = Field(None, description="Standard deviation (numeric only)")
    min: Optional[Any] = Field(None, description="Minimum value")
    max: Optional[Any] = Field(None, description="Maximum value")
    q25: Optional[float] = Field(None, description="25th percentile (numeric only)")
    q50: Optional[float] = Field(None, description="50th percentile (numeric only)")
    q75: Optional[float] = Field(None, description="75th percentile (numeric only)")
    top_values: Optional[Dict[str, int]] = Field(None, description="Top 10 most frequent values")