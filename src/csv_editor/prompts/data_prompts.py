"""Prompt templates - placeholder implementation."""

from typing import List

def analyze_csv_prompt(session_id: str, analysis_type: str) -> str:
    return f"Analyze CSV data in session {session_id} for {analysis_type}"

def suggest_transformations_prompt(session_id: str, goal: str) -> str:
    return f"Suggest transformations for session {session_id} to achieve: {goal}"

def data_cleaning_prompt(session_id: str, issues: List[str]) -> str:
    return f"Suggest cleaning for session {session_id} with issues: {', '.join(issues)}"