"""
Adzuna API Service
Handles live job search queries via the Adzuna Jobs API.
"""

import os
import requests
import streamlit as st


BASE_URL = "https://api.adzuna.com/v1/api/jobs"

# Adzuna uses country codes for API endpoints
COUNTRY_CODES = {
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Australia": "au",
    "Germany": "de",
    "France": "fr",
    "India": "in",
    "Netherlands": "nl",
    "Brazil": "br",
    "Singapore": "sg",
}


def _get_credentials() -> tuple[str, str]:
    """Retrieve Adzuna API credentials from environment or Streamlit secrets."""
    app_id = os.environ.get("ADZUNA_APP_ID", "")
    app_key = os.environ.get("ADZUNA_APP_KEY", "")
    
    if not app_id:
        try:
            app_id = st.secrets.get("ADZUNA_APP_ID", "")
        except Exception:
            pass
    
    if not app_key:
        try:
            app_key = st.secrets.get("ADZUNA_APP_KEY", "")
        except Exception:
            pass
    
    return app_id, app_key


def search_jobs(
    role: str,
    location: str,
    country: str = "United States",
    count: int = 100,
    salary_min: int | None = None,
    salary_max: int | None = None,
    full_time: bool = False,
) -> list[dict]:
    """
    Search for jobs using the Adzuna API.
    
    Args:
        role: Job title or keywords to search for
        location: City or region
        country: Country name (must be in COUNTRY_CODES)
        count: Maximum number of results to return (up to 100)
        salary_min: Minimum salary filter
        salary_max: Maximum salary filter  
        full_time: Filter for full-time positions only
        
    Returns:
        List of job dictionaries with standardized fields
    """
    app_id, app_key = _get_credentials()
    
    if not app_id or not app_key:
        raise ValueError(
            "Adzuna API credentials not configured. "
            "Set ADZUNA_APP_ID and ADZUNA_APP_KEY as environment variables "
            "or in .streamlit/secrets.toml"
        )
    
    country_code = COUNTRY_CODES.get(country, "us")
    results_per_page = min(50, count)  # Adzuna max per page is 50
    total_pages = (count + results_per_page - 1) // results_per_page
    
    all_jobs = []
    
    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}/{country_code}/search/{page}"
        
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": results_per_page,
            "what": role,
            "content-type": "application/json",
        }
        
        if location:
            params["where"] = location
        
        if salary_min is not None:
            params["salary_min"] = salary_min
        
        if salary_max is not None:
            params["salary_max"] = salary_max
        
        if full_time:
            params["full_time"] = 1
        
        try:
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 401:
                raise ValueError("Invalid Adzuna API credentials. Please check your APP_ID and APP_KEY.")
            
            if response.status_code == 429:
                # Rate limited — return what we have
                break
            
            response.raise_for_status()
            data = response.json()
            
            for result in data.get("results", []):
                job = _normalize_job(result)
                all_jobs.append(job)
                
            # If we got fewer results than expected, no more pages
            if len(data.get("results", [])) < results_per_page:
                break
                
        except requests.exceptions.Timeout:
            if all_jobs:
                break  # Return partial results
            raise Exception("Adzuna API request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            if all_jobs:
                break  # Return partial results
            raise Exception(f"Failed to fetch jobs from Adzuna: {str(e)}")
    
    return all_jobs[:count]


def _normalize_job(raw: dict) -> dict:
    """Normalize a raw Adzuna job result into a standardized format."""
    # Extract salary information
    salary_min = raw.get("salary_min")
    salary_max = raw.get("salary_max")
    
    # Build salary display string
    if salary_min and salary_max:
        salary_display = f"${salary_min:,.0f} - ${salary_max:,.0f}"
    elif salary_min:
        salary_display = f"From ${salary_min:,.0f}"
    elif salary_max:
        salary_display = f"Up to ${salary_max:,.0f}"
    else:
        salary_display = "Not specified"
    
    return {
        "title": raw.get("title", "Untitled Position"),
        "company": raw.get("company", {}).get("display_name", "Company Not Listed"),
        "location": raw.get("location", {}).get("display_name", "Location Not Specified"),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_display": salary_display,
        "description": raw.get("description", "No description available."),
        "apply_url": raw.get("redirect_url", ""),
        "created": raw.get("created", ""),
        "category": raw.get("category", {}).get("label", "General"),
        "contract_type": raw.get("contract_type", ""),
    }


def get_available_countries() -> list[str]:
    """Return list of countries supported by Adzuna API."""
    return list(COUNTRY_CODES.keys())
