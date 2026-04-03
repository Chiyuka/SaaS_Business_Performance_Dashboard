"""
app.py
------
Streamlit UI for the SaaS Business Performance Dashboard.
All data logic lives in data.py — this file is presentation only.

Run with:
    streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data import (
    generate_dataset,
    compute_kpis,
    compute_revenue_trend,
    compute_geo_distribution,
    compute_tier_revenue,
    run_health_checks,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main { background: #0d1117; }

  .kpi-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 20px 24px; text-align: center;
  }
  .kpi-label {
    font-size: 11px; font-weight: 600; letter-spacing: 1.4px;
    text-transform: uppercase; color: #8b949e; margin-bottom: 8px;
  }
  .kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem; color: #e6edf3; line-height: 1.1;
  }
  .kpi-delta     { font-size: 12px; margin-top: 6px; color: #3fb950; }
  .kpi-delta-bad { font-size: 12px; margin-top: 6px; color: #f85149; }

  .section-title {
    font-family: 'DM Serif Display', serif; font-size: 1.35rem;
    color: #e6edf3; margin: 8px 0 4px 0;
    border-left: 3px solid #388bfd; padding-left: 12px;
  }

  .badge-ok   { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950;
                border-radius:20px; padding:2px 12px; font-size:12px; font-weight:600; }
  .badge-warn { background:#3a2a1a; color:#d29922; border:1px solid #d29922;
                border-radius:20px; padding:2px 12px; font-size:12px; font-weight:600; }
  .badge-err  { background:#3a1a1a; color:#f85149; border:1px solid #f85149;
                border-radius:20px; padding:2px 12px; font-size:12px; font-weight:600; }

  .health-row {
    background: #161b22; border: 1px solid #30363d; border-radius: 10px;
    padding: 14px 20px; margin-bottom: 10px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .health-metric { color: #8b949e; font-size: 13px; }
  .health-detail { color: #e6edf3; font-size: 13px; font-weight: 500; }

  div[data-testid="stMetricValue"] > div { color: #e6edf3 !important; }
  .stSelectbox label, .stSlider label   { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)


# ── Load raw data (cached) ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return generate_dataset()

df_raw = load_data()


# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")

    tiers_all   = ["All"] + sorted(df_raw["Subscription Tier"].dropna().unique().tolist())
    sel_tier    = st.selectbox("Subscription Tier", tiers_all)

    countries_all = ["All"] + sorted(df_raw["Country"].dropna().unique().tolist())
    sel_country   = st.selectbox("Country", countries_all)

    show_churned = st.checkbox("Include churned users in map/bar chart", value=False)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("Mock dataset · 1 200 synthetic SaaS subscribers · Jan 2023 – Jan 2024")

# Apply filters
df = df_raw.copy()
if sel_tier    != "All": df = df[df["Subscription Tier"] == sel_tier]
if sel_country != "All": df = df[df["Country"]           == sel_country]
df_map = df if show_churned else df[df["Churn Date"].isna()]


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='font-family:DM Serif Display,serif;color:#e6edf3;margin-bottom:4px'>"
    "SaaS Business Performance Dashboard</h1>"
    "<p style='color:#8b949e;font-size:14px;margin-top:0'>"
    "Real-time KPI tracking · subscription analytics · data quality monitoring</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ── KPI cards ─────────────────────────────────────────────────────────────────
kpis = compute_kpis(df)
mrr, churn_rate, arpu = kpis["mrr"], kpis["churn_rate"], kpis["arpu"]
active_n, churned_n   = kpis["active_count"], kpis["churned_count"]

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Monthly Recurring Revenue</div>
      <div class="kpi-value">${mrr:,.0f}</div>
      <div class="kpi-delta">▲ MRR (active subs)</div>
    </div>""", unsafe_allow_html=True)

with k2:
    delta_cls = "kpi-delta-bad" if churn_rate > 10 else "kpi-delta"
    arrow     = "▲ above 10 % threshold" if churn_rate > 10 else "▼ within healthy range"
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Churn Rate</div>
      <div class="kpi-value">{churn_rate:.1f}%</div>
      <div class="{delta_cls}">{arrow}</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Avg Revenue Per User</div>
      <div class="kpi-value">${arpu:.2f}</div>
      <div class="kpi-delta">per active subscriber / mo</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">Active Subscribers</div>
      <div class="kpi-value">{active_n:,}</div>
      <div class="kpi-delta-bad">{churned_n} churned</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Chart 1 – Revenue Trend ───────────────────────────────────────────────────
st.markdown('<p class="section-title">📈 Revenue Trend (MRR over time)</p>', unsafe_allow_html=True)

trend_df = compute_revenue_trend(df)
fig_line  = go.Figure()
fig_line.add_trace(go.Scatter(
    x=trend_df["Month"], y=trend_df["MRR"],
    mode="lines+markers",
    line=dict(color="#388bfd", width=2.5),
    marker=dict(size=6, color="#388bfd"),
    fill="tozeroy", fillcolor="rgba(56,139,253,0.10)",
    name="MRR",
))
fig_line.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8b949e", family="DM Sans"),
    xaxis=dict(showgrid=False, color="#30363d", tickcolor="#30363d"),
    yaxis=dict(showgrid=True, gridcolor="#21262d", tickprefix="$"),
    margin=dict(l=0, r=0, t=10, b=0), height=300,
)
st.plotly_chart(fig_line, use_container_width=True)


# ── Charts 2 & 3 – Map + Bar ──────────────────────────────────────────────────
col_map, col_bar = st.columns([1.4, 1], gap="large")

with col_map:
    st.markdown('<p class="section-title">🌍 Active Users by Country</p>', unsafe_allow_html=True)
    geo     = compute_geo_distribution(df_map)
    fig_map = px.choropleth(
        geo, locations="Country", locationmode="country names",
        color="Users", color_continuous_scale="Blues",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False,
                 showcoastlines=True, coastlinecolor="#30363d",
                 landcolor="#161b22", oceancolor="#0d1117", showocean=True),
        margin=dict(l=0, r=0, t=0, b=0), height=320,
        coloraxis_colorbar=dict(tickfont=dict(color="#8b949e")),
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_bar:
    st.markdown('<p class="section-title">📊 Revenue by Subscription Tier</p>', unsafe_allow_html=True)
    tier_df     = compute_tier_revenue(df_map)
    TIER_COLORS = {"Starter": "#3fb950", "Professional": "#388bfd", "Enterprise": "#d2a8ff"}
    colors      = [TIER_COLORS.get(t, "#8b949e") for t in tier_df["Subscription Tier"]]

    fig_bar = go.Figure(go.Bar(
        x=tier_df["Monthly Revenue"], y=tier_df["Subscription Tier"],
        orientation="h", marker_color=colors,
        text=[f"${v:,.0f}" for v in tier_df["Monthly Revenue"]],
        textposition="outside", textfont=dict(color="#e6edf3", size=12),
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e", family="DM Sans"),
        xaxis=dict(showgrid=True, gridcolor="#21262d", tickprefix="$", color="#30363d"),
        yaxis=dict(showgrid=False, color="#8b949e"),
        margin=dict(l=0, r=80, t=10, b=0), height=320,
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ── Data Health ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-title">🩺 Data Health Check</p>', unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8b949e;font-size:13px;margin-top:-4px'>"
    "Automated quality checks on the raw dataset — catch issues before they distort KPIs.</p>",
    unsafe_allow_html=True,
)

health       = run_health_checks(df_raw)
null_counts  = health["null_counts"]
total_nulls  = health["total_nulls"]
dup_count    = health["dup_count"]
total_rows   = health["total_rows"]
completeness = health["completeness"]

h1, h2, h3 = st.columns(3)

with h1:
    badge = "badge-ok" if total_nulls == 0 else ("badge-warn" if total_nulls < 20 else "badge-err")
    label = "✓ Clean" if total_nulls == 0 else f"⚠ {total_nulls} nulls found"
    st.markdown(f"""
    <div class="health-row">
      <div>
        <div class="health-metric">Null Values</div>
        <div class="health-detail">Across all columns</div>
      </div>
      <span class="{badge}">{label}</span>
    </div>""", unsafe_allow_html=True)
    if total_nulls > 0:
        for col, cnt in null_counts[null_counts > 0].items():
            st.markdown(
                f"<span style='color:#8b949e;font-size:12px;padding-left:8px'>"
                f"↳ <b style='color:#e6edf3'>{col}</b>: {cnt} null(s)</span><br>",
                unsafe_allow_html=True,
            )

with h2:
    badge2 = "badge-ok" if dup_count == 0 else ("badge-warn" if dup_count < 10 else "badge-err")
    label2 = "✓ No duplicates" if dup_count == 0 else f"⚠ {dup_count} duplicate rows"
    st.markdown(f"""
    <div class="health-row">
      <div>
        <div class="health-metric">Duplicate Rows</div>
        <div class="health-detail">{total_rows:,} total rows inspected</div>
      </div>
      <span class="{badge2}">{label2}</span>
    </div>""", unsafe_allow_html=True)

with h3:
    badge3 = "badge-ok" if completeness >= 99 else ("badge-warn" if completeness >= 95 else "badge-err")
    st.markdown(f"""
    <div class="health-row">
      <div>
        <div class="health-metric">Dataset Completeness</div>
        <div class="health-detail">{health['total_cols']} columns · {total_rows:,} rows</div>
      </div>
      <span class="{badge3}">{completeness}%</span>
    </div>""", unsafe_allow_html=True)


# ── Raw data preview ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗂 Raw Data Preview (first 100 rows)"):
    st.dataframe(df_raw.head(100), use_container_width=True, height=340)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<hr style='border-color:#21262d'>"
    "<p style='text-align:center;color:#30363d;font-size:12px'>"
    "SaaS Performance Dashboard · built with Streamlit + Plotly · mock data only</p>",
    unsafe_allow_html=True,
)