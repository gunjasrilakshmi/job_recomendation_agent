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

# ── Sidebar ──
with st.sidebar:
    st.markdown("# 🚀 Jobs Engine")
    st.caption("AI Career Intelligence Agent")
    st.divider()
    
    if "user_profile" in st.session_state:
        profile = st.session_state["user_profile"]
        st.markdown("### 👤 Your Profile")
        st.metric("Skills", len(profile.get("skills", [])))
        st.metric("Level", profile.get("experience_level", "N/A"))
        
        if "matched_jobs" in st.session_state:
            st.metric("Jobs Found", len(st.session_state["matched_jobs"]))
    else:
        st.info("📤 Upload your resume to get started")
        
#     from utils.sidebar import render_agentic_workflow
#     render_agentic_workflow()

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

# ── Display Selected Job Details & Match Score Explanation ──
score = selected_job.get("score", 0)
tfidf_score = selected_job.get("tfidf_score", 0)
skill_score = selected_job.get("skill_score", 0)
matched_skills = selected_job.get("matched_skills", [])

# Determine score color
score_color = "#10B981" if score >= 60 else "#F59E0B" if score >= 35 else "#EF4444"

st.markdown(
    f'<div class="job-detail-card">'
    f'<div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">'
    f'<div>'
    f'<h3 style="color:#E2E8F0;margin-top:0;margin-bottom:0.3rem;">{selected_job["title"]}</h3>'
    f'<p style="color:#A78BFA;font-size:1.05rem;margin-bottom:0.5rem;">🏢 {selected_job["company"]}</p>'
    f'<p style="color:#94A3B8;margin-bottom:0;">'
    f'📍 {selected_job["location"]}  ·  💰 {selected_job.get("salary_display", "N/A")}'
    f'</p>'
    f'</div>'
    f'<div style="text-align:center; background:rgba(30,41,59,0.5); padding:0.75rem 1.25rem; border-radius:12px; border:1px solid #334155; min-width:120px;">'
    f'<div style="font-size:0.75rem; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.2rem;">Match Score</div>'
    f'<div style="font-size:2.2rem; font-weight:800; color:{score_color}; line-height:1.1;">{score}%</div>'
    f'</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("📊 Score Explanation — How was this calculated?", expanded=True):
    st.markdown(f"""
    The Jobs Engine matching algorithm calculates a **deterministic, dual-factor fit score** to ensure consistent, transparent results:
    
    $$\\text{{Final Score}} = (70\\% \\times \\text{{Semantic Similarity}}) + (30\\% \\times \\text{{Skill Overlap}})$$
    
    Here is the detailed breakdown for your profile match with this role:
    """)
    
    c_tfidf, c_skills = st.columns(2)
    with c_tfidf:
        st.markdown(f"""
        **🤖 Semantic Match (TF-IDF): `{tfidf_score}%`**  
        * **Weight:** 70% of final score
        * **Method:** We vectorize your resume summary, target roles, and skills, then compute the **Cosine Similarity** against the job title, description, and category.
        * **Insights:** Reflects how well your broad professional background aligns contextually and conceptually with the position.
        """)
    with c_skills:
        st.markdown(f"""
        **🛠️ Skill Match (Direct Overlap): `{skill_score}%`**  
        * **Weight:** 30% of final score
        * **Method:** Checks which of your **{len(profile.get("skills", []))} extracted skills** appear directly in the job posting text.
        * **Insights:** You directly match **{len(matched_skills)}** skills in this job description.
        """)
        
    st.markdown("---")
    if matched_skills:
        chips_html = "".join(f'<span class="matched-skill">{s}</span>' for s in matched_skills)
        st.markdown(f"**Matched skills contributing to this score:**<br>{chips_html}", unsafe_allow_html=True)
    else:
        st.markdown("*No direct skill overlap detected in the text. The score is driven by semantic context.*")

if selected_job.get("apply_url"):
    st.link_button("🔗 Apply Now", selected_job["apply_url"])

# ── Run All Agents Pipeline ──
pipeline_key = f"pipeline_done_{selected_idx}"
gap_key = f"skill_gap_{selected_idx}"
cover_key = f"cover_letter_{selected_idx}"
interview_key = f"interview_{selected_idx}"

if pipeline_key not in st.session_state:
    if st.button("🚀 Run Full Agent Pipeline", type="primary", use_container_width=True):
        from utils.agent_display import agent_status_card, agent_connector
        
        st.markdown("### 🤖 Agent Pipeline Execution")
        st.caption("Running all agents in sequence for this job...")
        st.write("")
        
        # Show prior agents as completed
        agent_status_card("Resume Upload", "📤", "Candidate resume ingested", "completed")
        agent_connector()
        agent_status_card("Resume Analysis Agent", "🤖", f"Extracted {len(profile.get('skills', []))} skills", "completed")
        agent_connector()
        agent_status_card("Job Analysis Agent", "🔍", f"Retrieved job listings from Adzuna", "completed")
        agent_connector()
        agent_status_card("Match Scoring Agent", "🎯", f"Scored jobs — This job: {score}%", "completed")
        agent_connector()
        
        # ── Agent 5: Resume Tailoring Agent ──
        tailoring_placeholder = st.empty()
        with tailoring_placeholder.container():
            agent_status_card("Resume Tailoring Agent", "✍️", "Generating tailored cover letter...", "running")
        
        try:
            letter = generate_cover_letter(
                user_profile=profile,
                job_title=selected_job["title"],
                company=selected_job["company"],
                job_description=selected_job.get("description", ""),
            )
            st.session_state[cover_key] = letter
            with tailoring_placeholder.container():
                agent_status_card("Resume Tailoring Agent", "✍️", "Cover letter generated successfully", "completed")
        except Exception as e:
            with tailoring_placeholder.container():
                agent_status_card("Resume Tailoring Agent", "✍️", f"Error: {str(e)}", "error")
        
        agent_connector()
        
        # ── Agent 6: Interview Coach Agent ──
        interview_placeholder = st.empty()
        with interview_placeholder.container():
            agent_status_card("Interview Coach Agent", "🎤", "Generating interview prep Q&A...", "running")
        
        try:
            questions = generate_interview_questions(
                user_profile=profile,
                job_title=selected_job["title"],
                company=selected_job["company"],
                job_description=selected_job.get("description", ""),
            )
            st.session_state[interview_key] = questions
            with interview_placeholder.container():
                agent_status_card("Interview Coach Agent", "🎤", f"Generated {len(questions)} interview questions", "completed")
        except Exception as e:
            with interview_placeholder.container():
                agent_status_card("Interview Coach Agent", "🎤", f"Error: {str(e)}", "error")
        
        agent_connector()
        
        # ── Agent 7: Career Roadmap Agent ──
        roadmap_placeholder = st.empty()
        with roadmap_placeholder.container():
            agent_status_card("Career Roadmap Agent", "🗺️", "Analyzing skill gaps & building learning roadmap...", "running")
        
        try:
            analysis = analyze_skill_gap(
                user_skills=profile.get("skills", []),
                job_title=selected_job["title"],
                job_description=selected_job.get("description", ""),
            )
            st.session_state[gap_key] = analysis
            missing_count = len(analysis.get("missing_skills", []))
            roadmap_phases = len(analysis.get("learning_roadmap", []))
            with roadmap_placeholder.container():
                agent_status_card("Career Roadmap Agent", "🗺️", f"Identified {missing_count} gaps, created {roadmap_phases}-phase roadmap", "completed")
        except Exception as e:
            with roadmap_placeholder.container():
                agent_status_card("Career Roadmap Agent", "🗺️", f"Error: {str(e)}", "error")
        
        st.session_state[pipeline_key] = True
        st.write("")
        st.success("✅ **All agents completed!** Scroll down to view the full results.")
        st.rerun()

st.divider()

# ── Tabs Creation (Unconditional Layout Level) ──
tab_gap, tab_cover, tab_interview = st.tabs([
    "🗺️ Career Roadmap & Skill Gaps",
    "✍️ Tailored Cover Letter",
    "🎤 Interview Preparation",
])

# ── Tab 1: Career Roadmap & Skill Gaps ──
with tab_gap:
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
        
        st.markdown(f"### {emoji} Assessment: **{assessment}**")
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
        
        # Structured Learning Roadmap
        roadmap = analysis.get("learning_roadmap", [])
        if roadmap:
            st.write("")
            st.divider()
            st.markdown("### 🗺️ AI-Generated Learning Roadmap")
            st.caption("A structured, step-by-step roadmap tailored to bridge your skill gaps for this specific position:")
            
            for i, phase in enumerate(roadmap, 1):
                with st.container():
                    st.markdown(
                        f'<div style="background:linear-gradient(145deg, #1E293B, #0F172A); padding:1.25rem; border-radius:12px; border-left:4px solid #F59E0B; margin:0.75rem 0;">'
                        f'<div style="display:flex; justify-content:space-between; flex-wrap:wrap; margin-bottom:0.5rem;">'
                        f'<strong style="font-size:1.1rem; color:#E2E8F0;">{phase.get("phase", f"Phase {i}")}</strong>'
                        f'<span style="color:#F59E0B; font-weight:600; font-size:0.9rem;">⏳ {phase.get("duration", "N/A")}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    
                    skills = phase.get("skills", [])
                    if skills:
                        skills_html = " ".join(f'<span class="priority-badge" style="font-size:0.75rem; padding:2px 8px;">{s}</span>' for s in skills)
                        st.markdown(f"<div style='margin-bottom:0.75rem;'><strong>Skills to Focus On:</strong> {skills_html}</div>", unsafe_allow_html=True)
                    
                    steps = phase.get("steps", [])
                    if steps:
                        st.markdown("**Action Steps:**")
                        for step in steps:
                            st.markdown(f"- {step}")
                    
                    resources = phase.get("resources", [])
                    if resources:
                        st.markdown("<div style='margin-top:0.5rem;'><strong>Recommended Resources:</strong></div>", unsafe_allow_html=True)
                        for res in resources:
                            st.markdown(f"- 📖 {res}")
                            
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Career Roadmap Agent did not produce results. Click the button below to run the analysis individually, or run the full pipeline above.")
        if st.button("🔍 Analyze Skill Gap", type="primary", key="btn_gap"):
            with st.spinner("🧠 Analyzing skill gap with AI..."):
                try:
                    analysis = analyze_skill_gap(
                        user_skills=profile.get("skills", []),
                        job_title=selected_job["title"],
                        job_description=selected_job.get("description", ""),
                    )
                    st.session_state[gap_key] = analysis
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

# ── Tab 2: Cover Letter ──
with tab_cover:
    if cover_key in st.session_state:
        letter = st.session_state[cover_key]
        
        st.markdown("### ✍️ Your Tailored Cover Letter")
        st.write("")
        
        st.markdown(
            f'<div class="cover-letter-box">{letter.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )
        
        st.write("")
        
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
                if pipeline_key in st.session_state:
                    del st.session_state[pipeline_key]
                st.rerun()
    else:
        st.info("Resume Tailoring Agent did not produce results. Click the button below to generate a cover letter individually, or run the full pipeline above.")
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
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")

# ── Tab 3: Interview Prep ──
with tab_interview:
    if interview_key in st.session_state:
        questions = st.session_state[interview_key]
        
        st.markdown(f"### 🎤 Interview Preparation — {len(questions)} Questions")
        st.write("")
        
        categories = {}
        for q in questions:
            cat = q.get("category", "General")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(q)
        
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
