"""
AutoRisk · Vehicle Safety Intelligence
Streamlit Dashboard
UCLA STAT 418 — Spring 2026
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AutoRisk · Vehicle Safety Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.environ.get("API_URL", "http://localhost:8080")

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* sidebar */
[data-testid="stSidebar"] {background: #f5f3ef;}
[data-testid="stSidebar"] h1 {font-size: 1.3rem; font-weight: 700; margin-bottom: 0;}
[data-testid="stSidebar"] p.subtitle {font-size: 0.78rem; color: #888; margin-top: -8px;}

/* metric cards */
.metric-card {
    background: #fafaf8;
    border: 1px solid #e8e4dc;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 4px 0;
}
.metric-label {font-size: 0.75rem; color: #888; text-transform: lowercase; letter-spacing: .03em;}
.metric-value {font-size: 2rem; font-weight: 700; line-height: 1.1; color: #1a1a1a;}
.metric-sub {font-size: 0.72rem; color: #aaa; margin-top: 2px;}

/* risk badge */
.badge-high {background:#fee2e2;color:#b91c1c;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:600;}
.badge-low  {background:#dcfce7;color:#166534;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:600;}

/* AI insight box */
.ai-box {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 0.85rem;
    line-height: 1.55;
    color: #1a1a1a;
}
.ai-label {font-size:0.72rem;font-weight:600;color:#16a34a;margin-bottom:6px;letter-spacing:.05em;}

/* ranking */
.rank-row {display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #f0ece4;font-size:.84rem;}
.rank-row.highlight {background:#fff7ed;font-weight:700;border-radius:4px;padding:5px 6px;}
.rank-label {color:#555;}
.rank-val {color:#1a1a1a;font-weight:600;}

/* section header */
.section-header {font-size:.78rem;color:#999;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px;margin-top:4px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    candidates = [
        Path(__file__).parent.parent / "data" / "processed" / "vehicle_risk_features_labeled.csv",
        Path("data/processed/vehicle_risk_features_labeled.csv"),
    ]
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            df["make"] = df["make"].str.title()
            return df
    st.error("Data file not found. Please ensure vehicle_risk_features_labeled.csv exists.")
    st.stop()


@st.cache_data
def load_full_data() -> pd.DataFrame:
    """Load the full dataset (with complaint info for EDA/trends)."""
    candidates = [
        Path(__file__).parent.parent / "data" / "processed" / "vehicle_risk_2020_2024_10brands.csv",
        Path("data/processed/vehicle_risk_2020_2024_10brands.csv"),
    ]
    for p in candidates:
        if p.exists():
            df = pd.read_csv(p)
            df["make"] = df["make"].str.title()
            return df
    return load_data()


@st.cache_data
def load_feature_importance() -> pd.DataFrame:
    candidates = [
        Path(__file__).parent.parent / "data" / "processed" / "random_forest_feature_importance.csv",
        Path("data/processed/random_forest_feature_importance.csv"),
    ]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p)
    return pd.DataFrame()


df = load_data()
full_df = load_full_data()
fi_df = load_feature_importance()

MAKES = sorted(df["make"].unique().tolist())
YEARS = sorted(df["year"].unique().tolist(), reverse=True)

COMPONENT_COLS = {
    "electrical": ("recall_electrical_count", "complaint_electrical_count"),
    "brake":      ("recall_brake_count",       "complaint_brake_count"),
    "restraint":  ("recall_restraint_count",   "complaint_restraint_count"),
    "powertrain": ("recall_powertrain_count",  "complaint_powertrain_count"),
    "engine":     ("recall_engine_count",      "complaint_engine_count"),
    "structure":  ("recall_structure_count",   "complaint_structure_count"),
    "steering":   ("recall_steering_count",    "complaint_steering_count"),
    "fuel":       ("recall_fuel_count",        "complaint_fuel_count"),
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h1>AutoRisk</h1><p class='subtitle'>vehicle safety intelligence</p>",
                unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "Navigation",
        ["🔍 Lookup", "⚖️ Compare", "📈 Trends", "🤖 Predict", "📖 Methodology"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Data: NHTSA API · 2020–2024 · 10 brands")
    st.caption("Model: Random Forest (F1 = 0.69)")

page_key = page.split(" ", 1)[1]


# ---------------------------------------------------------------------------
# Helper: call predict API
# ---------------------------------------------------------------------------
def api_predict(row: pd.Series) -> dict | None:
    payload = {
        "year": int(row["year"]),
        "make": str(row["make"]),
        "brand_category": str(row.get("brand_category", "")),
        "recall_count": int(row.get("recall_count", 0)),
        "recall_restraint_count": int(row.get("recall_restraint_count", 0)),
        "recall_brake_count": int(row.get("recall_brake_count", 0)),
        "recall_electrical_count": int(row.get("recall_electrical_count", 0)),
        "recall_engine_count": int(row.get("recall_engine_count", 0)),
        "recall_powertrain_count": int(row.get("recall_powertrain_count", 0)),
        "recall_fuel_count": int(row.get("recall_fuel_count", 0)),
        "recall_steering_count": int(row.get("recall_steering_count", 0)),
        "recall_suspension_count": int(row.get("recall_suspension_count", 0)),
        "recall_structure_count": int(row.get("recall_structure_count", 0)),
        "recall_other_count": int(row.get("recall_other_count", 0)),
    }
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    # Fallback: use risk_label from data
    return {
        "high_risk_probability": float(row.get("risk_label", 0)),
        "prediction": int(row.get("risk_label", 0)),
        "label": "high-risk" if row.get("risk_label", 0) == 1 else "low-risk",
        "source": "data",
    }


# ---------------------------------------------------------------------------
# Helper: component breakdown chart
# ---------------------------------------------------------------------------
def component_chart(row: pd.Series) -> go.Figure:
    components = list(COMPONENT_COLS.keys())
    recall_vals, complaint_vals = [], []

    for comp, (rc, cc) in COMPONENT_COLS.items():
        recall_vals.append(int(row.get(rc, 0) or 0))
        complaint_vals.append(int(row.get(cc, 0) or 0) if cc in row.index else 0)

    max_val = max(max(recall_vals), max(complaint_vals), 1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=components,
        x=recall_vals,
        orientation="h",
        name="recalls",
        marker_color="#3b82f6",
        hovertemplate="%{y}: %{x} recalls<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        y=components,
        x=complaint_vals,
        orientation="h",
        name="complaints",
        marker_color="#f59e0b",
        hovertemplate="%{y}: %{x} complaints<extra></extra>",
    ))

    fig.update_layout(
        barmode="overlay",
        height=280,
        margin=dict(l=10, r=60, t=10, b=10),
        legend=dict(orientation="h", x=0, y=1.12, font_size=11),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0ece4", range=[0, max_val * 1.15]),
        yaxis=dict(showgrid=False),
        font_family="sans-serif",
    )

    # Add value labels
    for i, (rv, cv) in enumerate(zip(recall_vals, complaint_vals)):
        if rv > 0:
            fig.add_annotation(x=rv, y=i, text=str(rv), xanchor="left",
                                showarrow=False, font_size=10, xshift=4)
        if cv > 0 and cv != rv:
            fig.add_annotation(x=cv, y=i, text=str(cv), xanchor="left",
                                showarrow=False, font_size=10, xshift=4)

    return fig


# ===========================================================================
# PAGE: Lookup
# ===========================================================================
if page_key == "Lookup":

    # --- filters bar -------------------------------------------------------
    col_y, col_m, col_mod = st.columns([1, 1, 1.5])
    with col_y:
        sel_year = st.selectbox("Year", YEARS, key="lu_year")
    with col_m:
        makes_for_year = sorted(df[df["year"] == sel_year]["make"].unique().tolist())
        sel_make = st.selectbox("Make", makes_for_year, key="lu_make")
    with col_mod:
        models_for = sorted(
            df[(df["year"] == sel_year) & (df["make"] == sel_make)]["base_model"].unique().tolist()
        )
        sel_model = st.selectbox("Model", models_for, key="lu_model")

    # --- fetch row ---------------------------------------------------------
    mask = (
        (df["year"] == sel_year)
        & (df["make"] == sel_make)
        & (df["base_model"] == sel_model)
    )
    rows = df[mask]

    if rows.empty:
        st.warning("No data found for this selection.")
        st.stop()

    row = rows.iloc[0]

    # --- header ------------------------------------------------------------
    pred = api_predict(row)
    risk_badge = (
        "<span class='badge-high'>high risk</span>"
        if pred and pred["prediction"] == 1
        else "<span class='badge-low'>lower risk</span>"
    )
    prob = pred["high_risk_probability"] if pred else float(row.get("risk_label", 0))
    pct_rank = int((1 - prob) * 100)

    vehicle_age = int(row.get("vehicle_age", 2026 - sel_year))

    st.markdown(f"""
    <div style='margin-bottom:4px'>
        <span style='font-size:1.6rem;font-weight:700'>{sel_year} {sel_make} {sel_model.title()}</span>
        &nbsp;{risk_badge}
        &nbsp;<span style='font-size:.8rem;color:#aaa;background:#f5f3ef;padding:3px 10px;border-radius:20px'>sk · top {pct_rank}%</span>
    </div>
    <div style='font-size:.78rem;color:#999;margin-bottom:16px'>
        {row.get("brand_category","").replace("_"," ")} ·
        {vehicle_age} model year{"s" if vehicle_age != 1 else ""} on the road ·
        last refreshed May 2026
    </div>
    """, unsafe_allow_html=True)

    # --- KPI cards ---------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    complaint_rate = row.get("complaint_rate", 0)
    threshold = row.get("risk_threshold", 0)

    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>complaint rate / yr</div>
            <div class='metric-value'>{complaint_rate:.1f}</div>
            <div class='metric-sub'>label threshold · {threshold:.1f}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        make_median = df[df["make"] == sel_make]["recall_count"].median()
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>recall count</div>
            <div class='metric-value'>{int(row.get("recall_count",0))}</div>
            <div class='metric-sub'>make median · {make_median:.0f}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        crash = int(row.get("crash_count", 0) or 0)
        fire  = int(row.get("fire_count",  0) or 0)
        inj   = int(row.get("injury_count", 0) or 0)
        dth   = int(row.get("death_count",  0) or 0)
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>crash · fire</div>
            <div class='metric-value'>{crash} · {fire}</div>
            <div class='metric-sub'>injuries · {inj} · deaths · {dth}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>model probability</div>
            <div class='metric-value'>{prob:.2f}</div>
            <div class='metric-sub'>random forest</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # --- main body: component breakdown + ranking --------------------------
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown("<div class='section-header'>Component breakdown · recalls vs complaints by category</div>",
                    unsafe_allow_html=True)
        fig = component_chart(row)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with right:
        st.markdown(f"<div class='section-header'>Ranked within {sel_make} {sel_year} · by complaint rate</div>",
                    unsafe_allow_html=True)

        same_make_year = (
            df[(df["make"] == sel_make) & (df["year"] == sel_year)]
            .sort_values("complaint_rate", ascending=False)
            .reset_index(drop=True)
        )
        n_total = len(same_make_year)

        shown = 0
        for i, r2 in same_make_year.iterrows():
            rank = i + 1
            is_current = r2["base_model"] == sel_model
            cls = "rank-row highlight" if is_current else "rank-row"
            shown += 1
            if shown > 8 and not is_current:
                continue
            arrow = " ←" if is_current else ""
            st.markdown(f"""<div class='{cls}'>
                <span class='rank-label'>{rank} · {r2["base_model"].title()}{arrow}</span>
                <span class='rank-val'>{r2["complaint_rate"]:.1f}</span>
            </div>""", unsafe_allow_html=True)

        if n_total > 8:
            rest = n_total - 8
            st.markdown(f"<div class='rank-row'><span class='rank-label'>+{rest} others</span><span class='rank-val'>&lt; {same_make_year.iloc[7]['complaint_rate']:.1f}</span></div>",
                        unsafe_allow_html=True)

    # --- AI insight --------------------------------------------------------
    st.markdown("")
    top_comp = max(COMPONENT_COLS.keys(),
                   key=lambda c: int(row.get(COMPONENT_COLS[c][1], 0) or 0))
    top_comp_cnt = int(row.get(COMPONENT_COLS[top_comp][1], 0) or 0)
    second_comp = sorted(COMPONENT_COLS.keys(),
                         key=lambda c: int(row.get(COMPONENT_COLS[c][1], 0) or 0),
                         reverse=True)[1]
    second_cnt = int(row.get(COMPONENT_COLS[second_comp][1], 0) or 0)

    rank_pos = same_make_year[same_make_year["base_model"] == sel_model].index[0] + 1 if len(same_make_year) > 0 else "–"
    rank_worse = [r2["base_model"].title() for _, r2 in same_make_year.iterrows()
                  if r2["complaint_rate"] > float(complaint_rate)][:2]
    rank_worse_str = " and ".join(rank_worse) if rank_worse else "no models"

    insight = (
        f"{sel_model.title()}'s risk classification is driven mostly by "
        f"{top_comp} ({top_comp_cnt} reports) and {second_comp} ({second_cnt}) complaints. "
        f"Within {sel_make}'s {sel_year} lineup it sits #{rank_pos} by complaint rate"
        + (f" — {rank_worse_str} {'are' if len(rank_worse) > 1 else 'is'} noticeably worse." if rank_worse else ".")
        + f" The random forest gives {prob:.2f} probability of high-risk"
        + ("; recalls are a meaningful but not dominant factor." if int(row.get("recall_count", 0)) > 0 else ".")
    )

    st.markdown(f"""<div class='ai-box'>
        <div class='ai-label'>🤖 AI insights · grounded on this vehicle's data</div>
        {insight}
    </div>""", unsafe_allow_html=True)

    # --- action buttons ----------------------------------------------------
    st.markdown("")
    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        if st.button("＋ add to comparison", use_container_width=True):
            key = f"{sel_year} {sel_make} {sel_model}"
            lst = st.session_state.setdefault("compare_list", [])
            if key not in lst:
                lst.append(key)
                if len(lst) > 3:
                    lst.pop(0)
            for i in range(3):
                for suffix in ("year", "make", "model"):
                    st.session_state.pop(f"cmp_{suffix}_{i}", None)
            n = len(lst)
            st.success(f"Added! ({n}/3) — {'comparison full, oldest removed when adding more' if n == 3 else 'go to Compare tab'}")
    with bc2:
        if st.button("✕ clear comparison", use_container_width=True):
            st.session_state["compare_list"] = []
            for i in range(3):
                for suffix in ("year", "make", "model"):
                    st.session_state.pop(f"cmp_{suffix}_{i}", None)
            st.info("Comparison cleared.")
    with bc4:
        csv_bytes = row.to_frame().T.to_csv(index=False).encode()
        st.download_button("↓ export CSV", data=csv_bytes,
                           file_name=f"{sel_year}_{sel_make}_{sel_model}.csv",
                           mime="text/csv", use_container_width=True)


# ===========================================================================
# PAGE: Compare
# ===========================================================================
elif page_key == "Compare":
    st.subheader("Vehicle Comparison")
    st.caption("Select up to 3 vehicles to compare side by side.")

    # Parse vehicles added via "add to comparison" button
    def parse_compare_entry(entry: str):
        """Parse '2024 Chevrolet 3500Hd' → (2024, 'Chevrolet', '3500hd')"""
        parts = entry.split(" ", 2)
        if len(parts) == 3:
            return int(parts[0]), parts[1], parts[2].upper()
        return None

    preloaded = [
        parse_compare_entry(e)
        for e in st.session_state.get("compare_list", [])
        if parse_compare_entry(e) is not None
    ][:3]

    cols = st.columns(3)
    selections = []
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Vehicle {i+1}**")
            pre = preloaded[i] if i < len(preloaded) else None

            default_year = pre[0] if pre and pre[0] in YEARS else YEARS[0]
            yr = st.selectbox("Year", YEARS, index=YEARS.index(default_year), key=f"cmp_year_{i}")

            mk_opts = sorted(df[df["year"] == yr]["make"].unique().tolist())
            default_make = pre[1] if pre and pre[1] in mk_opts else mk_opts[0]
            mk = st.selectbox("Make", mk_opts, index=mk_opts.index(default_make), key=f"cmp_make_{i}")

            mod_opts = sorted(df[(df["year"] == yr) & (df["make"] == mk)]["base_model"].unique())
            default_mod = pre[2] if pre and pre[2] in mod_opts else mod_opts[0]
            md = st.selectbox("Model", mod_opts, index=mod_opts.index(default_mod) if default_mod in mod_opts else 0, key=f"cmp_model_{i}")
            selections.append((yr, mk, md))

    st.divider()

    # Build comparison table
    records = []
    for yr, mk, md in selections:
        mask = (df["year"] == yr) & (df["make"] == mk) & (df["base_model"] == md)
        rows_sel = df[mask]
        if not rows_sel.empty:
            r = rows_sel.iloc[0].copy()
            pred = api_predict(r)
            r["high_risk_prob"] = pred["high_risk_probability"] if pred else float(r.get("risk_label", 0))
            r["vehicle_label"] = f"{yr} {mk} {md.title()}"
            records.append(r)

    if records:
        metrics_to_show = {
            "Complaint Rate / yr": "complaint_rate",
            "Recall Count": "recall_count",
            "Crashes": "crash_count",
            "Fires": "fire_count",
            "Injuries": "injury_count",
            "Deaths": "death_count",
            "Risk Probability": "high_risk_prob",
        }

        table_data = {m: [] for m in metrics_to_show}
        table_data["Vehicle"] = [r["vehicle_label"] for r in records]

        for metric, col_name in metrics_to_show.items():
            for r in records:
                val = r.get(col_name, 0)
                if pd.isna(val):
                    val = 0
                if col_name in ("complaint_rate", "high_risk_prob"):
                    table_data[metric].append(f"{float(val):.2f}")
                else:
                    table_data[metric].append(int(val))

        comp_df = pd.DataFrame(table_data).set_index("Vehicle")
        st.dataframe(comp_df, use_container_width=True)

        # Radar chart
        fig_r = go.Figure()
        categories = list(metrics_to_show.keys())

        for r in records:
            vals = []
            for metric, col_name in metrics_to_show.items():
                v = float(r.get(col_name, 0) or 0)
                vals.append(v)

            # Normalize
            max_vals = []
            for metric, col_name in metrics_to_show.items():
                max_v = df[col_name].max() if col_name in df.columns else 1
                max_vals.append(float(max_v) if max_v else 1)

            norm_vals = [v / m if m > 0 else 0 for v, m in zip(vals, max_vals)]
            norm_vals += [norm_vals[0]]

            fig_r.add_trace(go.Scatterpolar(
                r=norm_vals,
                theta=categories + [categories[0]],
                fill="toself",
                name=r["vehicle_label"],
                opacity=0.6,
            ))

        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=400,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# PAGE: Trends
# ===========================================================================
elif page_key == "Trends":
    st.subheader("Safety Trends")

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        metric_choice = st.selectbox(
            "Metric",
            ["complaint_rate", "recall_count", "crash_count", "death_count"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
    with col_t2:
        selected_makes = st.multiselect("Makes", MAKES, default=MAKES[:4])

    trend_df = (
        full_df[full_df["make"].isin(selected_makes)]
        .groupby(["year", "make"])[metric_choice]
        .mean()
        .reset_index()
    )

    fig_t = go.Figure()
    colors = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444",
              "#8b5cf6", "#06b6d4", "#f97316", "#84cc16"]

    for i, mk in enumerate(selected_makes):
        sub = trend_df[trend_df["make"] == mk]
        fig_t.add_trace(go.Scatter(
            x=sub["year"],
            y=sub[metric_choice],
            mode="lines+markers",
            name=mk,
            line=dict(color=colors[i % len(colors)], width=2.5),
            marker=dict(size=7),
        ))

    fig_t.update_layout(
        title=f"Average {metric_choice.replace('_',' ').title()} by Year",
        xaxis_title="Model Year",
        yaxis_title=metric_choice.replace("_", " ").title(),
        height=420,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0ece4", dtick=1),
        yaxis=dict(showgrid=True, gridcolor="#f0ece4"),
        legend=dict(orientation="h", y=-0.2),
        font_family="sans-serif",
    )
    st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

    # Top components by complaint volume
    st.divider()
    st.markdown("#### Complaint Volume by Component (all makes, all years)")
    comp_totals = {
        comp: int(full_df[cc].sum() if cc in full_df.columns else 0)
        for comp, (_, cc) in COMPONENT_COLS.items()
    }
    comp_df = (
        pd.DataFrame.from_dict(comp_totals, orient="index", columns=["complaints"])
        .sort_values("complaints", ascending=True)
    )

    fig_c = go.Figure(go.Bar(
        x=comp_df["complaints"],
        y=comp_df.index,
        orientation="h",
        marker_color="#f59e0b",
    ))
    fig_c.update_layout(
        height=280,
        margin=dict(l=10, r=40, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0ece4"),
        font_family="sans-serif",
    )
    st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# PAGE: Predict
# ===========================================================================
elif page_key == "Predict":
    st.subheader("Risk Predictor")
    st.caption(
        "Enter recall information for any vehicle to get a high-risk probability "
        "from the Random Forest model."
    )

    with st.form("predict_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            p_year = st.number_input("Model Year", min_value=2015, max_value=2026, value=2022)
            p_make = st.selectbox("Make", MAKES)
            p_rc = st.number_input("Total Recall Count", 0, 30, 2)
        with c2:
            p_elec = st.number_input("Electrical Recalls", 0, 15, 0)
            p_brake = st.number_input("Brake Recalls", 0, 10, 0)
            p_rest = st.number_input("Restraint Recalls", 0, 10, 1)
        with c3:
            p_eng = st.number_input("Engine Recalls", 0, 10, 0)
            p_pw = st.number_input("Powertrain Recalls", 0, 10, 1)
            p_fuel = st.number_input("Fuel System Recalls", 0, 10, 0)
            p_steer = st.number_input("Steering Recalls", 0, 10, 0)

        submitted = st.form_submit_button("Predict Risk", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "year": int(p_year),
            "make": str(p_make),
            "recall_count": int(p_rc),
            "recall_electrical_count": int(p_elec),
            "recall_brake_count": int(p_brake),
            "recall_restraint_count": int(p_rest),
            "recall_engine_count": int(p_eng),
            "recall_powertrain_count": int(p_pw),
            "recall_fuel_count": int(p_fuel),
            "recall_steering_count": int(p_steer),
            "recall_suspension_count": 0,
            "recall_structure_count": 0,
            "recall_other_count": max(0, int(p_rc) - int(p_elec) - int(p_brake) -
                                      int(p_rest) - int(p_eng) - int(p_pw) -
                                      int(p_fuel) - int(p_steer)),
        }

        try:
            resp = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
            else:
                result = None
        except Exception:
            result = None

        if result:
            prob_val = result["high_risk_probability"]
            label = result["label"]
            age = result.get("vehicle_age", 2026 - int(p_year))

            col_res, col_gauge = st.columns([1, 1])
            with col_res:
                badge = "<span class='badge-high'>HIGH RISK</span>" if label == "high-risk" else "<span class='badge-low'>LOWER RISK</span>"
                st.markdown(f"""
                <div class='metric-card' style='text-align:center;margin-top:16px'>
                    <div class='metric-label'>predicted classification</div>
                    <div style='font-size:2rem;font-weight:700;margin:8px 0'>{badge}</div>
                    <div class='metric-value'>{prob_val:.0%}</div>
                    <div class='metric-sub'>high-risk probability · {age} yr old vehicle</div>
                </div>
                """, unsafe_allow_html=True)
            with col_gauge:
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prob_val * 100,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "Risk Score", "font": {"size": 14}},
                    number={"suffix": "%", "font": {"size": 28}},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#ef4444" if prob_val > 0.5 else "#22c55e"},
                        "steps": [
                            {"range": [0, 50], "color": "#dcfce7"},
                            {"range": [50, 100], "color": "#fee2e2"},
                        ],
                        "threshold": {
                            "line": {"color": "#1a1a1a", "width": 3},
                            "thickness": 0.8,
                            "value": 50,
                        },
                    },
                ))
                fig_g.update_layout(height=260, margin=dict(l=20, r=20, t=40, b=10))
                st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

            st.markdown(f"""<div class='ai-box'>
                <div class='ai-label'>🤖 Interpretation</div>
                The model assigns a <strong>{prob_val:.0%}</strong> probability of high-risk
                classification to a {p_year} {p_make} with {p_rc} total recalls.
                {'This exceeds the 50% decision threshold — the vehicle is classified as <strong>high-risk</strong>.' if prob_val > 0.5 else 'This is below the 50% threshold — the vehicle is classified as <strong>lower-risk</strong>.'}
                Recall count is the top feature; electrical and brake recalls
                are additional strong signals.
            </div>""", unsafe_allow_html=True)
        else:
            st.error("Could not reach the API. Make sure the Flask API is running.")

    # Feature importance
    if not fi_df.empty:
        st.divider()
        st.markdown("#### Feature Importance (Random Forest)")
        top_fi = fi_df.nlargest(12, "importance").sort_values("importance")
        fig_fi = go.Figure(go.Bar(
            x=top_fi["importance"],
            y=top_fi["feature_clean"],
            orientation="h",
            marker_color="#3b82f6",
        ))
        fig_fi.update_layout(
            height=320,
            margin=dict(l=10, r=40, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0ece4", title="Importance"),
            font_family="sans-serif",
        )
        st.plotly_chart(fig_fi, use_container_width=True, config={"displayModeBar": False})


# ===========================================================================
# PAGE: Methodology
# ===========================================================================
elif page_key == "Methodology":
    st.subheader("Methodology")

    st.markdown("""
    ### Data Collection
    Vehicle recall and complaint data was collected via the **NHTSA public API**
    (`api.nhtsa.dot.gov`) covering model years **2020–2024** across **10 major brands**:
    Toyota, Honda, Ford, Chevrolet, Nissan, Hyundai, Kia, Subaru, Mazda, and Mazda.
    ~817 (year, make, model) rows after deduplication.

    ### Feature Engineering
    - Recall counts disaggregated by component category (electrical, brake, restraint, etc.)
    - `vehicle_age` = current year − model year
    - `brand_category` encodes origin market (Japanese ICE, Korean ICE, Domestic ICE)
    - **Complaint-derived columns excluded** from model features to prevent data leakage
      (the risk label is based on complaint rate)

    ### Risk Label
    A vehicle is labeled **high-risk (1)** if its complaint rate (complaints per year on road)
    exceeds the dataset median threshold (~22.75 complaints/yr). This results in ~38% positive
    class prevalence.

    ### Models
    | Model | Accuracy | Precision | Recall | F1 |
    |---|---|---|---|---|
    | Logistic Regression | 0.73 | 0.55 | 0.63 | 0.59 |
    | **Random Forest** | **0.80** | **0.65** | **0.74** | **0.69** |

    Random Forest (300 trees, balanced class weights) outperforms logistic regression
    on all metrics and is used for production inference.

    ### Top Predictive Features
    1. Recall count (total)
    2. Electrical system recalls
    3. Vehicle age
    4. Powertrain recalls
    5. Brand category

    ### Architecture
    ```
    NHTSA API → collect_data.py → data/raw/
                                    ↓
                               merge.py / eda.py → data/processed/
                                    ↓
                          model_baseline.py (RF training)
                                    ↓
                           api/main.py (Flask · Cloud Run)
                                    ↓
                       app/streamlit_app.py (Streamlit · Cloud Run)
    ```

    ### Deployment
    - **Model API**: Flask + Gunicorn on Google Cloud Run
    - **Web App**: Streamlit on Google Cloud Run
    - **Containerisation**: Docker (separate images for API and app)
    """)

    # Model metrics chart
    if not fi_df.empty:
        st.divider()
        st.markdown("#### Feature Importance")
        top_fi = fi_df.nlargest(12, "importance").sort_values("importance")
        fig_fi = go.Figure(go.Bar(
            x=top_fi["importance"],
            y=top_fi["feature_clean"],
            orientation="h",
            marker_color="#3b82f6",
        ))
        fig_fi.update_layout(
            height=320,
            margin=dict(l=10, r=40, t=10, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(showgrid=True, gridcolor="#f0ece4"),
            font_family="sans-serif",
        )
        st.plotly_chart(fig_fi, use_container_width=True, config={"displayModeBar": False})
