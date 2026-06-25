"""
Analytics Service
Generates market intelligence from the historical jobs dataset.
Includes dataset generation for first-run setup.
"""

import os
import random
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATASET_PATH = os.path.join(DATA_DIR, "jobs_dataset.csv")


# ---------- Dataset Generation ----------

JOB_CATEGORIES = {
    "Software Engineering": {
        "titles": [
            "Software Engineer", "Software Developer", "Backend Engineer",
            "Frontend Engineer", "Full Stack Developer", "Systems Engineer",
            "Platform Engineer", "Application Developer", "Integration Engineer",
        ],
        "skills": [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go",
            "Git", "Docker", "REST API", "SQL", "Agile", "Scrum",
            "Microservices", "Linux", "CI/CD", "Unit Testing",
        ],
        "salary_range": (75000, 180000),
    },
    "Data Science": {
        "titles": [
            "Data Scientist", "Machine Learning Engineer", "AI Engineer",
            "Data Analyst", "Research Scientist", "NLP Engineer",
            "Computer Vision Engineer", "MLOps Engineer",
        ],
        "skills": [
            "Python", "R", "SQL", "Machine Learning", "Deep Learning",
            "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
            "NLP", "Computer Vision", "Statistics", "A/B Testing",
            "Feature Engineering", "Data Visualization",
        ],
        "salary_range": (80000, 200000),
    },
    "Web Development": {
        "titles": [
            "Web Developer", "Frontend Developer", "React Developer",
            "Angular Developer", "Vue.js Developer", "UI Developer",
            "WordPress Developer", "Webmaster",
        ],
        "skills": [
            "JavaScript", "TypeScript", "React", "Angular", "Vue.js",
            "HTML", "CSS", "Node.js", "REST API", "GraphQL",
            "Webpack", "Git", "Responsive Design", "Figma",
        ],
        "salary_range": (60000, 155000),
    },
    "DevOps & Cloud": {
        "titles": [
            "DevOps Engineer", "Cloud Engineer", "Site Reliability Engineer",
            "Infrastructure Engineer", "Cloud Architect", "Platform Engineer",
            "Release Engineer", "Build Engineer",
        ],
        "skills": [
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Ansible", "Jenkins", "CI/CD", "Linux", "Python", "Bash",
            "Monitoring", "Prometheus", "Grafana", "Infrastructure as Code",
        ],
        "salary_range": (90000, 195000),
    },
    "Cybersecurity": {
        "titles": [
            "Security Engineer", "Security Analyst", "Cybersecurity Specialist",
            "Penetration Tester", "Security Architect", "SOC Analyst",
            "Information Security Manager", "Application Security Engineer",
        ],
        "skills": [
            "Cybersecurity", "Network Security", "Penetration Testing",
            "SIEM", "Firewall", "Encryption", "Python", "Linux",
            "Vulnerability Assessment", "Compliance", "OWASP",
            "Incident Response", "Risk Assessment",
        ],
        "salary_range": (85000, 190000),
    },
    "Mobile Development": {
        "titles": [
            "iOS Developer", "Android Developer", "Mobile Developer",
            "React Native Developer", "Flutter Developer",
            "Mobile App Engineer", "Mobile Architect",
        ],
        "skills": [
            "Swift", "Kotlin", "Java", "React Native", "Flutter",
            "iOS", "Android", "Xcode", "REST API", "Git",
            "Firebase", "CI/CD", "UI/UX", "Agile",
        ],
        "salary_range": (80000, 175000),
    },
    "Product Management": {
        "titles": [
            "Product Manager", "Senior Product Manager", "Technical Product Manager",
            "Product Owner", "Product Analyst", "Growth Product Manager",
            "Associate Product Manager",
        ],
        "skills": [
            "Product Strategy", "Agile", "Scrum", "Data Analysis", "SQL",
            "A/B Testing", "User Research", "Roadmapping", "Jira",
            "Stakeholder Management", "Communication", "Leadership",
        ],
        "salary_range": (90000, 200000),
    },
    "UX/UI Design": {
        "titles": [
            "UX Designer", "UI Designer", "UX/UI Designer", "Product Designer",
            "Interaction Designer", "Visual Designer", "UX Researcher",
        ],
        "skills": [
            "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
            "User Research", "Wireframing", "Prototyping", "Usability Testing",
            "Design Systems", "CSS", "HTML", "Responsive Design",
        ],
        "salary_range": (65000, 160000),
    },
    "Data Engineering": {
        "titles": [
            "Data Engineer", "ETL Developer", "Big Data Engineer",
            "Analytics Engineer", "Data Platform Engineer",
            "Data Infrastructure Engineer",
        ],
        "skills": [
            "Python", "SQL", "Apache Spark", "Airflow", "Kafka",
            "AWS", "Snowflake", "dbt", "Data Warehousing", "ETL",
            "Hadoop", "BigQuery", "Docker", "Databricks",
        ],
        "salary_range": (85000, 190000),
    },
    "Quality Assurance": {
        "titles": [
            "QA Engineer", "Test Engineer", "SDET", "Quality Analyst",
            "Automation Engineer", "Performance Test Engineer",
            "QA Lead",
        ],
        "skills": [
            "Selenium", "Cypress", "Jest", "Pytest", "JUnit",
            "Python", "Java", "JavaScript", "CI/CD", "Git",
            "Agile", "Test Automation", "API Testing", "Postman",
        ],
        "salary_range": (60000, 145000),
    },
}

COMPANIES = [
    "TechNova Solutions", "DataStream Inc", "CloudPeak Systems", "InnovateTech",
    "Quantum Digital", "NexGen Software", "Apex Technologies", "Synapse Labs",
    "Horizon Computing", "Vertex AI", "Digital Forge", "CyberShield Corp",
    "PulsePoint Tech", "Elevate Systems", "CodeCraft Studios", "Nimbus Cloud",
    "SilverLine Tech", "Catalyst Engineering", "ByteWorks", "Fusion Dynamics",
    "Greenfield Tech", "Stellar Systems", "Vanguard Digital", "ProLogic Inc",
    "Summit Technologies", "BlueOcean Labs", "RedShift Computing", "Keystone IT",
    "Pinnacle Software", "Mercury Solutions", "Atlas Data Corp", "Ember Analytics",
    "Ironclad Security", "Zenith Innovations", "Cascade Systems", "Nexus Global",
    "Torchlight AI", "Granite Tech", "Crimson Software", "Echo Dynamics",
    "Sapphire Technologies", "Whiteboard Labs", "Cobalt Engineering", "Prism Digital",
    "Osprey Solutions", "Firefly Analytics", "Helix Technologies", "Redwood Systems",
    "Maverick Tech", "Orion Software Group",
]

LOCATIONS = [
    "New York, NY", "San Francisco, CA", "Seattle, WA", "Austin, TX",
    "Boston, MA", "Chicago, IL", "Los Angeles, CA", "Denver, CO",
    "Atlanta, GA", "Miami, FL", "Portland, OR", "Dallas, TX",
    "San Diego, CA", "Philadelphia, PA", "Phoenix, AZ", "Minneapolis, MN",
    "Raleigh, NC", "Nashville, TN", "Salt Lake City, UT", "Detroit, MI",
    "Washington, DC", "San Jose, CA", "Charlotte, NC", "Columbus, OH",
    "Remote",
]

EXPERIENCE_LEVELS = ["Entry Level", "Mid Level", "Senior Level", "Lead/Principal"]
EXPERIENCE_WEIGHTS = [0.20, 0.35, 0.30, 0.15]


def _generate_dataset(num_rows: int = 50000) -> pd.DataFrame:
    """Generate a synthetic job market dataset with realistic distributions."""
    random.seed(42)
    np.random.seed(42)
    
    records = []
    categories = list(JOB_CATEGORIES.keys())
    # Category distribution — weighted toward Software Engineering and Data Science
    cat_weights = [0.18, 0.14, 0.12, 0.11, 0.08, 0.08, 0.08, 0.07, 0.08, 0.06]
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    for _ in range(num_rows):
        category = random.choices(categories, weights=cat_weights, k=1)[0]
        cat_data = JOB_CATEGORIES[category]
        
        title = random.choice(cat_data["titles"])
        exp_level = random.choices(EXPERIENCE_LEVELS, weights=EXPERIENCE_WEIGHTS, k=1)[0]
        
        # Adjust title based on experience level
        if exp_level == "Senior Level":
            title = "Senior " + title
        elif exp_level == "Lead/Principal":
            title = "Lead " + title
        elif exp_level == "Entry Level":
            title = "Junior " + title
        
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        
        # Salary with location and experience adjustments
        base_min, base_max = cat_data["salary_range"]
        exp_multiplier = {
            "Entry Level": 0.70, "Mid Level": 1.0,
            "Senior Level": 1.35, "Lead/Principal": 1.60,
        }[exp_level]
        
        # Location salary adjustment
        loc_multiplier = 1.0
        if location in ("San Francisco, CA", "San Jose, CA", "New York, NY"):
            loc_multiplier = 1.25
        elif location in ("Seattle, WA", "Boston, MA", "Los Angeles, CA", "Washington, DC"):
            loc_multiplier = 1.15
        elif location == "Remote":
            loc_multiplier = 1.05
        
        salary_min = int(base_min * exp_multiplier * loc_multiplier * random.uniform(0.9, 1.1))
        salary_max = int(base_max * exp_multiplier * loc_multiplier * random.uniform(0.9, 1.1))
        if salary_min > salary_max:
            salary_min, salary_max = salary_max, salary_min
        
        # Select random subset of skills
        num_skills = random.randint(4, min(10, len(cat_data["skills"])))
        skills = random.sample(cat_data["skills"], num_skills)
        
        # Random posting date
        posted_date = start_date + timedelta(days=random.randint(0, date_range_days))
        
        records.append({
            "job_title": title,
            "company": company,
            "location": location,
            "category": category,
            "experience_level": exp_level,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "skills": ", ".join(skills),
            "posted_date": posted_date.strftime("%Y-%m-%d"),
        })
    
    return pd.DataFrame(records)


def ensure_dataset_exists() -> str:
    """Ensure the dataset CSV exists, generating it if needed. Return path."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(DATASET_PATH):
        df = _generate_dataset(50000)
        df.to_csv(DATASET_PATH, index=False)
    
    return DATASET_PATH


# ---------- Analytics Functions ----------

@st.cache_data(ttl=3600)
def load_dataset() -> pd.DataFrame:
    """Load and cache the jobs dataset."""
    path = ensure_dataset_exists()
    df = pd.read_csv(path)
    df["posted_date"] = pd.to_datetime(df["posted_date"])
    df["avg_salary"] = (df["salary_min"] + df["salary_max"]) / 2
    return df


def get_top_skills(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Get the most frequently listed skills across all job postings.
    
    Returns:
        DataFrame with 'skill' and 'count' columns, sorted by count desc
    """
    all_skills = []
    for skills_str in df["skills"].dropna():
        all_skills.extend([s.strip() for s in skills_str.split(",")])
    
    skill_counts = pd.Series(all_skills).value_counts().head(top_n)
    return pd.DataFrame({
        "skill": skill_counts.index,
        "count": skill_counts.values,
        "percentage": (skill_counts.values / len(df) * 100).round(1),
    })


def get_highest_paying_skills(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Get skills associated with the highest average salaries.
    
    Returns:
        DataFrame with 'skill', 'avg_salary', and 'job_count' columns
    """
    skill_salaries = {}
    
    for _, row in df.iterrows():
        if pd.isna(row["skills"]):
            continue
        skills = [s.strip() for s in row["skills"].split(",")]
        avg_sal = row["avg_salary"]
        for skill in skills:
            if skill not in skill_salaries:
                skill_salaries[skill] = {"total": 0, "count": 0}
            skill_salaries[skill]["total"] += avg_sal
            skill_salaries[skill]["count"] += 1
    
    results = []
    for skill, data in skill_salaries.items():
        if data["count"] >= 50:  # Minimum sample size
            results.append({
                "skill": skill,
                "avg_salary": round(data["total"] / data["count"]),
                "job_count": data["count"],
            })
    
    result_df = pd.DataFrame(results)
    return result_df.sort_values("avg_salary", ascending=False).head(top_n).reset_index(drop=True)


def get_demand_by_location(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get job demand and average salary by location.
    
    Returns:
        DataFrame with 'location', 'job_count', and 'avg_salary' columns
    """
    location_stats = df.groupby("location").agg(
        job_count=("job_title", "count"),
        avg_salary=("avg_salary", "mean"),
    ).reset_index()
    
    location_stats["avg_salary"] = location_stats["avg_salary"].round(0).astype(int)
    return location_stats.sort_values("job_count", ascending=False).reset_index(drop=True)


def get_demand_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get job demand and average salary by job category.
    
    Returns:
        DataFrame with 'category', 'job_count', and 'avg_salary' columns
    """
    cat_stats = df.groupby("category").agg(
        job_count=("job_title", "count"),
        avg_salary=("avg_salary", "mean"),
        avg_salary_max=("salary_max", "mean"),
    ).reset_index()
    
    cat_stats["avg_salary"] = cat_stats["avg_salary"].round(0).astype(int)
    cat_stats["avg_salary_max"] = cat_stats["avg_salary_max"].round(0).astype(int)
    return cat_stats.sort_values("job_count", ascending=False).reset_index(drop=True)


def get_experience_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get distribution of jobs by experience level."""
    exp_counts = df["experience_level"].value_counts().reset_index()
    exp_counts.columns = ["experience_level", "count"]
    return exp_counts


def get_trending_skills(df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    """
    Get skills that have grown the most in demand over recent months.
    
    Returns:
        DataFrame with skill name, recent count, previous count, and growth %
    """
    cutoff = df["posted_date"].max() - pd.Timedelta(days=months * 30)
    
    recent = df[df["posted_date"] >= cutoff]
    previous = df[df["posted_date"] < cutoff]
    
    def count_skills(subset):
        all_skills = []
        for skills_str in subset["skills"].dropna():
            all_skills.extend([s.strip() for s in skills_str.split(",")])
        return pd.Series(all_skills).value_counts()
    
    recent_counts = count_skills(recent)
    prev_counts = count_skills(previous)
    
    # Normalize by number of postings in each period
    recent_norm = recent_counts / max(len(recent), 1)
    prev_norm = prev_counts / max(len(previous), 1)
    
    all_skills = set(recent_counts.index) | set(prev_counts.index)
    
    trends = []
    for skill in all_skills:
        r = recent_norm.get(skill, 0)
        p = prev_norm.get(skill, 0)
        
        if p > 0:
            growth = ((r - p) / p) * 100
        elif r > 0:
            growth = 100.0
        else:
            growth = 0.0
        
        if recent_counts.get(skill, 0) >= 20:  # Min sample
            trends.append({
                "skill": skill,
                "recent_mentions": recent_counts.get(skill, 0),
                "previous_mentions": prev_counts.get(skill, 0),
                "growth_pct": round(growth, 1),
            })
    
    result = pd.DataFrame(trends)
    return result.sort_values("growth_pct", ascending=False).head(15).reset_index(drop=True)


def get_salary_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get salary distribution data for histogram plotting."""
    return df[["avg_salary", "category", "experience_level"]].dropna()


def get_market_summary(df: pd.DataFrame) -> dict:
    """Get high-level market summary statistics."""
    return {
        "total_jobs": len(df),
        "avg_salary": int(df["avg_salary"].mean()),
        "median_salary": int(df["avg_salary"].median()),
        "top_category": df["category"].value_counts().index[0],
        "top_location": df["location"].value_counts().index[0],
        "unique_companies": df["company"].nunique(),
        "salary_range": f"${int(df['salary_min'].min()):,} — ${int(df['salary_max'].max()):,}",
        "categories": df["category"].nunique(),
    }


def get_user_eligibility_boost(user_skills: list[str], df: pd.DataFrame) -> list[dict]:
    """
    Calculate how learning specific skills would increase job eligibility.
    
    Returns:
        List of dicts with skill name and eligibility increase percentage
    """
    if not user_skills:
        return []
    
    user_skills_lower = {s.lower() for s in user_skills}
    total_jobs = len(df)
    
    # Count jobs the user currently matches (has at least 1 skill match)
    current_matches = 0
    for skills_str in df["skills"].dropna():
        job_skills = {s.strip().lower() for s in skills_str.split(",")}
        if user_skills_lower & job_skills:
            current_matches += 1
    
    current_pct = (current_matches / total_jobs) * 100 if total_jobs > 0 else 0
    
    # Count all skills in dataset that user doesn't have
    all_skills = []
    for skills_str in df["skills"].dropna():
        all_skills.extend([s.strip() for s in skills_str.split(",")])
    
    skill_counts = pd.Series(all_skills).value_counts()
    
    boosts = []
    for skill, count in skill_counts.items():
        if skill.lower() not in user_skills_lower:
            # Simulate adding this skill
            new_matches = 0
            for skills_str in df["skills"].dropna():
                job_skills = {s.strip().lower() for s in skills_str.split(",")}
                augmented_user = user_skills_lower | {skill.lower()}
                if augmented_user & job_skills:
                    new_matches += 1
            
            new_pct = (new_matches / total_jobs) * 100 if total_jobs > 0 else 0
            boost = new_pct - current_pct
            
            if boost > 0.5:  # Only show meaningful boosts
                boosts.append({
                    "skill": skill,
                    "boost_pct": round(boost, 1),
                    "job_count": count,
                })
    
    boosts.sort(key=lambda x: x["boost_pct"], reverse=True)
    return boosts[:10]
