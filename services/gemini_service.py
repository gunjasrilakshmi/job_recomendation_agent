"""
Gemini AI Service
Handles all interactions with Google's Gemini 2.5 Flash model.
Uses the modern google-genai SDK.
"""

import os
import json
import re
import streamlit as st
from google import genai


def _get_api_key() -> str:
    """Retrieve the Gemini API key from environment or Streamlit secrets."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    return key


def _get_client():
    """Initialize and return the Gemini client."""
    api_key = _get_api_key()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Set it as an environment variable or in .streamlit/secrets.toml"
        )
    return genai.Client(api_key=api_key)


def _generate(prompt: str) -> str:
    """Send a prompt to Gemini 2.5 Flash and return the response text."""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def _parse_json_response(text: str) -> dict | list:
    """Extract and parse JSON from Gemini's response text."""
    # Try to find JSON in code blocks first
    json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if json_match:
        return json.loads(json_match.group(1).strip())
    
    # Try to parse the entire response as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON-like structure in text
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
    
    raise ValueError(f"Could not parse JSON from response: {text[:200]}...")


def extract_resume_info(resume_text: str) -> dict:
    """
    Extract structured professional information from resume text using Gemini.
    
    Args:
        resume_text: Raw text extracted from a resume PDF
        
    Returns:
        Dictionary with keys: skills, experience_level, roles, education
    """
    prompt = f"""You are an expert resume analyzer. Analyze the following resume text and extract structured information.

Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{{
    "skills": ["skill1", "skill2", ...],
    "experience_level": "Entry Level" | "Mid Level" | "Senior Level" | "Lead/Principal" | "Executive",
    "roles": ["role1", "role2", ...],
    "education": "highest degree and field",
    "summary": "2-3 sentence professional summary",
    "years_of_experience": number
}}

Rules:
- Extract ALL technical skills, tools, frameworks, and programming languages mentioned
- Extract soft skills like leadership, communication, etc.
- Identify the most recent and relevant job roles/titles
- Determine experience level based on years and seniority of roles
- Extract the highest education qualification
- Be thorough - don't miss any skills

Resume Text:
{resume_text}
"""
    
    try:
        response_text = _generate(prompt)
        result = _parse_json_response(response_text)
        
        # Validate and provide defaults
        return {
            "skills": result.get("skills", []),
            "experience_level": result.get("experience_level", "Mid Level"),
            "roles": result.get("roles", []),
            "education": result.get("education", "Not specified"),
            "summary": result.get("summary", ""),
            "years_of_experience": result.get("years_of_experience", 0),
        }
    except Exception as e:
        raise Exception(f"Failed to analyze resume with Gemini: {str(e)}")


def analyze_skill_gap(user_skills: list, job_title: str, job_description: str) -> dict:
    """
    Analyze the gap between a user's skills and a job's requirements.
    
    Returns:
        Dictionary with strengths, missing_skills, and recommendations
    """
    prompt = f"""You are a career advisor. Analyze the skill gap between a candidate and a job posting.

Candidate's Skills: {', '.join(user_skills)}

Job Title: {job_title}
Job Description: {job_description}

Return ONLY valid JSON with this structure (no markdown, no explanation):
{{
    "strengths": ["strength1", "strength2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "recommendations": [
        "recommendation1",
        "recommendation2",
        ...
    ],
    "match_assessment": "Strong Match" | "Good Match" | "Moderate Match" | "Developing Match",
    "priority_skills": ["top skill to learn 1", "top skill to learn 2", "top skill to learn 3"],
    "learning_roadmap": [
        {{
            "phase": "Phase title (e.g. Phase 1: Core Fundamentals)",
            "duration": "Estimated time (e.g. Week 1-2)",
            "skills": ["skill to focus on 1", "skill to focus on 2"],
            "steps": ["actionable step 1", "actionable step 2"],
            "resources": ["recommended online course, documentation, or tutorial 1", "recommended resource 2"]
        }}
    ]
}}

Be specific and actionable in your recommendations.
"""
    
    try:
        response_text = _generate(prompt)
        result = _parse_json_response(response_text)
        return {
            "strengths": result.get("strengths", []),
            "missing_skills": result.get("missing_skills", []),
            "recommendations": result.get("recommendations", []),
            "match_assessment": result.get("match_assessment", "Moderate Match"),
            "priority_skills": result.get("priority_skills", []),
            "learning_roadmap": result.get("learning_roadmap", []),
        }
    except Exception as e:
        raise Exception(f"Failed to analyze skill gap: {str(e)}")


def generate_cover_letter(
    user_profile: dict, job_title: str, company: str, job_description: str
) -> str:
    """
    Generate a tailored cover letter for a specific job posting.
    
    Returns:
        Formatted cover letter text
    """
    skills_text = ", ".join(user_profile.get("skills", []))
    roles_text = ", ".join(user_profile.get("roles", []))
    
    prompt = f"""You are an expert career coach and professional writer. Write a compelling, 
tailored cover letter for the following candidate and job.

Candidate Profile:
- Skills: {skills_text}
- Experience Level: {user_profile.get('experience_level', 'Mid Level')}
- Previous Roles: {roles_text}
- Education: {user_profile.get('education', 'Not specified')}
- Summary: {user_profile.get('summary', '')}

Job Details:
- Title: {job_title}
- Company: {company}
- Description: {job_description}

Requirements:
1. Professional but personable tone
2. Highlight relevant skills and experience
3. Show enthusiasm for the specific role and company
4. Include specific examples where possible
5. Keep it concise (3-4 paragraphs)
6. Use proper cover letter format with [Your Name], [Date], etc. placeholders

Write the cover letter now:
"""
    
    try:
        return _generate(prompt)
    except Exception as e:
        raise Exception(f"Failed to generate cover letter: {str(e)}")


def generate_interview_questions(
    user_profile: dict, job_title: str, company: str, job_description: str
) -> list:
    """
    Generate likely interview questions with suggested answers.
    
    Returns:
        List of dictionaries with 'question' and 'answer' keys
    """
    skills_text = ", ".join(user_profile.get("skills", []))
    roles_text = ", ".join(user_profile.get("roles", []))
    
    prompt = f"""You are a senior technical interviewer. Generate 10 likely interview questions 
for the following job, along with suggested answers tailored to the candidate's profile.

Candidate Profile:
- Skills: {skills_text}
- Experience Level: {user_profile.get('experience_level', 'Mid Level')}
- Previous Roles: {roles_text}
- Education: {user_profile.get('education', 'Not specified')}

Job Details:
- Title: {job_title}
- Company: {company}
- Description: {job_description}

Return ONLY valid JSON array (no markdown, no explanation):
[
    {{
        "question": "Interview question here?",
        "answer": "Detailed suggested answer here...",
        "category": "Technical" | "Behavioral" | "Situational" | "Role-Specific"
    }},
    ...
]

Generate exactly 10 questions:
- 3 Technical questions
- 3 Behavioral questions  
- 2 Situational questions
- 2 Role-specific questions

Make answers specific to the candidate's experience and the job requirements.
"""
    
    try:
        response_text = _generate(prompt)
        result = _parse_json_response(response_text)
        
        if isinstance(result, list):
            return result
        return result.get("questions", [])
    except Exception as e:
        raise Exception(f"Failed to generate interview questions: {str(e)}")


def generate_career_insights(user_skills: list, market_data_summary: str) -> str:
    """
    Generate personalized career insights based on user skills and market data.
    
    Returns:
        Formatted career insights text
    """
    prompt = f"""You are a career intelligence analyst. Based on the following market data 
and the candidate's skills, provide personalized career insights and recommendations.

Candidate Skills: {', '.join(user_skills)}

Market Data Summary:
{market_data_summary}

Provide actionable insights including:
1. How the candidate's skills align with market demand
2. Skills they should prioritize learning (with estimated impact, e.g., "increases eligibility by X%")
3. Emerging trends they should be aware of
4. Salary optimization strategies
5. Career path recommendations

Be specific with percentages and data-backed recommendations where possible.
Format your response with clear headings and bullet points.
"""
    
    try:
        return _generate(prompt)
    except Exception as e:
        raise Exception(f"Failed to generate career insights: {str(e)}")
