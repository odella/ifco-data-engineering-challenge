"""
IFCO Data Engineering Challenge — Test 6: Executive Sales Dashboard
====================================================================
Interactive Streamlit + Plotly dashboard that answers all three
questions set by the challenge (Test 6), plus bonus KPI and trend analysis.

Reads pre-processed CSVs exported from the Databricks Gold/Silver tables.
"""

import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 0. PAGE CONFIG & GLOBAL PLOTLY THEME
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IFCO Sales Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Register a fully custom Plotly template ──────────────────────────────────
# This is the reliable way to guarantee ALL text (axes, legends, titles,
# annotations, hover labels, colorbars) is light on dark backgrounds.
BG       = "#1a2030"      # chart area & paper
GRID     = "#2a3347"
TEXT     = "#e2e8f0"      # all chart text — bright enough for dark BG
TITLE_C  = "#e2e8f0"      # chart titles — same as TEXT for maximum contrast

_dark = pio.templates["plotly_dark"]
custom_template = pio.templates["plotly_dark"]

pio.templates["ifco_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(color=TEXT, size=12),
        title=dict(font=dict(color=TITLE_C, size=15), x=0.05),
        legend=dict(
            font=dict(color=TEXT, size=11),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=GRID,
        ),
        xaxis=dict(
            gridcolor=GRID, zerolinecolor=GRID,
            tickfont=dict(color=TEXT),
            title=dict(font=dict(color=TEXT)),
            linecolor=GRID,
        ),
        yaxis=dict(
            gridcolor=GRID, zerolinecolor=GRID,
            tickfont=dict(color=TEXT),
            title=dict(font=dict(color=TEXT)),
            linecolor=GRID,
        ),
        polar=dict(
            bgcolor=BG,
            angularaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TEXT)),
            radialaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TEXT)),
        ),
        coloraxis=dict(
            colorbar=dict(
                tickfont=dict(color=TEXT),
                title=dict(font=dict(color=TEXT)),
                outlinecolor=GRID,
            )
        ),
        geo=dict(bgcolor=BG, lakecolor=GRID, landcolor="#2d3748"),
        hoverlabel=dict(bgcolor="#2d3748", font=dict(color=TEXT)),
        annotationdefaults=dict(font=dict(color=TEXT)),
    )
)
pio.templates.default = "ifco_dark"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #2a3347; }

    /* Hide the white Streamlit top toolbar/header */
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { background: transparent !important; height: 0 !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }

    /* Sidebar text — labels, captions, markdown */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] span:not([data-baseweb]) {
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

    /* Main page title visibility */
    h1, h2, h3, h4 { color: #e2e8f0 !important; }

    /* st.caption visibility */
    [data-testid="stCaptionContainer"] p,
    .stCaption, small { color: #94a3b8 !important; }

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a2030 0%, #1e2a3d 100%);
        border: 1px solid #2a3347;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-value { font-size: 2.1rem; font-weight: 700; color: #60a5fa; margin: 0; }
    .kpi-label { font-size: 0.72rem; color: #6b7280; text-transform: uppercase;
                 letter-spacing: 0.1em; margin-top: 4px; }
    .kpi-delta { font-size: 0.8rem; color: #34d399; margin-top: 2px; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #60a5fa 0%, #93c5fd 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 1.3rem; font-weight: 700; margin-bottom: 0.15rem;
        padding-left: 4px;
    }
    .section-sub { color: #94a3b8; font-size: 0.82rem; margin-bottom: 1rem; padding-left: 4px; }

    hr { border-color: #1f2937 !important; margin: 1.8rem 0; }
    .stPlotlyChart { border-radius: 10px; overflow: hidden;
                     border: 1px solid #1f2937; }
    [data-testid="stExpander"] { background: #161b22; border: 1px solid #1f2937; border-radius: 8px; }

    /* Streamlit tabs — make unselected tabs clearly readable */
    button[data-baseweb="tab"] { color: #9ca3af !important; font-weight: 500; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #e2e8f0 !important; font-weight: 700; }
    [data-testid="stTabBar"] { border-bottom: 1px solid #2a3347; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data"
)

@st.cache_data
def load_data():
    orders      = pd.read_csv(os.path.join(DATA_DIR, "silver_orders.csv"), parse_dates=["date"], dayfirst=True)
    crate_dist  = pd.read_csv(os.path.join(DATA_DIR, "gold_crate_distribution.csv"))
    commissions = pd.read_csv(os.path.join(DATA_DIR, "gold_sales_commissions.csv"))
    companies   = pd.read_csv(os.path.join(DATA_DIR, "gold_companies_salesowners.csv"))
    invoicing   = pd.read_csv(os.path.join(DATA_DIR, "silver_invoicing.csv"))
    return orders, crate_dist, commissions, companies, invoicing

orders, crate_dist, commissions, companies, invoicing = load_data()

def explode_owners(df):
    rows = []
    for _, r in df.iterrows():
        for i, o in enumerate([x.strip() for x in str(r["salesowners"]).split(",")]):
            rows.append({**r.to_dict(), "salesowner": o, "owner_rank": i})
    return pd.DataFrame(rows)

orders_exp  = explode_owners(orders)
plastic_orders = orders[orders["crate_type"] == "Plastic"].copy()
plastic_exp    = orders_exp[orders_exp["crate_type"] == "Plastic"].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HELPER — apply consistent dark styling to any go.Figure
# ─────────────────────────────────────────────────────────────────────────────
def dark(fig, height=None, margin=None, legend_h=False):
    """Apply unified dark-mode overrides to any Plotly figure."""
    leg = dict(font=dict(color=TEXT, size=11), bgcolor="rgba(0,0,0,0)")
    if legend_h:
        leg.update(orientation="h", y=-0.18)
    upd = dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TEXT, size=12),
        title_font=dict(color=TITLE_C, size=16),
        title_x=0.05,
        legend=leg,
        margin=margin or dict(t=70, b=45, l=20, r=20),
    )
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    # Force all axis text to be light too
    fig.update_xaxes(tickfont_color=TEXT, title_font_color=TEXT, gridcolor=GRID, zerolinecolor=GRID)
    fig.update_yaxes(tickfont_color=TEXT, title_font_color=TEXT, gridcolor=GRID, zerolinecolor=GRID)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. SIDEBAR — GLOBAL FILTERS
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.markdown("""
        <div style="padding: 12px 0 8px 0; text-align: center;">
            <p style="font-size: 1.5rem; font-weight: 700; color: #e2e8f0;
                      margin: 0; letter-spacing: -0.02em;">📦 IFCO</p>
            <p style="font-size: 0.7rem; color: #6b7280; margin: 2px 0 0 0;
                      letter-spacing: 0.08em; text-transform: uppercase;">Sales Analytics</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception:
        st.markdown("## 📦 IFCO")
    st.markdown("---")
    st.markdown("### 🔍 Global Filters")

    all_crate_types = sorted(orders["crate_type"].dropna().unique())
    sel_crates = st.multiselect("Crate Types", all_crate_types, default=all_crate_types)

    min_date = orders["date"].min().date()
    max_date = orders["date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date),
                               min_value=min_date, max_value=max_date)

    st.markdown("---")
    st.caption("IFCO Data Engineering Challenge\nTest 6 — Executive Dashboard\nStreamlit + Plotly")

# Apply global filters
if len(date_range) == 2:
    d_start = pd.Timestamp(date_range[0])
    d_end   = pd.Timestamp(date_range[1])
else:
    d_start = orders["date"].min()
    d_end   = orders["date"].max()

filt_orders = orders[
    orders["crate_type"].isin(sel_crates) &
    orders["date"].between(d_start, d_end)
].copy()

filt_exp = orders_exp[
    orders_exp["crate_type"].isin(sel_crates) &
    orders_exp["date"].between(d_start, d_end)
].copy()

filt_plastic = plastic_orders[plastic_orders["date"].between(d_start, d_end)].copy()

filt_plastic_exp = plastic_exp[
    plastic_exp["date"].between(d_start, d_end)
].copy()


# ─────────────────────────────────────────────────────────────────────────────
# 3. HEADER & TOP KPIs
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 📦 IFCO Sales Analytics Dashboard")
st.markdown('<p style="color:#94a3b8; font-size:0.95rem; margin-top:-0.5rem;">IFCO Sales Analytics &middot; Orders &middot; Commissions &middot; <em>Test 6 &mdash; Executive View</em></p>', unsafe_allow_html=True)

total_orders     = len(filt_orders)
total_plastic    = len(filt_plastic)
plastic_pct      = total_plastic / total_orders * 100 if total_orders else 0
total_commission = commissions["commission_euros"].sum()
active_owners    = orders_exp["salesowner"].nunique()
active_companies = orders["company_name"].nunique()

kpi_cols = st.columns(5)
for col, val, label, delta in zip(
    kpi_cols,
    [f"{total_orders:,}", f"{plastic_pct:.1f}%", f"€{total_commission:,.2f}",
     str(active_owners), str(active_companies)],
    ["Total Orders", "Plastic Share", "Total Commissions", "Active Sales Owners", "Companies Served"],
    ["", "of total orders", "all time", "", ""]
):
    with col:
        d_html = f'<p class="kpi-delta">{delta}</p>' if delta else ""
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{val}</p>
            <p class="kpi-label">{label}</p>
            {d_html}
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 4. SECTION A — CRATE TYPE DISTRIBUTION  (Challenge Q1)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📊 A · Distribution of Orders by Crate Type</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Challenge Q1 — How are orders distributed across crate types?</p>', unsafe_allow_html=True)

CRATE_COLORS = {"Plastic": "#3b82f6", "Wood": "#22c55e", "Metal": "#f59e0b"}

col_a1, col_a2 = st.columns(2)

with col_a1:
    overall = filt_orders["crate_type"].value_counts().reset_index()
    overall.columns = ["crate_type", "count"]
    fig_pie = px.pie(
        overall, values="count", names="crate_type",
        color="crate_type", color_discrete_map=CRATE_COLORS,
        hole=0.55, title="Overall Crate Type Split"
    )
    fig_pie.update_traces(
        textinfo="percent+label",
        textfont=dict(color=TEXT, size=13),
        pull=[0.03] * len(overall),
        marker=dict(line=dict(color="#0d1117", width=2))
    )
    dark(fig_pie, legend_h=True, margin=dict(t=55, b=55, l=20, r=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_a2:
    monthly = filt_orders.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_cnt = monthly.groupby(["month", "crate_type"]).size().reset_index(name="count")
    fig_bar = px.bar(
        monthly_cnt, x="month", y="count", color="crate_type",
        color_discrete_map=CRATE_COLORS,
        barmode="stack",
        title="Monthly Orders by Crate Type",
        labels={"month": "", "count": "Orders", "crate_type": "Type"}
    )
    dark(fig_bar, legend_h=True, margin=dict(t=55, b=65, l=50, r=20))
    fig_bar.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

# Heatmap company × crate type
st.markdown('<p class="section-sub">Company × Crate Type Heatmap</p>', unsafe_allow_html=True)
pivot = crate_dist.pivot_table(index="company_name", columns="crate_type",
                                values="total_crates", fill_value=0)
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).head(20).index]
fig_heat = px.imshow(
    pivot, text_auto=True, aspect="auto",
    color_continuous_scale="Blues",
    title="Top 20 Companies — Orders per Crate Type",
    labels=dict(x="Crate Type", y="Company", color="Orders")
)
fig_heat.update_traces(textfont=dict(size=14), texttemplate="%{z}")
dark(fig_heat, margin=dict(t=70, b=20, l=180, r=20))
fig_heat.update_coloraxes(
    colorbar=dict(tickfont=dict(color=TEXT), title=dict(font=dict(color=TEXT), text="Orders"))
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 5. SECTION B — PLASTIC TRAINING NEEDS  (Challenge Q2)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🎯 B · Who Needs Plastic Crate Training? (Last 12 Months)</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Challenge Q2 — Sales owners with lowest plastic crate conversion rate in last 12 months</p>', unsafe_allow_html=True)

cutoff_12m = orders["date"].max() - pd.DateOffset(months=12)
last12_exp = orders_exp[orders_exp["date"] >= cutoff_12m].copy()

total_per_owner   = last12_exp.groupby("salesowner")["order_id"].nunique().rename("total")
plastic_per_owner = (
    last12_exp[last12_exp["crate_type"] == "Plastic"]
    .groupby("salesowner")["order_id"].nunique().rename("plastic")
)
training_df = pd.DataFrame({"total": total_per_owner, "plastic": plastic_per_owner}).fillna(0)
training_df["non_plastic"]  = training_df["total"] - training_df["plastic"]
training_df["plastic_rate"] = training_df["plastic"] / training_df["total"] * 100
training_df = training_df[training_df["total"] >= 1].sort_values("plastic_rate").reset_index()

col_b1, col_b2 = st.columns([3, 2])

with col_b1:
    fig_train = go.Figure()
    fig_train.add_bar(y=training_df["salesowner"], x=training_df["plastic"],
                      name="Plastic Orders", orientation="h", marker_color="#3b82f6")
    fig_train.add_bar(y=training_df["salesowner"], x=training_df["non_plastic"],
                      name="Other Types", orientation="h",
                      marker_color="#2a3347")
    dark(fig_train, legend_h=True, margin=dict(t=70, b=65, l=170, r=20))
    fig_train.update_layout(
        barmode="stack",
        title=dict(text="Orders by crate type (last 12 months) — sorted by plastic rate",
                   font=dict(color=TEXT, size=16))
    )
    fig_train.update_xaxes(title="Orders")
    st.plotly_chart(fig_train, use_container_width=True)

with col_b2:
    fig_rate = px.bar(
        training_df, y="salesowner", x="plastic_rate", orientation="h",
        color="plastic_rate",
        color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
        range_color=[0, 100],
        title="Plastic Conversion Rate (%)",
        labels={"plastic_rate": "Rate %", "salesowner": ""}
    )
    avg_rate = training_df["plastic_rate"].mean()
    fig_rate.add_vline(x=avg_rate, line_dash="dash", line_color="#6b7280",
                       annotation_text=f"avg {avg_rate:.0f}%",
                       annotation_font_color=TEXT)
    dark(fig_rate, margin=dict(t=70, b=30, l=165, r=20))
    fig_rate.update_coloraxes(showscale=False)
    fig_rate.update_xaxes(range=[0, 105])
    st.plotly_chart(fig_rate, use_container_width=True)

# Training callout cards
st.markdown('<p class="section-sub">Highest Training Priority (lowest plastic %):</p>', unsafe_allow_html=True)
bottom3 = training_df.head(3)
tcols = st.columns(3)
for i, (_, row) in enumerate(bottom3.iterrows()):
    with tcols[i]:
        rate  = row["plastic_rate"]
        color = "#ef4444" if rate < 20 else "#f59e0b" if rate < 40 else "#22c55e"
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}60">
            <p class="kpi-value" style="color:{color}">{rate:.1f}%</p>
            <p class="kpi-label">{row['salesowner']}</p>
            <p class="kpi-delta" style="color:#6b7280">{int(row['plastic'])}/{int(row['total'])} plastic orders</p>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 6. SECTION C — ROLLING 3-MONTH TOP 5  (Challenge Q3)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🏆 C · Monthly Top 5 Performers — Plastic (Rolling 3-Month Window)</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Challenge Q3 — Top 5 plastic crate sellers per month on a rolling 3-month evaluation window</p>', unsafe_allow_html=True)

plastic_exp["year_month"] = plastic_exp["date"].dt.to_period("M")

# GUARANTEE a perfectly continuous timeline from the first to the last order date.
# If we only use unique() dates from plastic_exp, any month where ZERO plastic crates 
# were sold company-wide will be skipped in the loop, breaking the rolling sum and causing false 0s.
all_months = pd.period_range(
    start=orders["date"].min().to_period("M"),
    end=orders["date"].max().to_period("M"),
    freq="M"
)

# Calculate rolling 3-month performance for all owners
all_rolling_rows = []
for month in all_months:
    mask = (plastic_exp["year_month"] >= month - 2) & (plastic_exp["year_month"] <= month)
    counts = (plastic_exp[mask]
              .groupby("salesowner")["order_id"].nunique()
              .reset_index(name="plastic_orders"))

    # Sort descending by orders, ascending by name to break ties predictably
    counts = counts.sort_values(["plastic_orders", "salesowner"], ascending=[False, True])
    
    # Calculate mathematics rank: dense assigns consecutive numbers.
    # Ex: 1st=10 boxes, 2nd=10 boxes, 3rd=9 boxes -> Ranks: 1, 1, 2.
    # Thus, a "second best seller" is ALWAYS firmly on line 2, never pushed down.
    counts["rank"] = counts["plastic_orders"].rank(method="dense", ascending=False).astype(int)
    counts["rank_display"] = counts["rank"]
    
    counts["month"] = str(month)
    all_rolling_rows.append(counts)

full_rolling_df = pd.concat(all_rolling_rows, ignore_index=True)

# Cutoff exactly at geometric rank=5 to enforce exactly 5 owners plotted per month
rolling_df = full_rolling_df[full_rolling_df["rank"] <= 5].copy()

# ── Prepare Heatmap Data ─────────────────────────────────────────────────────
# The people who EVER hit Top 5:
all_top_owners = sorted(rolling_df["salesowner"].unique())
PALETTE = px.colors.qualitative.Plotly + px.colors.qualitative.Safe
color_map = {o: PALETTE[i % len(PALETTE)] for i, o in enumerate(all_top_owners)}

# For the heatmap, get their FULL history (showing true orders even when not in top 5)
heatmap_data = full_rolling_df[full_rolling_df["salesowner"].isin(all_top_owners)].copy()

# Pivot: rows=month, cols=owner (fill 0 if they genuinely had no orders)
pivot_full = heatmap_data.pivot_table(
    index="month", columns="salesowner", values="plastic_orders", fill_value=0
)

# Generate COMPLETE monthly range (min → max of ALL orders, not just plastic)
full_month_range = pd.period_range(
    start=orders["date"].min().to_period("M"),
    end=orders["date"].max().to_period("M"),
    freq="M"
)
all_month_strs = [str(m) for m in full_month_range]
pivot_full = pivot_full.reindex(all_month_strs, fill_value=0)

# ── Viz 1: Bump chart — rank trajectory over time ────────────────────────────
bump_df = rolling_df.copy()
all_months_str = [str(m) for m in all_months]

fig_bump = go.Figure()

for owner in all_top_owners:
    owner_data = bump_df[bump_df["salesowner"] == owner].sort_values("month")
    rank_by_month   = dict(zip(owner_data["month"], owner_data["rank"]))
    display_by_month = dict(zip(owner_data["month"], owner_data["rank_display"]))
    orders_by_month = dict(zip(owner_data["month"], owner_data["plastic_orders"]))
    y_ranks  = [-rank_by_month[m] if m in rank_by_month else None for m in all_months_str]
    # Store rank text formatting but only use it if Y is not None
    hover_texts = [
        f"<b>{owner}</b> — Rank #{display_by_month[m]} ({orders_by_month[m]} orders)"
        if m in rank_by_month else ""
        for m in all_months_str
    ]
    # For hovertemplate, only output text if customdata has something
    fig_bump.add_scatter(
        x=all_months_str, y=y_ranks,
        mode="lines+markers",
        name=owner,
        line=dict(color=color_map.get(owner, "#60a5fa"), width=3),
        marker=dict(size=9, color=color_map.get(owner, "#60a5fa"),
                    line=dict(color="#0d1117", width=1.5)),
        customdata=hover_texts,
        hovertemplate="%{customdata}<span style='display:none'>%{y}</span><extra></extra>",
        connectgaps=False,
        showlegend=True,
    )

# Increased top margin to 120 so there is plenty of room for both title and legend
dark(fig_bump, height=430, legend_h=False, margin=dict(t=120, b=20, l=60, r=20))
fig_bump.update_layout(
    title=dict(
        text="Rolling 3-Month RANKING (Running Sum) — Top 5 Performers by Month",
        font=dict(color=TEXT, size=16),
        y=0.95, yref="container", yanchor="top"
    ),
    dragmode="pan",
    hovermode="x",           # Replaced 'x unified' with individual 'x' coordinates
    hoverlabel=dict(
        bgcolor="#1f2937",
        font_size=12,
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.05, # Legend sits right above the plot, safely below the title
        xanchor="center", x=0.5,
        title_text="",
    )
)
fig_bump.update_xaxes(
    showspikes=True,
    spikemode="across",      # Draws a vertical guide line across all ranks for the hovered month
    spikedash="solid",
    spikecolor="#4b5563",
    spikethickness=1,
)
fig_bump.update_yaxes(
    tickvals=[-1, -2, -3, -4, -5],
    ticktext=["🥇 #1", "🥈 #2", "🥉 #3", "  #4", "  #5"],
    title="Rank in rolling window",
    range=[-5.4, -0.6],  # STRICTLY limit Y-axis to 5
    dtick=1, showgrid=True,
    fixedrange=True,
)

# Show last 15 months by default, with a native rangeslider for horizontal scrolling
visible_window = 15
x_start = all_months_str[-visible_window] if len(all_months_str) > visible_window else all_months_str[0]
x_end = all_months_str[-1]

fig_bump.update_xaxes(
    tickangle=-45, title_text="",
    range=[x_start, x_end],
    rangeslider=dict(visible=True, thickness=0.06, bgcolor="#1a2030", bordercolor="#374151", borderwidth=1),
)

st.plotly_chart(fig_bump, use_container_width=True)

# ── Viz 2: Heatmap — The exact data behind the bump chart ────────────────────
st.markdown('<p class="section-sub" style="margin-top: 1rem;">'
            'Heat Map (Running Sum of Orders in Trailing 3-Month Window)</p>', unsafe_allow_html=True)

fig_heat = px.imshow(
    pivot_full.T,  # Transpose so owners are on Y-axis and months are on X-axis
    color_continuous_scale="Blues",
    aspect="auto",
    labels=dict(x="Month", y="Sales Owner", color="Total Orders"),
    text_auto=True,
)
dark(fig_heat, height=max(300, len(all_top_owners) * 35))
fig_heat.update_xaxes(tickangle=45, dtick="M6", title_text="Month")
fig_heat.update_yaxes(title_text="Sales Owner")
fig_heat.update_traces(
    hovertemplate="Sales Owner: %{y}<br>Month: %{x}<br>Orders (T3M): %{z}<extra></extra>"
)
fig_heat.update_layout(
    plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
    margin=dict(t=20, b=50, l=150, r=20),
    title_text="",  # Explicitly set title to empty string instead of None
    annotations=[]  # Nuke any rogue annotations created by px.imshow that say 'undefined'
)
fig_heat.update_coloraxes(colorbar=dict(thickness=12, len=0.8, x=1.02, title="Orders"))
st.plotly_chart(fig_heat, use_container_width=True)

# ── Viz 2: Medal table for the most recent rolling window ────────────────────
st.markdown('<p class="section-sub">Current Top 5 — Most Recent Rolling Window</p>', unsafe_allow_html=True)
latest_month = sorted(rolling_df["month"].unique())[-1]
top5_latest = rolling_df[rolling_df["month"] == latest_month].sort_values("rank")

medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
medal_cols = st.columns(min(5, len(top5_latest)))
for col, (_, row) in zip(medal_cols, top5_latest.iterrows()):
    with col:
        medal = medals[int(row["rank"]) - 1]
        clr = {"🥇":"#f59e0b","🥈":"#94a3b8","🥉":"#b45309"}.get(medal, "#3b82f6")
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{clr}50">
            <p class="kpi-value" style="color:{clr};font-size:1.6rem">{medal}</p>
            <p class="kpi-label">{row['salesowner']}</p>
            <p class="kpi-delta">{int(row['plastic_orders'])} orders · window ending {latest_month}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)



st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 7. SECTION D — COMMISSIONS LEADERBOARD  (Bonus)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">💰 D · Sales Commissions Leaderboard</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Bonus — Full commission breakdown from Test 4</p>', unsafe_allow_html=True)

col_d1, col_d2 = st.columns([2, 1])

with col_d1:
    fig_comm = px.bar(
        commissions.sort_values("commission_euros"),
        x="commission_euros", y="salesowner_name", orientation="h",
        text="commission_euros",
        color="commission_euros",
        color_continuous_scale=["#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd"],
        labels={"commission_euros": "Commission (€)", "salesowner_name": ""},
        title="Total Commissions per Sales Owner (all time)"
    )
    fig_comm.update_traces(
        texttemplate="€%{text:,.2f}", textposition="outside",
        textfont=dict(color=TEXT, size=11)
    )
    dark(fig_comm, margin=dict(t=55, b=20, l=165, r=110))
    fig_comm.update_coloraxes(showscale=False)
    st.plotly_chart(fig_comm, use_container_width=True)

with col_d2:
    fig_donut = px.pie(
        commissions, values="commission_euros", names="salesowner_name",
        hole=0.6, title="Commission Share",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig_donut.update_traces(
        textinfo="none",
        marker=dict(line=dict(color="#0d1117", width=1.5))
    )
    dark(fig_donut, legend_h=False, margin=dict(t=55, b=20, l=10, r=10))
    fig_donut.update_layout(
        legend=dict(font=dict(color=TEXT, size=10), orientation="v")
    )
    total_comm = commissions["commission_euros"].sum()
    fig_donut.add_annotation(
        text=f"€{total_comm:,.0f}", x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#60a5fa", family="Inter"),
        xref="paper", yref="paper"
    )
    st.plotly_chart(fig_donut, use_container_width=True)



# Calculate Commission per Order and its deviation from the mean
orders_per_owner = orders_exp.groupby("salesowner")["order_id"].nunique().reset_index(name="total_orders")
comm_merged = pd.merge(commissions, orders_per_owner, left_on="salesowner_name", right_on="salesowner", how="left")
comm_merged["commission_per_order"] = comm_merged["commission_euros"] / comm_merged["total_orders"]
mean_cpo = comm_merged["commission_per_order"].mean()
comm_merged["cpo_deviation"] = comm_merged["commission_per_order"] - mean_cpo

# Pre-format exact string labels to avoid Plotly number formatting bugs
comm_merged["cpo_text"] = comm_merged["commission_per_order"].apply(lambda x: f"€{x:,.2f}")
comm_merged["dev_text"] = comm_merged["cpo_deviation"].apply(lambda x: f"{x:+.2f}€")

col_d3, col_d4 = st.columns(2)

with col_d3:
    fig_cpo = px.bar(
        comm_merged.sort_values("commission_per_order"),
        x="commission_per_order", y="salesowner_name", orientation="h",
        text="cpo_text",  # Use pre-formatted text column
        color="commission_per_order",
        color_continuous_scale=["#10b981", "#34d399", "#6ee7b7", "#a7f3d0"],
        labels={"commission_per_order": "Commission per Order (€)", "salesowner_name": ""},
        title="Commission per Order (All-Time)"
    )
    fig_cpo.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False
    )
    # Give the axis 25% extra right padding dynamically based on data max
    fig_cpo.update_xaxes(range=[0, comm_merged["commission_per_order"].max() * 1.25])
    # Increased right margin to 90 to prevent '€36.41' from being clipped by the SVG boundary
    dark(fig_cpo, margin=dict(t=55, b=20, l=165, r=90))
    fig_cpo.update_coloraxes(showscale=False)
    st.plotly_chart(fig_cpo, use_container_width=True)

with col_d4:
    # Deviation chart
    df_sorted = comm_merged.sort_values("cpo_deviation")
    colors = ["#10b981" if val >= 0 else "#ef4444" for val in df_sorted["cpo_deviation"]]
    
    fig_dev = px.bar(
        df_sorted,
        x="cpo_deviation", y="salesowner_name", orientation="h",
        text="dev_text", # Use pre-formatted text column
        labels={"cpo_deviation": "Deviation from Mean (€)", "salesowner_name": ""},
        title=f"Deviation from Mean (€{mean_cpo:.2f})"
    )
    fig_dev.update_traces(
        marker_color=colors,
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False
    )
    # Symmetrically expand the axis by 30% based on the max deviation
    max_abs_dev = comm_merged["cpo_deviation"].abs().max()
    fig_dev.update_xaxes(range=[-max_abs_dev * 1.3, max_abs_dev * 1.3])
    # Increased right margin and left margin to prevent clipping on both extremes
    dark(fig_dev, margin=dict(t=55, b=20, l=165, r=100))
    fig_dev.add_vline(x=0, line_width=2, line_color="#4b5563", line_dash="dash")
    st.plotly_chart(fig_dev, use_container_width=True)

st.markdown("---")

# ── Role Distribution per Sales Owner ────────────────────────────────────────
st.markdown('<p class="section-sub" style="margin-top:1.5rem;">Role Distribution per Sales Owner</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub" style="font-size:0.75rem; margin-top:-0.5rem;">Proportion of orders where each salesperson acted as Main Owner vs Co-owner</p>', unsafe_allow_html=True)

# Create dynamic roles and colors based on max roles
max_co_owners = orders_exp["owner_rank"].max()
role_map = {0: "Main Owner"}
for i in range(1, max_co_owners + 1):
    role_map[i] = f"Co-owner {i}"

# Generate colors
base_colors = ["#3b82f6", "#f59e0b", "#22c55e", "#ef4444", "#a855f7", "#ec4899", "#8b5cf6"]
ROLE_COLORS = {role: base_colors[i % len(base_colors)] for i, role in role_map.items()}

role_df = orders_exp.copy()
role_df["role"] = role_df["owner_rank"].map(role_map)

# Calculate exactly 100% per person
role_counts = role_df.groupby(["salesowner", "role"]).size().reset_index(name="count")
totals = role_counts.groupby("salesowner")["count"].sum().reset_index(name="total")
role_pcts = pd.merge(role_counts, totals, on="salesowner")
role_pcts["pct"] = (role_pcts["count"] / role_pcts["total"]) * 100

# Sort owners by their % as Main Owner (for ordering the Y axis)
# Reversing the order so highest Main Owner % is at the top of the chart
main_data = role_pcts[role_pcts["role"] == "Main Owner"]
main_order = main_data.sort_values("pct", ascending=True)["salesowner"].tolist()

# Category order: Main Owner first, then Co-owner 1 -> Co-owner N
# This places Main Owner anchored to the left side (0%) of the bar.
category_roles = ["Main Owner"] + [f"Co-owner {i}" for i in range(1, max_co_owners + 1)]

fig_roles = go.Figure()

for role in category_roles:
    sub_df = role_pcts[role_pcts["role"] == role].set_index("salesowner").reindex(main_order).fillna(0)
    # Only show text if percentage is > 0 to avoid clutter
    text_labels = sub_df["pct"].apply(lambda x: f"{x:.1f}%" if x > 0 else "")
    
    fig_roles.add_trace(go.Bar(
        y=main_order,
        x=sub_df["pct"],        # Exact percentages
        name=role,
        orientation="h",
        marker_color=ROLE_COLORS.get(role, "#3b82f6"),
        text=text_labels,
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white")
    ))

fig_roles.update_layout(
    barmode="stack",
    xaxis_title="", 
    legend=dict(orientation="h", y=-0.2),
    bargap=0.3,
    title_text="",  # Remove undefined title
    annotations=[]  # Clear any hidden annotations
)
dark(fig_roles, margin=dict(t=20, b=50, l=140, r=20))
fig_roles.update_xaxes(ticksuffix="%", range=[0, 100], showgrid=False)
st.plotly_chart(fig_roles, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
# 8. SECTION E — COMPANY PORTFOLIO  (Bonus)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🏢 E · Company Portfolio Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Bonus — Company reach and geographic distribution</p>', unsafe_allow_html=True)

col_e1, col_e2 = st.columns(2)

with col_e1:
    companies["n_owners"] = companies["list_salesowners"].apply(
        lambda x: len(str(x).split(",")) if pd.notna(x) else 0
    )
    top_co = companies.sort_values("n_owners", ascending=False).head(20)
    fig_co = px.bar(
        top_co.sort_values("n_owners"),
        x="n_owners", y="company_name", orientation="h",
        color="n_owners", color_continuous_scale="Blues",
        title="Top 20 Companies by Number of Assigned Sales Owners",
        labels={"n_owners": "# Sales Owners", "company_name": ""},
        text="n_owners"
    )
    fig_co.update_traces(textposition="outside", textfont=dict(color=TEXT))
    dark(fig_co, margin=dict(t=55, b=20, l=185, r=60))
    fig_co.update_coloraxes(showscale=False)
    st.plotly_chart(fig_co, use_container_width=True)

with col_e2:
    city_data   = filt_orders["contact_address"].dropna()
    city_counts = (city_data[~city_data.str.startswith("Unknown")]
                   .apply(lambda x: x.split(",")[0].strip())
                   .value_counts().reset_index())
    city_counts.columns = ["city", "orders"]
    fig_city = px.bar(
        city_counts.head(15).sort_values("orders"),
        x="orders", y="city", orientation="h",
        color="orders", color_continuous_scale="Greens",
        title="Top 15 Cities by Order Volume",
        labels={"orders": "Orders", "city": ""},
        text="orders"
    )
    fig_city.update_traces(textposition="outside", textfont=dict(color=TEXT))
    dark(fig_city, margin=dict(t=55, b=20, l=145, r=60))
    fig_city.update_coloraxes(showscale=False)
    st.plotly_chart(fig_city, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 9. SECTION F — YEARLY TREND & SEASONALITY  (Bonus)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">📈 F · Order Trends & Seasonality</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Bonus — Year-over-year comparison and monthly seasonality by crate type</p>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns([3, 2])

with col_f1:
    tmp = filt_orders.copy()
    tmp["year"]   = tmp["date"].dt.year.astype(str)
    tmp["year_q"] = tmp["date"].dt.year.astype(str) + " Q" + tmp["date"].dt.quarter.astype(str)
    yoy = tmp.groupby(["year_q", "crate_type"]).size().reset_index(name="count").sort_values("year_q")
    fig_yoy = px.bar(
        yoy, x="year_q", y="count", color="crate_type",
        color_discrete_map=CRATE_COLORS, barmode="group",
        title="Quarterly Order Volume by Crate Type",
        labels={"year_q": "", "count": "Orders", "crate_type": "Type"}
    )
    dark(fig_yoy, legend_h=True, margin=dict(t=70, b=70, l=50, r=20))
    fig_yoy.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_yoy, use_container_width=True)

with col_f2:
    tmp2 = filt_orders.copy()
    tmp2["calendar_month"] = tmp2["date"].dt.month
    tmp2["month_name"]     = tmp2["date"].dt.strftime("%b")
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seasonality = (tmp2.groupby(["calendar_month","month_name","crate_type"])
                   .size().reset_index(name="count").sort_values("calendar_month"))
    fig_season = px.line_polar(
        seasonality, r="count", theta="month_name",
        color="crate_type", color_discrete_map=CRATE_COLORS,
        line_close=True, title="Seasonality Radar by Crate Type",
        category_orders={"month_name": month_order}
    )
    fig_season.update_traces(fill="toself", opacity=0.45)
    dark(fig_season, height=400, legend_h=True, margin=dict(t=70, b=55, l=20, r=20))
    fig_season.update_layout(
        polar=dict(
            bgcolor=BG,
            angularaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TEXT, size=11)),
            radialaxis=dict(gridcolor=GRID, linecolor=GRID, tickfont=dict(color=TEXT, size=9))
        )
    )
    st.plotly_chart(fig_season, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# 10. SECTION G — RAW DATA EXPLORER  (Bonus)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">🔬 G · Data Explorer</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Bonus — Explore the raw data tables directly</p>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Orders", "💰 Commissions", "🏢 Companies", "🧾 Invoicing"])
with tab1:
    cols_show = ["order_id","date","company_name","crate_type","contact_full_name","contact_address","salesowners"]
    st.dataframe(filt_orders[cols_show].sort_values("date", ascending=False).reset_index(drop=True),
                 use_container_width=True, height=320)
    st.caption(f"{len(filt_orders)} orders shown after filters")
with tab2:
    st.dataframe(commissions, use_container_width=True, height=320)
with tab3:
    st.dataframe(companies, use_container_width=True, height=320)
with tab4:
    st.dataframe(invoicing, use_container_width=True, height=320)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center; color:#9ca3af; font-size:0.73rem">'
    '📦 IFCO Data Engineering Challenge · Test 6 · Streamlit + Plotly'
    '</div>',
    unsafe_allow_html=True
)
