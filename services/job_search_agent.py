# services/job_search_agent.py
"""Job Search Agent module.

Provides a high‑level orchestration that fetches jobs from Adzuna and scores them
using the existing TF‑IDF + skill‑overlap matching engine.
"""

from typing import List, Dict, Any, Optional

from .adzuna_service import search_jobs
from .matching_service import match_jobs


def run_job_search_agent(
    profile: Optional[Dict[str, Any]],
    role: str,
    location: str = "",
    country: str = "US",
    count: int = 20,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    full_time: bool = False,
) -> List[Dict[str, Any]]:
    """Execute job search and optional matching.

    Parameters
    ----------
    profile: dict | None
        User profile extracted from the uploaded resume.
    role: str
        Job title or keyword query.
    location: str, optional
        City or region filter.
    country: str, optional
        Two‑letter country code for Adzuna.
    count: int, optional
        Number of job listings to retrieve.
    salary_min, salary_max: int | None, optional
        Salary range filters.
    full_time: bool, optional
        Restrict to full‑time positions.

    Returns
    -------
    List[dict]
        Jobs enriched with ``score`` and ``matched_skills`` when a profile is
        supplied. If ``profile`` is ``None`` the jobs are returned with a score
        of ``0``.
    """
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
    if profile and profile.get("skills"):
        matched = match_jobs(profile, jobs, top_n=len(jobs))
        matched.sort(key=lambda j: j.get("score", 0), reverse=True)
        return matched
    else:
        for job in jobs:
            job["score"] = 0
            job["matched_skills"] = []
        return jobs
