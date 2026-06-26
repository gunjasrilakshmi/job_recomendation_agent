"""
Sidebar Utility
Renders a dynamic, beautifully styled visualization of the Agentic Workflow in the sidebar.
Tracks the active state of all 7 agents in real-time.
"""

import streamlit as st
import os


def render_agentic_workflow():
    """Renders a dynamic agentic workflow pipeline in the sidebar matching the user's specification."""
    st.divider()
    st.markdown("### 🤖 Agentic Workflow")
    
    # Get active page name
    try:
        import inspect
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        filename = module.__file__ if module else ""
        page_name = os.path.basename(filename)
    except Exception:
        page_name = ""
        
    # Check session states
    has_upload = "resume_text" in st.session_state
    has_profile = "user_profile" in st.session_state
    has_jobs = "raw_jobs" in st.session_state or "matched_jobs" in st.session_state
    has_matches = "matched_jobs" in st.session_state
    
    selected_idx = st.session_state.get("selected_job_idx")
    has_analysis = "selected_job" in st.session_state
    
    has_tailoring = False
    has_interview = False
    has_roadmap = False
    if selected_idx is not None:
        has_tailoring = f"cover_letter_{selected_idx}" in st.session_state
        has_interview = f"interview_{selected_idx}" in st.session_state
        has_roadmap = f"skill_gap_{selected_idx}" in st.session_state

    # Page flags
    is_upload = "Upload_Resume" in page_name
    is_search = "Job_Search" in page_name
    is_rec = "Recommendations" in page_name

    # Determine status & color for each step/agent
    # Helper function
    def get_status(completed, active):
        if completed:
            return "🟢 Completed", "#10B981"
        elif active:
            return "⚡ Active", "#3B82F6"
        else:
            return "💤 Idle", "#64748B"

    status_upload, color_upload = get_status(has_upload, is_upload and not has_upload)
    status_resume, color_resume = get_status(has_profile, is_upload and has_upload and not has_profile)
    status_job, color_job = get_status(has_jobs, is_search and not has_jobs)
    status_match, color_match = get_status(has_matches, is_search and has_jobs and not has_matches)
    status_tailoring, color_tailoring = get_status(has_tailoring, is_rec and has_analysis and not has_tailoring)
    status_interview, color_interview = get_status(has_interview, is_rec and has_tailoring and not has_interview)
    status_roadmap, color_roadmap = get_status(has_roadmap, is_rec and has_interview and not has_roadmap)

    # Draw HTML pipeline
    pipeline_html = f"""
    <div style="background: linear-gradient(145deg, #1E293B, #0F172A); padding: 0.85rem; border-radius: 12px; border: 1px solid #334155; font-family: 'Inter', sans-serif; margin-bottom: 1rem;">
        <div style="display: flex; flex-direction: column; gap: 0.65rem;">
            
            <!-- 1. Resume Upload -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">📤 Resume Upload</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_upload};">{status_upload}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Ingest candidate resume PDF</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 2. Resume Analysis Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">🤖 Resume Analysis Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_resume};">{status_resume}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Parses text & extracts skills</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 3. Job Analysis Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">🔍 Job Analysis Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_job};">{status_job}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Queries & ingests job listings</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 4. Match Scoring Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">🎯 Match Scoring Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_match};">{status_match}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Ranks fit with TF-IDF & overlap</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 5. Resume Tailoring Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">✍️ Resume Tailoring Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_tailoring};">{status_tailoring}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Generates tailored cover letters</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 6. Interview Coach Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">🎤 Interview Coach Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_interview};">{status_interview}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Generates job-specific prep Q&A</div>
            </div>
            
            <!-- Connector -->
            <div style="border-left: 2px dashed #334155; height: 8px; margin-left: 0.5rem; margin-top: -0.35rem; margin-bottom: -0.35rem;"></div>
            
            <!-- 7. Career Roadmap Agent -->
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; font-weight: 700; color: #E2E8F0;">🗺️ Career Roadmap Agent</span>
                    <span style="font-size: 0.72rem; font-weight: bold; color: {color_roadmap};">{status_roadmap}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.7rem; margin-left: 1.15rem; line-height: 1.1;">Maps gaps & creates roadmap</div>
            </div>
            
        </div>
    </div>
    """
    st.markdown(pipeline_html, unsafe_allow_html=True)
