"""
Matching Service
Deterministic job matching engine using TF-IDF + Cosine Similarity + Skill Overlap.
No AI/LLM used for scoring — purely algorithmic.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re


# Weights for the final composite score
SIMILARITY_WEIGHT = 0.70
SKILL_MATCH_WEIGHT = 0.30


def _clean_text(text: str) -> str:
    """Clean and normalize text for TF-IDF processing."""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z0-9\s\+\#\.]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def _calculate_skill_overlap(user_skills: list[str], job_text: str) -> float:
    """
    Calculate the fraction of user skills that appear in the job text.
    
    Args:
        user_skills: List of skill names from the user's profile
        job_text: Combined job title + description text
        
    Returns:
        Float between 0 and 1 representing skill match ratio
    """
    if not user_skills:
        return 0.0
    
    job_text_lower = job_text.lower()
    matched_count = 0
    
    for skill in user_skills:
        skill_lower = skill.lower()
        # Use word boundary for short skills to avoid false positives
        if len(skill_lower) <= 3:
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', job_text_lower):
                matched_count += 1
        else:
            if skill_lower in job_text_lower:
                matched_count += 1
    
    return matched_count / len(user_skills)


def _get_matched_skills(user_skills: list[str], job_text: str) -> list[str]:
    """Return list of user skills that match the job text."""
    if not user_skills:
        return []
    
    job_text_lower = job_text.lower()
    matched = []
    
    for skill in user_skills:
        skill_lower = skill.lower()
        if len(skill_lower) <= 3:
            if re.search(r'\b' + re.escape(skill_lower) + r'\b', job_text_lower):
                matched.append(skill)
        else:
            if skill_lower in job_text_lower:
                matched.append(skill)
    
    return matched


def match_jobs(user_profile: dict, jobs: list[dict], top_n: int = 10) -> list[dict]:
    """
    Match and rank jobs against a user profile using TF-IDF + Cosine Similarity + Skill Overlap.
    
    Formula: Final Score = 70% * TF-IDF Cosine Similarity + 30% * Skill Overlap Ratio
    
    Args:
        user_profile: Dictionary with 'skills', 'roles', 'experience_level', etc.
        jobs: List of job dictionaries from Adzuna
        top_n: Number of top matches to return
        
    Returns:
        List of top_n jobs sorted by match score (highest first), 
        each augmented with 'score' and 'matched_skills' fields
    """
    if not jobs:
        return []
    
    user_skills = user_profile.get("skills", [])
    user_roles = user_profile.get("roles", [])
    user_summary = user_profile.get("summary", "")
    
    if not user_skills and not user_roles:
        # No profile data — can't match meaningfully
        for job in jobs:
            job["score"] = 0.0
            job["matched_skills"] = []
        return jobs[:top_n]
    
    # Build the user document for TF-IDF
    user_document = _clean_text(
        " ".join(user_skills) + " " + 
        " ".join(user_roles) + " " + 
        user_summary
    )
    
    # Build job documents
    job_documents = []
    for job in jobs:
        job_text = _clean_text(
            job.get("title", "") + " " +
            job.get("description", "") + " " +
            job.get("category", "")
        )
        job_documents.append(job_text)
    
    # Compute TF-IDF cosine similarities
    all_documents = [user_document] + job_documents
    
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),  # Include bigrams for multi-word skills
            min_df=1,
            max_df=0.95,
        )
        tfidf_matrix = vectorizer.fit_transform(all_documents)
        
        # Similarity between user document (index 0) and all job documents
        similarities = cosine_similarity(
            tfidf_matrix[0:1], tfidf_matrix[1:]
        ).flatten()
        
    except ValueError:
        # If vectorizer fails (e.g., all stop words), fall back to skill-only matching
        similarities = np.zeros(len(jobs))
    
    # Score each job
    scored_jobs = []
    for i, job in enumerate(jobs):
        job_text = job.get("title", "") + " " + job.get("description", "")
        
        # Skill overlap score
        skill_score = _calculate_skill_overlap(user_skills, job_text)
        
        # Composite score
        tfidf_score = float(similarities[i]) if i < len(similarities) else 0.0
        final_score = (SIMILARITY_WEIGHT * tfidf_score) + (SKILL_MATCH_WEIGHT * skill_score)
        
        # Get matched skills for display
        matched = _get_matched_skills(user_skills, job_text)
        
        scored_job = {
            **job,
            "score": round(final_score * 100, 1),
            "tfidf_score": round(tfidf_score * 100, 1),
            "skill_score": round(skill_score * 100, 1),
            "matched_skills": matched,
            "match_count": len(matched),
            "total_skills": len(user_skills),
        }
        scored_jobs.append(scored_job)
    
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_jobs[:top_n]
