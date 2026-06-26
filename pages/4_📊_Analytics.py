"""
Page 4: Market Intelligence (Analytics)
Visualizes the 50k job dataset with Plotly charts.
Provides personalized career recommendations.
"""

import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.analytics_service import (
    load_dataset,
    get_top_skills,
    get_highest_paying_skills,
    get_demand_by_location,
    get_demand_by_category,
    get_experience_distribution,
    get_trending_skills,
    get_salary_distribution,
    get_market_summary,
    get_user_eligibility_boost,
)
from services.gemini_service import generate_career_insights


# ── Page Config ──
st.set_page_config(
    page_title="Analytics — Jobs Engine",
    page_icon="📊",
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
    .analytics-header {
        background: linear-gradient(135deg, #10B981 0%, #06B6D4 50%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .analytics-sub {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .insight-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
    }
    .boost-badge {
        display: inline-block;
        background: linear-gradient(135deg, #064E3B, #065F46);
        color: #6EE7B7;
        padding: 6px 14px;
        border-radius: 12px;
        margin: 4px;
        font-size: 0.85rem;
        border: 1px solid #10B981;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme defaults ──
CHART_COLORS = [
    "#6366F1", "#8B5CF6", "#A78BFA", "#C084FC",
    "#06B6D4", "#22D3EE", "#67E8F9",
    "#10B981", "#34D399", "#6EE7B7",
    "#F59E0B", "#FBBF24", "#FDE68A",
    "#EF4444", "#F87171", "#FCA5A5",
]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#E2E8F0", family="Inter, sans-serif"),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(30,41,59,0.8)",
        bordercolor="#334155",
        borderwidth=1,
    ),
)


# ── Header ──
st.markdown('<p class="analytics-header">📊 Market Intelligence</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="analytics-sub">Explore market trends, salary insights, and in-demand skills '
    'from 50,000+ job postings to guide your career strategy.</p>',
    unsafe_allow_html=True,
)

# ── Load Dataset ──
with st.spinner("📦 Loading market intelligence data..."):
    df = load_dataset()
    summary = get_market_summary(df)

# ── Overview Metrics ──
m1, m2, m3, m4 = st.columns(4)
m1.metric("📋 Total Jobs Analyzed", f"{summary['total_jobs']:,}")
m2.metric("💰 Average Salary", f"${summary['avg_salary']:,}")
m3.metric("🏢 Companies", f"{summary['unique_companies']}")
m4.metric("📂 Categories", f"{summary['categories']}")

st.divider()

# ── Analytics Tabs ──
tab_skills, tab_salary, tab_location, tab_trends, tab_career = st.tabs([
    "🛠️ Top Skills",
    "💰 Salary Insights",
    "📍 Demand by Location",
    "📈 Trends",
    "🎯 Career Recommendations",
])


# ── Tab 1: Top Skills ──
with tab_skills:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Most In-Demand Skills")
        top_skills = get_top_skills(df, top_n=20)
        
        fig = px.bar(
            top_skills,
            x="count",
            y="skill",
            orientation="h",
            color="count",
            color_continuous_scale=["#312E81", "#4F46E5", "#818CF8", "#C7D2FE"],
            labels={"count": "Job Postings", "skill": ""},
        )
        fig.update_layout(
            **CHART_LAYOUT,
            height=600,
            title="Top 20 Most In-Demand Skills",
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            coloraxis_showscale=False,
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Appears in %{x:,} job postings<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Skill Frequency Table")
        st.dataframe(
            top_skills.rename(columns={
                "skill": "Skill",
                "count": "Job Postings",
                "percentage": "% of Jobs"
            }),
            use_container_width=True,
            hide_index=True,
        )
        
        st.write("")
        st.subheader("Experience Level Distribution")
        exp_dist = get_experience_distribution(df)
        
        fig_pie = px.pie(
            exp_dist,
            values="count",
            names="experience_level",
            color_discrete_sequence=CHART_COLORS,
            hole=0.45,
        )
        fig_pie.update_layout(
            **CHART_LAYOUT,
            height=350,
            title="Jobs by Experience Level",
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value:,} jobs<extra></extra>",
        )
        st.plotly_chart(fig_pie, use_container_width=True)


# ── Tab 2: Salary Insights ──
with tab_salary:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Highest Paying Skills")
        top_paying = get_highest_paying_skills(df, top_n=15)
        
        fig = px.bar(
            top_paying,
            x="avg_salary",
            y="skill",
            orientation="h",
            color="avg_salary",
            color_continuous_scale=["#064E3B", "#059669", "#10B981", "#6EE7B7"],
            labels={"avg_salary": "Average Salary ($)", "skill": ""},
        )
        fig.update_layout(
            **CHART_LAYOUT,
            height=550,
            title="Skills with Highest Average Salaries",
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            coloraxis_showscale=False,
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Avg Salary: $%{x:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Salary by Job Category")
        cat_data = get_demand_by_category(df)
        
        fig = px.bar(
            cat_data,
            x="category",
            y="avg_salary",
            color="job_count",
            color_continuous_scale=["#312E81", "#4F46E5", "#818CF8"],
            labels={
                "avg_salary": "Average Salary ($)",
                "category": "",
                "job_count": "Job Count",
            },
        )
        fig.update_layout(
            **CHART_LAYOUT,
            height=550,
            title="Average Salary by Category",
            xaxis=dict(tickangle=45),
            coloraxis_showscale=True,
        )
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Avg Salary: $%{y:,.0f}<extra></extra>"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Salary distribution histogram
    st.subheader("Salary Distribution")
    sal_data = get_salary_distribution(df)
    
    fig_hist = px.histogram(
        sal_data,
        x="avg_salary",
        color="experience_level",
        nbins=50,
        color_discrete_sequence=CHART_COLORS,
        labels={"avg_salary": "Average Salary ($)", "experience_level": "Experience"},
        barmode="overlay",
        opacity=0.7,
    )
    fig_hist.update_layout(
        **CHART_LAYOUT,
        height=400,
        title="Salary Distribution by Experience Level",
        xaxis=dict(tickformat="$,.0f"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)


# ── Tab 3: Demand by Location ──
with tab_location:
    st.subheader("Job Demand by Location")
    loc_data = get_demand_by_location(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            loc_data.head(15),
            x="job_count",
            y="location",
            orientation="h",
            color="avg_salary",
            color_continuous_scale=["#312E81", "#4F46E5", "#7C3AED", "#A78BFA"],
            labels={
                "job_count": "Number of Jobs",
                "location": "",
                "avg_salary": "Avg Salary ($)",
            },
        )
        fig.update_layout(
            **CHART_LAYOUT,
            height=550,
            title="Top 15 Locations by Job Count",
            yaxis=dict(autorange="reversed"),
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Jobs: %{x:,}<br>Avg Salary: $%{customdata[0]:,.0f}<extra></extra>",
            customdata=loc_data.head(15)[["avg_salary"]].values,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig_scatter = px.scatter(
            loc_data,
            x="job_count",
            y="avg_salary",
            text="location",
            size="job_count",
            color="avg_salary",
            color_continuous_scale=["#DC2626", "#F59E0B", "#10B981"],
            labels={
                "job_count": "Number of Jobs",
                "avg_salary": "Average Salary ($)",
            },
        )
        fig_scatter.update_layout(
            **CHART_LAYOUT,
            height=550,
            title="Location: Jobs vs Salary",
        )
        fig_scatter.update_traces(
            textposition="top center",
            textfont=dict(size=9, color="#94A3B8"),
            hovertemplate="<b>%{text}</b><br>Jobs: %{x:,}<br>Avg Salary: $%{y:,.0f}<extra></extra>",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Location data table
    with st.expander("📋 Full Location Data"):
        st.dataframe(
            loc_data.rename(columns={
                "location": "Location",
                "job_count": "Jobs",
                "avg_salary": "Avg Salary ($)",
            }),
            use_container_width=True,
            hide_index=True,
        )


# ── Tab 4: Trends ──
with tab_trends:
    st.subheader("Trending Skills (Growth in Recent 6 Months)")
    trending = get_trending_skills(df, months=6)
    
    if not trending.empty:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Color by positive/negative growth
            trending["color"] = trending["growth_pct"].apply(
                lambda x: "#10B981" if x > 0 else "#EF4444"
            )
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=trending["growth_pct"],
                y=trending["skill"],
                orientation="h",
                marker=dict(
                    color=trending["growth_pct"],
                    colorscale=[[0, "#EF4444"], [0.5, "#F59E0B"], [1, "#10B981"]],
                ),
                hovertemplate="<b>%{y}</b><br>Growth: %{x:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                **CHART_LAYOUT,
                height=550,
                title="Skill Demand Growth (%)",
                yaxis=dict(autorange="reversed"),
                xaxis=dict(title="Growth (%)"),
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Trending Skills Table")
            display_df = trending[["skill", "recent_mentions", "growth_pct"]].rename(
                columns={
                    "skill": "Skill",
                    "recent_mentions": "Recent Mentions",
                    "growth_pct": "Growth (%)",
                }
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Category demand over time
    st.subheader("Job Category Demand")
    cat_data = get_demand_by_category(df)
    
    fig_cat = px.treemap(
        cat_data,
        path=["category"],
        values="job_count",
        color="avg_salary",
        color_continuous_scale=["#312E81", "#4F46E5", "#10B981"],
        labels={"job_count": "Jobs", "avg_salary": "Avg Salary ($)"},
    )
    fig_cat.update_layout(
        **CHART_LAYOUT,
        height=400,
        title="Job Market by Category (Size = Job Count, Color = Avg Salary)",
    )
    st.plotly_chart(fig_cat, use_container_width=True)


# ── Tab 5: Career Recommendations ──
with tab_career:
    has_profile = "user_profile" in st.session_state
    
    if has_profile:
        profile = st.session_state["user_profile"]
        user_skills = profile.get("skills", [])
        
        st.subheader("🎯 Personalized Career Intelligence")
        st.markdown(f"Based on your **{len(user_skills)} skills**, here's how you can boost your career.")
        
        st.write("")
        
        # Eligibility Boost Analysis
        st.markdown("#### 📈 Skill Eligibility Boost")
        st.caption("Learning these skills would increase the number of jobs you're eligible for:")
        
        with st.spinner("Calculating eligibility boosts..."):
            boosts = get_user_eligibility_boost(user_skills, df)
        
        if boosts:
            for boost in boosts[:7]:
                col_skill, col_boost, col_bar = st.columns([2, 1, 4])
                with col_skill:
                    st.markdown(f"**{boost['skill']}**")
                with col_boost:
                    st.markdown(
                        f'<span class="boost-badge">+{boost["boost_pct"]}%</span>',
                        unsafe_allow_html=True,
                    )
                with col_bar:
                    st.progress(min(boost["boost_pct"] / 20, 1.0))
            
            st.write("")
            st.info(
                f"💡 **Example:** Learning **{boosts[0]['skill']}** increases your "
                f"job eligibility by **{boosts[0]['boost_pct']}%** "
                f"({boosts[0]['job_count']:,} additional job postings)."
            )
        else:
            st.success("🎉 Your skills already cover a broad range of the job market!")
        
        st.divider()
        
        # AI Career Insights
        st.markdown("#### 🤖 AI Career Insights")
        
        if st.button("Generate Personalized Insights", type="primary"):
            # Build market summary for context
            market_context = f"""
            - Total jobs analyzed: {summary['total_jobs']:,}
            - Average salary: ${summary['avg_salary']:,}
            - Top category: {summary['top_category']}
            - Top location: {summary['top_location']}
            - Top 5 in-demand skills: {', '.join(get_top_skills(df, 5)['skill'].tolist())}
            - Top 5 highest-paying skills: {', '.join(get_highest_paying_skills(df, 5)['skill'].tolist())}
            """
            
            if boosts:
                boost_context = "\n".join(
                    f"- Learning {b['skill']} increases eligibility by {b['boost_pct']}%"
                    for b in boosts[:5]
                )
                market_context += f"\n\nEligibility boost opportunities:\n{boost_context}"
            
            with st.spinner("🧠 Generating personalized career insights..."):
                try:
                    insights = generate_career_insights(user_skills, market_context)
                    st.session_state["career_insights"] = insights
                except Exception as e:
                    st.error(f"❌ Failed to generate insights: {str(e)}")
        
        if "career_insights" in st.session_state:
            st.markdown(st.session_state["career_insights"])
    
    else:
        st.warning(
            "⚠️ **Upload your resume** to get personalized career recommendations. "
            "Without a profile, we can only show general market data."
        )
        
        st.subheader("📊 General Market Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🏆 Top Category", summary["top_category"])
            st.metric("📍 Top Location", summary["top_location"])
        with col2:
            st.metric("💰 Median Salary", f"${summary['median_salary']:,}")
            st.metric("📊 Salary Range", summary["salary_range"])
        
        st.write("")
        top_5 = get_top_skills(df, 5)
        st.markdown("**Top 5 In-Demand Skills:**")
        for _, row in top_5.iterrows():
            st.markdown(f"- **{row['skill']}** — {row['count']:,} job postings ({row['percentage']}%)")
