"""
Jobs Engine — AI Career Intelligence Agent
Main application entry point and home page.
"""

import streamlit as st


# ── Page Config ──
st.set_page_config(
    page_title="Jobs Engine — AI Career Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main-title {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 25%, #A78BFA 50%, #06B6D4 75%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .main-subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.25rem;
        font-weight: 300;
        margin-top: 0.5rem;
        margin-bottom: 2.5rem;
    }

    .feature-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 240px;
    }

    .feature-card:hover {
        border-color: #6366F1;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }

    .feature-title {
        color: #E2E8F0;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #94A3B8;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .stat-number {
        background: linear-gradient(135deg, #6366F1, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
    }

    .stat-label {
        color: #64748B;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .tech-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1E293B, #334155);
        color: #A78BFA;
        padding: 6px 16px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.82rem;
        border: 1px solid #475569;
        font-weight: 500;
    }

    .divider-gradient {
        height: 2px;
        background: linear-gradient(90deg, transparent, #4F46E5, #06B6D4, transparent);
        border: none;
        margin: 2rem 0;
    }

    .workflow-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin: 1rem 0;
    }

    .step-number {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A, #1E293B) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h1 {
        background: linear-gradient(135deg, #6366F1, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5rem;
    }

    .cta-section {
        background: linear-gradient(145deg, #312E81, #1E1B4B);
        border: 1px solid #4338CA;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──
with st.sidebar:
    st.markdown("# 🚀 Jobs Engine")
    st.caption("AI Career Intelligence Agent")
    
    st.divider()
    
    st.markdown("### 📋 Navigation")
    st.markdown("""
    - 📄 **Upload Resume** — Parse your CV
    - 🔍 **Job Search** — Find live jobs
    - ⭐ **Recommendations** — AI insights
    - 📊 **Analytics** — Market data
    """)
    
    st.divider()
    
    # Show profile summary if available
    if "user_profile" in st.session_state:
        profile = st.session_state["user_profile"]
        st.markdown("### 👤 Your Profile")
        st.metric("Skills", len(profile.get("skills", [])))
        st.metric("Level", profile.get("experience_level", "N/A"))
        
        if "matched_jobs" in st.session_state:
            st.metric("Jobs Found", len(st.session_state["matched_jobs"]))
    else:
        st.info("📤 Upload your resume to get started")
    
    st.divider()
    st.caption("Powered by Gemini 2.5 Flash · Adzuna API")


# ── Hero Section ──
st.write("")
st.markdown('<h1 class="main-title">Jobs Engine</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">'
    'Your AI-powered career intelligence agent. Upload your resume, discover matching jobs, '
    'and get personalized career guidance — all in one place.'
    '</p>',
    unsafe_allow_html=True,
)

st.markdown('<div class="divider-gradient"></div>', unsafe_allow_html=True)

# ── Feature Cards ──
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">Smart Resume Parser</div>
        <div class="feature-desc">Upload your PDF resume and let AI extract your skills, experience, and career profile automatically.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Live Job Matching</div>
        <div class="feature-desc">Search real-time jobs from Adzuna and get AI-powered match scores using TF-IDF and skill analysis.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⭐</div>
        <div class="feature-title">AI Recommendations</div>
        <div class="feature-desc">Get skill gap analysis, tailored cover letters, and interview prep questions for every job.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Market Intelligence</div>
        <div class="feature-desc">Explore salary trends, in-demand skills, and career insights from 50,000+ job postings.</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ── How It Works ──
st.markdown('<div class="divider-gradient"></div>', unsafe_allow_html=True)
st.markdown("## How It Works")
st.write("")

steps = [
    ("📄", "Upload Your Resume", "Upload a PDF resume and our AI extracts your skills, experience level, target roles, and education."),
    ("🔍", "Search Live Jobs", "Enter a role and location to search real-time job listings from the Adzuna API across 10+ countries."),
    ("🎯", "AI Matching Engine", "Our TF-IDF + Cosine Similarity engine ranks jobs by relevance, combining semantic matching (70%) with skill overlap (30%)."),
    ("⭐", "Get Recommendations", "Select any job to receive skill gap analysis, a personalized cover letter, and 10 tailored interview Q&A pairs."),
    ("📊", "Market Intelligence", "Explore 50,000+ job postings to discover top skills, salary trends, and personalized career growth strategies."),
]

for i, (icon, title, desc) in enumerate(steps, 1):
    c1, c2 = st.columns([1, 12])
    with c1:
        st.markdown(
            f'<div class="step-number">{i}</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(f"**{icon} {title}**")
        st.caption(desc)

st.write("")

# ── Tech Stack ──
st.markdown('<div class="divider-gradient"></div>', unsafe_allow_html=True)
st.markdown("## Tech Stack")
st.write("")

tech_items = [
    "Streamlit", "Python", "Gemini 2.5 Flash", "Adzuna API",
    "Scikit-learn", "TF-IDF", "Cosine Similarity", "Plotly",
    "Pandas", "NumPy", "pdfplumber", "SQLite",
]

tech_html = " ".join(f'<span class="tech-badge">{t}</span>' for t in tech_items)
st.markdown(tech_html, unsafe_allow_html=True)

st.write("")
st.write("")

# ── CTA Section ──
st.markdown("""
<div class="cta-section">
    <h2 style="color: #E2E8F0; margin-top: 0;">Ready to supercharge your job search?</h2>
    <p style="color: #A5B4FC; font-size: 1.1rem;">
        Start by uploading your resume on the <strong>Upload Resume</strong> page in the sidebar.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ──
st.markdown('<div class="divider-gradient"></div>', unsafe_allow_html=True)
st.caption(
    "Jobs Engine v1.0 · Built with Streamlit & Gemini 2.5 Flash · "
    "Job data from Adzuna · Market intelligence from 50k+ historical postings"
)
