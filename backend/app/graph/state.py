"""
State definition for the competitive intelligence workflow.

Defines the shared state object that flows between agents.
Each agent reads from and writes to this state.
"""

from typing import TypedDict, List, Dict, Optional, Literal, Annotated
from datetime import datetime


def keep_first(left, right):
    """
    Reducer that keeps the first (left) value, ignoring updates from parallel nodes.
    For read-only fields, this ensures the original value is preserved.
    Handles strings, lists, booleans, and other types.
    
    Special handling: If left is a "default" value (False, empty string, empty list, None)
    and right is a "real" value, prefer right (the explicit initial state value).
    This handles the case where LangGraph might initialize with defaults before our initial state.
    """
    # If right is None, always use left
    if right is None:
        return left
    
    # If left is None, use right
    if left is None:
        return right
    
    # For booleans: prefer explicit True over default False
    if isinstance(left, bool) and isinstance(right, bool):
        # If left is False (likely default) and right is True (explicit), prefer right
        if not left and right:
            return right
        # If left is True and right is False, keep left (initial state had True)
        if left and not right:
            return left
        # Both same, keep left
        return left
    
    # For lists: if left is empty and right is not, prefer right
    if isinstance(left, list) and isinstance(right, list):
        if len(left) == 0 and len(right) > 0:
            return right  # Prefer non-empty list
        if len(left) > 0:
            return left  # Keep non-empty left
        return left  # Both empty, keep left
    
    # For strings: if left is empty and right is not, prefer right
    if isinstance(left, str) and isinstance(right, str):
        if left == "" and right != "":
            return right  # Prefer non-empty string
        if left != "":
            return left  # Keep non-empty left
        return left  # Both empty, keep left
    
    # For integers: prefer non-zero values
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if left == 0 and right != 0:
            return right  # Prefer non-zero
        if left != 0:
            return left  # Keep non-zero left
        return left  # Both zero, keep left
    
    # Default: keep left (original behavior)
    return left


def prefer_initial(left, right):
    """
    Reducer that prefers the right value (initial state) over left (defaults).
    Use this for read-only fields where we want to ensure the initial state value
    is always used, even if LangGraph creates defaults first.
    """
    # Always prefer right (initial state) if it's not None
    if right is not None:
        return right
    return left


def merge_lists(left, right):
    """
    Reducer that merges two lists and removes duplicates while preserving order.
    Used for completed_agents and errors lists.
    """
    if not left:
        return right if right else []
    if not right:
        return left
    
    # Merge and deduplicate while preserving order
    seen = set()
    result = []
    for item in left + right:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def keep_last(left, right):
    """
    Reducer that keeps the last (right) value - last write wins.
    Used for fields that can be updated by agents and we want the latest value.
    """
    return right if right is not None else left


def keep_unchanged(left, right):
    """
    Reducer for read-only fields that should never change.
    When parallel nodes both return the same read-only field, they return identical values.
    Prefer right (initial state value) to ensure our explicit values override any defaults.
    """
    # Prefer right (initial state) if it's not None, otherwise keep left
    # This ensures our explicit initial state values (like use_auto_discovery=True) 
    # override any default values LangGraph might create
    if right is not None:
        return right
    return left


class CompetitiveIntelligenceState(TypedDict):
    # Shared state passed between all agents in the workflow
    
    # Input parameters (read-only - need reducers because parallel nodes return **state)
    query: Annotated[str, keep_unchanged]  # Read-only, never changes
    company_name: Annotated[str, keep_unchanged]  # Read-only, never changes
    competitors: Annotated[List[str], keep_last]  # Updated by discovery agent when auto-discovery enabled
    use_auto_discovery: Annotated[bool, keep_unchanged]  # Read-only, never changes
    max_competitors: Annotated[int, keep_unchanged]  # Read-only, never changes
    company_info: Annotated[Optional[Dict], keep_last]  # Updated by discovery agent, last write wins
    freshness: Annotated[str, keep_unchanged]  # Read-only, never changes
    
    # Agent outputs (need reducers because parallel nodes return **state with all fields)
    research_results: Annotated[List[Dict], keep_last]  # Only research agent writes, but parallel nodes return it
    extracted_data: Annotated[List[Dict], keep_last]  # Only extraction agent writes, but parallel nodes return it
    crawl_results: Annotated[List[Dict], keep_last]  # Only crawl agent writes, but parallel nodes return it
    analysis: Annotated[Optional[str], keep_last]  # Only analysis agent writes, but parallel nodes return it
    chart_data: Annotated[Optional[Dict], keep_last]  # Only analysis agent writes, but parallel nodes return it
    
    # Workflow metadata (fields that ARE updated by parallel nodes need reducers)
    current_step: Annotated[str, keep_last]  # Both extraction and crawl write this
    completed_agents: Annotated[List[str], merge_lists]  # Both extraction and crawl append to this
    errors: Annotated[List[str], merge_lists]  # Multiple agents may append errors
    
    # Timestamps
    started_at: Annotated[datetime, keep_unchanged]  # Read-only, never changes
    updated_at: Annotated[datetime, keep_last]  # Both extraction and crawl write this