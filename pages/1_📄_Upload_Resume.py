"""
Page 1: Resume Upload
Upload PDF resume → Extract text → Analyze with Gemini → Store profile in session state.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.pdf_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills_from_text, categorize_skills
from services.gemini_service import extract_resume_info


# ── Page Config ──
st.set_page_config(
    page_title="Upload Resume — Jobs Engine",
    page_icon="📄",
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
    else:
        st.info("📤 Upload your resume to get started")
        
    from utils.sidebar import render_agentic_workflow
#     render_agentic_workflow()

# ── Custom CSS ──
st.markdown("""
<style>
    .upload-header {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .upload-sub {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .skill-chip {
        display: inline-block;
        background: linear-gradient(135deg, #312E81, #4338CA);
        color: #C7D2FE;
        padding: 6px 14px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #4338CA;
    }
    .profile-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .success-banner {
        background: linear-gradient(135deg, #064E3B, #065F46);
        border: 1px solid #10B981;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: #A7F3D0;
    }
    .stFileUploader > div {
        border: 2px dashed #4338CA !important;
        border-radius: 16px !important;
        padding: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Page Header ──
st.markdown('<p class="upload-header">📄 Upload Your Resume</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="upload-sub">Upload your resume and let AI extract your professional profile. '
    'We\'ll identify your skills, experience level, and target roles.</p>',
    unsafe_allow_html=True,
)

# ── File Upload ──
uploaded_file = st.file_uploader(
    "Upload your resume (PDF format)",
    type=["pdf"],
    help="Maximum file size: 10MB. We support text-based PDF resumes.",
    key="resume_uploader",
)

if uploaded_file is not None:
    # Show file info
    file_size_kb = uploaded_file.size / 1024
    st.info(f"📎 **{uploaded_file.name}** ({file_size_kb:.1f} KB)")
    
    # Extract text from PDF
    with st.spinner("📖 Extracting text from your resume..."):
        try:
            resume_text = extract_text_from_pdf(uploaded_file)
        except Exception as e:
            st.error(f"❌ {str(e)}")
            st.stop()
    
    # Show extracted text preview
    st.success(f"✅ Successfully extracted **{len(resume_text):,}** characters from your resume.")
    
    with st.expander("👀 Preview Extracted Text", expanded=False):
        st.text_area(
            "Raw text",
            resume_text,
            height=250,
            disabled=True,
            label_visibility="collapsed",
        )
    
    st.divider()
    
    # ── AI Agent Pipeline ──
    analyze_clicked = st.button(
        "🚀 Run Resume Analysis Agent",
        type="primary",
        use_container_width=True,
    )
    
    if analyze_clicked:
        from utils.agent_display import agent_status_card, agent_connector
        
        st.markdown("### 🤖 Agent Pipeline Execution")
        st.caption("Agents are processing your resume in sequence...")
        st.write("")
        
        # Step 1: Resume Upload — mark completed
        agent_status_card("Resume Upload", "📤", "Ingest candidate resume PDF", "completed")
        agent_connector()
        
        # Step 2: Resume Analysis Agent — show running
        agent_placeholder = st.empty()
        with agent_placeholder.container():
            agent_status_card("Resume Analysis Agent", "🤖", "Parsing text & extracting skills with Gemini AI", "running")
        
        try:
            profile = extract_resume_info(resume_text)
        except Exception as e:
            with agent_placeholder.container():
                agent_status_card("Resume Analysis Agent", "🤖", f"Error: {str(e)}", "error")
            st.info("💡 Make sure your GEMINI_API_KEY is configured correctly.")
            st.stop()
        
        # Also extract skills using keyword matcher as supplement
        keyword_skills = extract_skills_from_text(resume_text)
        # Merge skills (Gemini + keyword matcher, deduplicated)
        all_skills = list(dict.fromkeys(
            profile.get("skills", []) + keyword_skills
        ))
        profile["skills"] = all_skills
        
        # Store in session state
        st.session_state["user_profile"] = profile
        st.session_state["resume_text"] = resume_text
        
        # Mark completed
        with agent_placeholder.container():
            agent_status_card("Resume Analysis Agent", "🤖", f"Extracted {len(all_skills)} skills, {len(profile.get('roles', []))} roles", "completed")
        
        # ── Display Results ──
        st.markdown('<div class="success-banner">✅ <strong>Profile extracted successfully!</strong> '
                    'Navigate to <strong>Job Search</strong> to find matching opportunities.</div>',
                    unsafe_allow_html=True)
        
        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🛠️ Skills Found", len(profile["skills"]))
        m2.metric("📊 Experience", profile.get("experience_level", "N/A"))
        m3.metric("💼 Roles", len(profile.get("roles", [])))
        m4.metric("🎓 Education", profile.get("education", "N/A")[:20])
        
        st.divider()
        
        # Professional Summary
        if profile.get("summary"):
            st.subheader("📝 Professional Summary")
            st.markdown(f"> {profile['summary']}")
            st.write("")
        
        # Skills display
        col_skills, col_details = st.columns([3, 2])
        
        with col_skills:
            st.subheader("🛠️ Your Skills")
            categorized = categorize_skills(profile["skills"])
            
            if categorized:
                for category, skills in categorized.items():
                    st.markdown(f"**{category}**")
                    chips_html = "".join(
                        f'<span class="skill-chip">{skill}</span>' for skill in skills
                    )
                    st.markdown(chips_html, unsafe_allow_html=True)
                    st.write("")
            
            # Uncategorized skills
            categorized_set = {s for skills in categorized.values() for s in skills}
            uncategorized = [s for s in profile["skills"] if s not in categorized_set]
            if uncategorized:
                st.markdown("**Other Skills**")
                chips_html = "".join(
                    f'<span class="skill-chip">{skill}</span>' for skill in uncategorized
                )
                st.markdown(chips_html, unsafe_allow_html=True)
        
        with col_details:
            st.subheader("💼 Target Roles")
            for role in profile.get("roles", []):
                st.markdown(f"- {role}")
            
            st.write("")
            st.subheader("📋 Profile Details")
            st.markdown(f"**Experience Level:** {profile.get('experience_level', 'N/A')}")
            st.markdown(f"**Education:** {profile.get('education', 'N/A')}")
            if profile.get("years_of_experience"):
                st.markdown(f"**Years of Experience:** ~{profile['years_of_experience']}")

# ── Show existing profile if already analyzed ──
elif "user_profile" in st.session_state:
    st.markdown("---")
    st.subheader("📋 Current Profile")
    profile = st.session_state["user_profile"]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("🛠️ Skills", len(profile.get("skills", [])))
    m2.metric("📊 Experience", profile.get("experience_level", "N/A"))
    m3.metric("💼 Roles", len(profile.get("roles", [])))
    
    if profile.get("skills"):
        chips_html = "".join(
            f'<span class="skill-chip">{s}</span>' for s in profile["skills"]
        )
        st.markdown(chips_html, unsafe_allow_html=True)
    
    st.info("📤 Upload a new resume above to update your profile.")
else:
    st.markdown("---")
    st.markdown(
        "### 👆 Upload your resume to get started\n\n"
        "Your resume will be analyzed by AI to extract:\n"
        "- **Technical & soft skills**\n"
        "- **Experience level**\n"
        "- **Target roles**\n"
        "- **Education background**\n\n"
        "This profile is used to match you with the best job opportunities."
    )
