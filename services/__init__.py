# Services package

"""Utility functions for the Career Intelligence Agent.

This module now includes a lightweight Job Search Agent that
wraps the existing Adzuna search and matching engine.
"""

from .adzuna_service import search_jobs, get_available_countries
from .matching_service import match_jobs

def run_job_search_agent(
    profile: dict,
    role: str,
    location: str = "",
    country: str = "US",
    count: int = 20,
    salary_min: int | None = None,
    salary_max: int | None = None,
    full_time: bool = False,
) -> list[dict]:
    """Execute the job search pipeline.

    Args:
        profile: The uploaded resume profile (contains skills, experience).
        role: Job title or keywords to search for.
        location: Optional location filter.
        country: Country code for the Adzuna API.
        count: Number of job listings to retrieve.
        salary_min: Minimum salary filter (optional).
        salary_max: Maximum salary filter (optional).
        full_time: If True, restrict to full‑time positions.

    Returns:
        A list of matched job dictionaries, each enriched with a
        `score` field and `matched_skills` list.
    """
    # Fetch raw job listings
    jobs = search_jobs(
        role=role,
        location=location,
        country=country,
        count=count,
        salary_min=salary_min,
        salary_max=salary_max,
        full_time=full_time,
    )
    if not jobs:
        return []

    # Score and rank using the existing TF‑IDF + skill overlap engine
    matched_jobs = match_jobs(profile, jobs, top_n=len(jobs))
    return matched_jobs

