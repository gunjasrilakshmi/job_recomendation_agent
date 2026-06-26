"""
Agent Display Utility
Renders visual agent execution status cards in the main content area.
Used to show the agentic pipeline progressing step by step.
"""

import streamlit as st


def agent_status_card(name: str, icon: str, description: str, status: str = "idle"):
    """
    Render a single agent status card.
    
    Args:
        name: Agent name (e.g. "Resume Analysis Agent")
        icon: Emoji icon
        description: Brief description of what the agent does
        status: "idle" | "running" | "completed" | "error"
    """
    if status == "completed":
        border_color = "#10B981"
        status_html = '<span style="color:#10B981; font-weight:700; font-size:0.85rem;">✅ Completed</span>'
        bg = "linear-gradient(145deg, #0D2818, #0F172A)"
    elif status == "running":
        border_color = "#3B82F6"
        status_html = '<span style="color:#3B82F6; font-weight:700; font-size:0.85rem;">⚡ Running...</span>'
        bg = "linear-gradient(145deg, #1E293B, #172554)"
    elif status == "error":
        border_color = "#EF4444"
        status_html = '<span style="color:#EF4444; font-weight:700; font-size:0.85rem;">❌ Error</span>'
        bg = "linear-gradient(145deg, #1E293B, #2D1B1B)"
    else:
        border_color = "#334155"
        status_html = '<span style="color:#64748B; font-weight:700; font-size:0.85rem;">💤 Waiting</span>'
        bg = "linear-gradient(145deg, #1E293B, #0F172A)"

    st.markdown(f"""
    <div style="
        background: {bg};
        border: 1px solid {border_color};
        border-left: 4px solid {border_color};
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <div>
            <span style="font-size: 1rem; font-weight: 700; color: #E2E8F0;">{icon} {name}</span>
            <div style="color: #94A3B8; font-size: 0.78rem; margin-top: 0.1rem;">{description}</div>
        </div>
        <div>{status_html}</div>
    </div>
    """, unsafe_allow_html=True)


def agent_connector():
    """Render a visual connector arrow between agent cards."""
    st.markdown("""
    <div style="display: flex; justify-content: center; margin: -0.15rem 0;">
        <span style="color: #475569; font-size: 1rem;">↓</span>
    </div>
    """, unsafe_allow_html=True)
