"""
State definition for the competitive intelligence workflow.

Defines the shared state object that flows between agents.
Each agent reads from and writes to this state.
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from datetime import datetime


def keep_first(left, right):
    # Keep the first (left) value unless left is default/empty and right is set
    if right is None:
        return left
    if left is None:
        return right
    if isinstance(left, bool) and isinstance(right, bool):
        if not left and right:
            return right
        return left
    if isinstance(left, list) and isinstance(right, list):
        return right if len(left) == 0 and len(right) > 0 else left
    if isinstance(left, str) and isinstance(right, str):
        return right if left == "" and right != "" else left
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return right if left == 0 and right != 0 else left
    return left


def prefer_initial(left, right):
    # Prefer the right value (initial state) if it exists
    return right if right is not None else left


def merge_lists(left, right):
    # Merge two lists, remove duplicates, preserve order
    if not left:
        return right or []
    if not right:
        return left
    seen = set()
    result = []
    for item in left + right:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def keep_last(left, right):
    # Keep the last value (right) if present
    return right if right is not None else left


def keep_unchanged(left, right):
    # Keep original value unless right (initial state) is set
    return right if right is not None else left


class CompetitiveIntelligenceState(TypedDict):
    # Shared workflow state passed between agents
    
    # Input parameters (read-only)
    query: Annotated[str, keep_unchanged]
    company_name: Annotated[str, keep_unchanged]
    competitors: Annotated[List[str], keep_last]  # Can be updated by discovery agent
    use_auto_discovery: Annotated[bool, keep_unchanged]
    max_competitors: Annotated[int, keep_unchanged]
    company_info: Annotated[Optional[Dict], keep_last]  # Discovery agent updates
    freshness: Annotated[str, keep_unchanged]
    
    # Agent outputs
    research_results: Annotated[List[Dict], keep_last]  # Written by research agent
    extracted_data: Annotated[List[Dict], keep_last]    # Written by extraction agent
    crawl_results: Annotated[List[Dict], keep_last]     # Written by crawl agent
    analysis: Annotated[Optional[str], keep_last]       # Written by analysis agent
    chart_data: Annotated[Optional[Dict], keep_last]    # Written by analysis agent
    
    # Workflow metadata
    current_step: Annotated[str, keep_last]             # Updated by multiple agents
    completed_agents: Annotated[List[str], merge_lists] # Agents append to this
    errors: Annotated[List[str], merge_lists]          # Agents append errors
    
    # Timestamps
    started_at: Annotated[datetime, keep_unchanged]
    updated_at: Annotated[datetime, keep_last]
