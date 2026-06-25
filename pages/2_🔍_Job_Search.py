"""
Page 2: Live Job Search
Search Adzuna API → Retrieve jobs → Run matching engine → Display ranked results.
"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.adzuna_service import search_jobs, get_available_countries
from services.matching_service import match_jobs


# ── Page Config ──
st.set_page_config(
    page_title="Job Search — Jobs Engine",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .search-header {
        background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .search-sub {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .job-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: border-color 0.3s;
    }
    .job-card:hover {
        border-color: #6366F1;
    }
    .job-title {
        color: #E2E8F0;
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .job-company {
        color: #A78BFA;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .job-meta {
        color: #94A3B8;
        font-size: 0.85rem;
    }
    .score-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .score-badge.high {
        background: linear-gradient(135deg, #059669, #10B981);
    }
    .score-badge.medium {
        background: linear-gradient(135deg, #D97706, #F59E0B);
    }
    .score-badge.low {
        background: linear-gradient(135deg, #DC2626, #EF4444);
    }
    .matched-skill {
        display: inline-block;
        background: #1E3A5F;
        color: #7DD3FC;
        padding: 3px 10px;
        border-radius: 12px;
        margin: 2px;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown('<p class="search-header">🔍 Live Job Search</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="search-sub">Search real-time job listings and get AI-powered matching scores '
    'based on your resume profile.</p>',
    unsafe_allow_html=True,
)

# ── Check if profile exists ──
has_profile = "user_profile" in st.session_state

if not has_profile:
    st.warning(
        "⚠️ **No resume profile found.** Upload your resume on the "
        "**Upload Resume** page first for personalized job matching. "
        "You can still search jobs without a profile."
    )

# ── Search Form ──
with st.container():
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        default_role = ""
        if has_profile:
            roles = st.session_state["user_profile"].get("roles", [])
            default_role = roles[0] if roles else ""
        
        role = st.text_input(
            "🎯 Job Title / Keywords",
            value=default_role,
            placeholder="e.g., Software Engineer, Data Scientist...",
        )
    
    with col2:
        location = st.text_input(
            "📍 Location",
            placeholder="e.g., New York, San Francisco...",
        )
    
    with col3:
        country = st.selectbox(
            "🌍 Country",
            options=get_available_countries(),
            index=0,
        )

# Advanced filters
with st.expander("⚙️ Advanced Filters"):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        num_results = st.slider("Number of results", 10, 100, 50, step=10)
    with fc2:
        salary_min = st.number_input("Min Salary ($)", value=0, step=10000, min_value=0)
    with fc3:
        salary_max = st.number_input("Max Salary ($)", value=0, step=10000, min_value=0)
    
    full_time = st.checkbox("Full-time only", value=False)

# ── Search Button ──
search_clicked = st.button("🚀 Search Jobs", type="primary", use_container_width=True)

if search_clicked:
    if not role:
        st.error("Please enter a job title or keywords to search.")
        st.stop()
    
    # ── Fetch Jobs ──
    with st.spinner(f"🔎 Searching for **{role}** jobs{' in ' + location if location else ''}..."):
        try:
            jobs = search_jobs(
                role=role,
                location=location,
                country=country,
                count=num_results,
                salary_min=salary_min if salary_min > 0 else None,
                salary_max=salary_max if salary_max > 0 else None,
                full_time=full_time,
            )
        except Exception as e:
            st.error(f"❌ Job search failed: {str(e)}")
            st.stop()
    
    if not jobs:
        st.warning("No jobs found matching your criteria. Try broadening your search.")
        st.stop()
    
    # Store raw jobs
    st.session_state["raw_jobs"] = jobs
    
    # ── Run Matching Engine ──
    if has_profile:
        with st.spinner("🎯 Running AI matching engine..."):
            matched_jobs = match_jobs(st.session_state["user_profile"], jobs, top_n=len(jobs))
        st.session_state["matched_jobs"] = matched_jobs
        display_jobs = matched_jobs
    else:
        # No profile — show jobs without matching scores
        for job in jobs:
            job["score"] = 0
            job["matched_skills"] = []
        st.session_state["matched_jobs"] = jobs
        display_jobs = jobs
    
    # ── Results Header ──
    st.divider()
    r1, r2, r3 = st.columns(3)
    r1.metric("📋 Jobs Found", len(jobs))
    if has_profile:
        avg_score = sum(j["score"] for j in display_jobs[:10]) / min(10, len(display_jobs))
        r2.metric("🎯 Avg Match Score (Top 10)", f"{avg_score:.1f}%")
        high_matches = sum(1 for j in display_jobs if j["score"] >= 50)
        r3.metric("🏆 Strong Matches (50%+)", high_matches)
    
    st.divider()

# ── Display Results ──
if "matched_jobs" in st.session_state and st.session_state["matched_jobs"]:
    display_jobs = st.session_state["matched_jobs"]
    
    st.subheader(f"📋 Top Job Matches ({len(display_jobs)} results)")
    
    # View toggle
    view_mode = st.radio(
        "View mode",
        ["Cards", "Table"],
        horizontal=True,
        label_visibility="collapsed",
    )
    
    if view_mode == "Table":
        # Table view
        table_data = []
        for job in display_jobs:
            table_data.append({
                "Score": f"{job['score']}%" if job['score'] > 0 else "—",
                "Title": job["title"],
                "Company": job["company"],
                "Location": job["location"],
                "Salary": job.get("salary_display", "N/A"),
                "Skills Matched": job.get("match_count", 0),
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    else:
        # Card view
        for idx, job in enumerate(display_jobs):
            score = job.get("score", 0)
            score_class = "high" if score >= 60 else "medium" if score >= 35 else "low"
            
            with st.container():
                col_main, col_score = st.columns([5, 1])
                
                with col_main:
                    st.markdown(f"**{job['title']}**")
                    st.markdown(f"🏢 {job['company']}  ·  📍 {job['location']}  ·  💰 {job.get('salary_display', 'N/A')}")
                    
                    # Description preview
                    desc = job.get("description", "")
                    if desc:
                        preview = desc[:200] + "..." if len(desc) > 200 else desc
                        st.caption(preview)
                    
                    # Matched skills
                    matched = job.get("matched_skills", [])
                    if matched:
                        skills_html = " ".join(
                            f'<span class="matched-skill">{s}</span>' for s in matched[:8]
                        )
                        st.markdown(f"Skills matched: {skills_html}", unsafe_allow_html=True)
                
                with col_score:
                    if score > 0:
                        st.markdown(
                            f'<div style="text-align:center;padding-top:0.5rem;">'
                            f'<span class="score-badge {score_class}">{score}%</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 3])
                with btn_col1:
                    if job.get("apply_url"):
                        st.link_button("🔗 Apply", job["apply_url"], use_container_width=True)
                with btn_col2:
                    if st.button("⭐ Details", key=f"detail_{idx}", use_container_width=True):
                        st.session_state["selected_job"] = job
                        st.session_state["selected_job_idx"] = idx
                        st.switch_page("pages/3_⭐_Recommendations.py")
                
                st.divider()
