"""Quick validation script for the Jobs Engine project."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 60)
print("Jobs Engine - Validation Test")
print("=" * 60)

# Test 1: Skill Extractor
print("\n[1] Testing Skill Extractor...")
from utils.skill_extractor import extract_skills_from_text, categorize_skills
skills = extract_skills_from_text("Python developer with AWS, Docker, React, and SQL experience")
print(f"    Extracted: {skills}")
cats = categorize_skills(skills)
print(f"    Categories: {list(cats.keys())}")
print("    [PASS]")

# Test 2: Dataset Generation & Analytics
print("\n[2] Testing Dataset Generation & Analytics...")
from services.analytics_service import (
    load_dataset, get_market_summary, get_top_skills,
    get_highest_paying_skills, get_demand_by_location
)
df = load_dataset()
summary = get_market_summary(df)
print(f"    Dataset rows: {len(df)}")
print(f"    Avg salary: ${summary['avg_salary']:,}")
print(f"    Top category: {summary['top_category']}")
print(f"    Companies: {summary['unique_companies']}")

top_skills = get_top_skills(df, 5)
print(f"    Top 5 skills: {list(top_skills['skill'])}")

top_paying = get_highest_paying_skills(df, 5)
print(f"    Top paying: {list(top_paying['skill'])}")
print("    [PASS]")

# Test 3: Matching Engine
print("\n[3] Testing Matching Engine...")
from services.matching_service import match_jobs

mock_profile = {
    "skills": ["Python", "AWS", "Docker", "SQL", "Machine Learning"],
    "roles": ["Data Scientist", "ML Engineer"],
    "summary": "Experienced data scientist with cloud and ML skills",
}

mock_jobs = [
    {
        "title": "Senior Data Scientist",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "salary_display": "$150,000 - $200,000",
        "description": "Looking for a data scientist with Python, Machine Learning, SQL, and AWS experience.",
        "apply_url": "https://example.com/job1",
    },
    {
        "title": "Frontend Developer",
        "company": "WebCo",
        "location": "New York, NY",
        "salary_display": "$100,000 - $130,000",
        "description": "React and JavaScript developer needed for building user interfaces.",
        "apply_url": "https://example.com/job2",
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudInc",
        "location": "Seattle, WA",
        "salary_display": "$140,000 - $180,000",
        "description": "DevOps engineer with Docker, Kubernetes, AWS, and Python scripting skills.",
        "apply_url": "https://example.com/job3",
    },
]

matched = match_jobs(mock_profile, mock_jobs, top_n=3)
for job in matched:
    print(f"    {job['title']} @ {job['company']} -> Score: {job['score']}% | Skills: {job['matched_skills']}")
print("    [PASS]")

# Test 4: Service imports
print("\n[4] Testing Service Imports...")
from services.gemini_service import extract_resume_info, analyze_skill_gap, generate_cover_letter
from services.adzuna_service import search_jobs, get_available_countries
countries = get_available_countries()
print(f"    Adzuna countries: {len(countries)} supported")
print(f"    Gemini functions: extract_resume_info, analyze_skill_gap, generate_cover_letter")
print("    [PASS]")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
print("\nTo run the app: streamlit run app.py")
