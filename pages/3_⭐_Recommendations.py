"""
Page 3: Recommendations & Job Details
When a user selects a job, Gemini performs:
1. Skill Gap Analysis
2. Cover Letter Generation
3. Interview Preparation
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.gemini_service import (
    analyze_skill_gap,
    generate_cover_letter,
    generate_interview_questions,
)


# ── Page Config ──
st.set_page_config(
    page_title="Recommendations — Jobs Engine",
    page_icon="⭐",
    layout="wide",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .rec-header {
        background: linear-gradient(135deg, #F59E0B 0%, #EF4444 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .rec-sub {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .strength-badge {
        display: inline-block;
        background: linear-gradient(135deg, #064E3B, #065F46);
        color: #6EE7B7;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #10B981;
    }
    .gap-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7F1D1D, #991B1B);
        color: #FCA5A5;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #EF4444;
    }
    .priority-badge {
        display: inline-block;
        background: linear-gradient(135deg, #78350F, #92400E);
        color: #FDE68A;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #F59E0B;
    }
    .cover-letter-box {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        font-family: 'Georgia', serif;
        line-height: 1.7;
        color: #E2E8F0;
    }
    .question-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
    }
    .category-tag {
        display: inline-block;
        background: #312E81;
        color: #C7D2FE;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .job-detail-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #4F46E5;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ──
st.markdown('<p class="rec-header">⭐ Job Recommendations</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="rec-sub">Get AI-powered skill gap analysis, personalized cover letters, '
    'and interview preparation for your target jobs.</p>',
    unsafe_allow_html=True,
)

# ── Check prerequisites ──
has_profile = "user_profile" in st.session_state
has_jobs = "matched_jobs" in st.session_state and st.session_state["matched_jobs"]

if not has_profile:
    st.warning(
        "⚠️ **No resume profile found.** Please upload your resume on the "
        "**Upload Resume** page first."
    )
    st.stop()

if not has_jobs:
    st.warning(
        "⚠️ **No job results available.** Please search for jobs on the "
        "**Job Search** page first."
    )
    st.stop()

profile = st.session_state["user_profile"]
matched_jobs = st.session_state["matched_jobs"]

# ── Job Selector ──
st.subheader("Select a Job to Analyze")

# Build selection options
job_options = []
for i, job in enumerate(matched_jobs[:20]):  # Show top 20
    score_str = f" ({job['score']}%)" if job.get("score", 0) > 0 else ""
    option = f"{job['title']} @ {job['company']}{score_str}"
    job_options.append(option)

# Check if a job was pre-selected from the search page
default_idx = st.session_state.get("selected_job_idx", 0)
if default_idx >= len(job_options):
    default_idx = 0

selected_idx = st.selectbox(
    "Choose a job for detailed analysis",
    range(len(job_options)),
    format_func=lambda x: job_options[x],
    index=default_idx,
    key="job_selector",
)

selected_job = matched_jobs[selected_idx]

# ── Display Selected Job Details ──
st.markdown(
    f'<div class="job-detail-card">'
    f'<h3 style="color:#E2E8F0;margin-top:0;">{selected_job["title"]}</h3>'
    f'<p style="color:#A78BFA;font-size:1.05rem;">🏢 {selected_job["company"]}</p>'
    f'<p style="color:#94A3B8;">'
    f'📍 {selected_job["location"]}  ·  💰 {selected_job.get("salary_display", "N/A")}'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True,
)

if selected_job.get("apply_url"):
    st.link_button("🔗 Apply Now", selected_job["apply_url"])

st.divider()

# ── Analysis Tabs ──
tab_gap, tab_cover, tab_interview = st.tabs([
    "🎯 Skill Gap Analysis",
    "📝 Cover Letter",
    "🎤 Interview Prep",
])


# ── Tab 1: Skill Gap Analysis ──
with tab_gap:
    gap_key = f"skill_gap_{selected_idx}"
    
    if gap_key not in st.session_state:
        if st.button("🔍 Analyze Skill Gap", type="primary", key="btn_gap"):
            with st.spinner("🧠 Analyzing skill gap with AI..."):
                try:
                    analysis = analyze_skill_gap(
                        user_skills=profile.get("skills", []),
                        job_title=selected_job["title"],
                        job_description=selected_job.get("description", ""),
                    )
                    st.session_state[gap_key] = analysis
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.stop()
    
    if gap_key in st.session_state:
        analysis = st.session_state[gap_key]
        
        # Match Assessment
        assessment = analysis.get("match_assessment", "Moderate Match")
        assessment_colors = {
            "Strong Match": ("🟢", "#10B981"),
            "Good Match": ("🔵", "#3B82F6"),
            "Moderate Match": ("🟡", "#F59E0B"),
            "Developing Match": ("🟠", "#EF4444"),
        }
        emoji, color = assessment_colors.get(assessment, ("⚪", "#94A3B8"))
        
        st.markdown(
            f"### {emoji} Assessment: **{assessment}**"
        )
        st.write("")
        
        # Strengths and Gaps in columns
        col_str, col_gap = st.columns(2)
        
        with col_str:
            st.markdown("#### ✅ Your Strengths")
            strengths = analysis.get("strengths", [])
            if strengths:
                html = "".join(f'<span class="strength-badge">{s}</span>' for s in strengths)
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified.")
        
        with col_gap:
            st.markdown("#### ❌ Missing Skills")
            missing = analysis.get("missing_skills", [])
            if missing:
                html = "".join(f'<span class="gap-badge">{s}</span>' for s in missing)
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.success("No significant skill gaps found!")
        
        st.write("")
        
        # Priority Skills
        priority = analysis.get("priority_skills", [])
        if priority:
            st.markdown("#### 🔥 Priority Skills to Learn")
            html = "".join(f'<span class="priority-badge">⚡ {s}</span>' for s in priority)
            st.markdown(html, unsafe_allow_html=True)
        
        st.write("")
        
        # Recommendations
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            st.markdown("#### 💡 Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")


# ── Tab 2: Cover Letter ──
with tab_cover:
    cover_key = f"cover_letter_{selected_idx}"
    
    if cover_key not in st.session_state:
        if st.button("✍️ Generate Cover Letter", type="primary", key="btn_cover"):
            with st.spinner("📝 Writing your personalized cover letter..."):
                try:
                    letter = generate_cover_letter(
                        user_profile=profile,
                        job_title=selected_job["title"],
                        company=selected_job["company"],
                        job_description=selected_job.get("description", ""),
                    )
                    st.session_state[cover_key] = letter
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
                    st.stop()
    
    if cover_key in st.session_state:
        letter = st.session_state[cover_key]
        
        st.markdown("### 📝 Your Tailored Cover Letter")
        st.write("")
        
        st.markdown(
            f'<div class="cover-letter-box">{letter.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        
        st.write("")
        
        # Copy button
        col_copy, col_regen = st.columns(2)
        with col_copy:
            st.download_button(
                "📥 Download as Text",
                data=letter,
                file_name=f"cover_letter_{selected_job['company'].replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_regen:
            if st.button("🔄 Regenerate", key="regen_cover", use_container_width=True):
                del st.session_state[cover_key]
                st.rerun()


# ── Tab 3: Interview Prep ──
with tab_interview:
    interview_key = f"interview_{selected_idx}"
    
    if interview_key not in st.session_state:
        if st.button("🎤 Generate Interview Questions", type="primary", key="btn_interview"):
            with st.spinner("🧠 Preparing interview questions and answers..."):
                try:
                    questions = generate_interview_questions(
                        user_profile=profile,
                        job_title=selected_job["title"],
                        company=selected_job["company"],
                        job_description=selected_job.get("description", ""),
                    )
                    st.session_state[interview_key] = questions
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
                    st.stop()
    
    if interview_key in st.session_state:
        questions = st.session_state[interview_key]
        
        st.markdown(f"### 🎤 Interview Preparation — {len(questions)} Questions")
        st.write("")
        
        # Group by category
        categories = {}
        for q in questions:
            cat = q.get("category", "General")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(q)
        
        # Category icons
        cat_icons = {
            "Technical": "💻",
            "Behavioral": "🤝",
            "Situational": "🎭",
            "Role-Specific": "🎯",
            "General": "📋",
        }
        
        for cat, cat_questions in categories.items():
            icon = cat_icons.get(cat, "📋")
            st.markdown(f"#### {icon} {cat} Questions")
            
            for i, q in enumerate(cat_questions, 1):
                with st.expander(f"Q: {q.get('question', 'Question')}"):
                    st.markdown("**Suggested Answer:**")
                    st.markdown(q.get("answer", "No suggested answer available."))
            
            st.write("")
        
        # Download all Q&A
        qa_text = ""
        for q in questions:
            qa_text += f"Category: {q.get('category', 'General')}\n"
            qa_text += f"Q: {q.get('question', '')}\n"
            qa_text += f"A: {q.get('answer', '')}\n"
            qa_text += f"\n{'='*60}\n\n"
        
        st.download_button(
            "📥 Download All Q&A",
            data=qa_text,
            file_name=f"interview_prep_{selected_job['company'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
