"""Streamlit UI: plot history and call the Flask forecast API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app_lib.config import RAW_GAS_CSV  # noqa: E402
from app_lib.events import (  # noqa: E402
    events_for_chart,
    kind_label,
    scope_label,
)
from app_lib.features import load_raw_prices  # noqa: E402
from app_lib.pipeline import EIA_LINKS, collect_from_eia, run_full_pipeline, train_models  # noqa: E402

# Plotly styling per marker type
_STYLE = {
    ("event", "us"): dict(color="#ea580c", symbol="diamond", size=12, textpos="top center"),
    ("event", "international"): dict(color="#7c3aed", symbol="diamond", size=12, textpos="top center"),
    ("peak", "us"): dict(color="#dc2626", symbol="triangle-up", size=14, textpos="top center"),
    ("peak", "international"): dict(color="#b91c1c", symbol="triangle-up", size=14, textpos="top center"),
    ("trough", "us"): dict(color="#059669", symbol="triangle-down", size=14, textpos="bottom center"),
    ("trough", "international"): dict(color="#047857", symbol="triangle-down", size=14, textpos="bottom center"),
}

_LEGEND_NAMES = {
    ("event", "us"): "U.S. events (diamond)",
    ("event", "international"): "Global events (diamond)",
    ("peak", "international"): "Price peaks (▲)",
    ("trough", "international"): "Price lows (▼)",
}


def _hover_html(ev, row: pd.Series) -> str:
    price = float(row["price"])
    return (
        f"<b>{ev['title']}</b><br>"
        f"{ev['detail']}<br>"
        f"<i>{kind_label(ev['kind'])} · {scope_label(ev['scope'])}</i><br>"
        f"EIA week: {row['period'].date()} · <b>{price:.3f} $/gal</b>"
    )


def _build_history_figure(
    raw: pd.DataFrame,
    show_events: bool,
    show_peaks: bool,
    show_troughs: bool,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=raw["period"],
            y=raw["price"],
            mode="lines",
            name="Retail (weekly)",
            line=dict(color="#1d4ed8", width=2),
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.3f} $/gal<extra></extra>",
        )
    )

    if not (show_events or show_peaks or show_troughs):
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=60),
            yaxis_title="$/gal",
            xaxis_title="Week",
            height=560,
            hovermode="x unified",
        )
        return fig

    grouped: dict[tuple, list] = {}
    for ev, row in events_for_chart(raw):
        if ev["kind"] == "event" and not show_events:
            continue
        if ev["kind"] == "peak" and not show_peaks:
            continue
        if ev["kind"] == "trough" and not show_troughs:
            continue
        key = (ev["kind"], ev["scope"])
        grouped.setdefault(key, []).append((ev, row))

    for key, items in grouped.items():
        style = _STYLE.get(key, _STYLE[("event", "international")])
        xs = [row["period"] for _, row in items]
        ys = [row["price"] for _, row in items]
        texts = [ev["title"] for ev, _ in items]
        hovers = [_hover_html(ev, row) for ev, row in items]
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                name=_LEGEND_NAMES.get(key, f"{key[0]} ({key[1]})"),
                text=texts,
                textposition=style["textpos"],
                textfont=dict(size=9),
                marker=dict(
                    size=style["size"],
                    color=style["color"],
                    symbol=style["symbol"],
                    line=dict(width=1, color="white"),
                ),
                hovertext=hovers,
                hovertemplate="%{hovertext}<extra></extra>",
            )
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=80),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="$/gal",
        xaxis_title="Week",
        height=560,
        hovermode="closest",
    )
    return fig


def _load_api_history(api_url: str) -> pd.DataFrame:
    resp = requests.get(f"{api_url.rstrip('/')}/data/history", timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("ok", True) and payload.get("error"):
        raise RuntimeError(payload["error"])
    raw = pd.DataFrame(payload["series"])
    raw["period"] = pd.to_datetime(raw["period"])
    raw["price"] = raw["price"].astype(float)
    return raw.sort_values("period").reset_index(drop=True)


def _load_api_metadata(api_url: str) -> dict:
    resp = requests.get(f"{api_url.rstrip('/')}/metadata", timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload


def _load_local_metadata() -> dict:
    meta_path = ROOT / "models" / "metadata.json"
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _load_display_history(api_url: str) -> tuple[pd.DataFrame, str]:
    try:
        return _load_api_history(api_url), "Flask API"
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Could not load history from Flask API, falling back to local CSV: {exc}")

    if not RAW_GAS_CSV.exists():
        st.warning(
            "No local price file yet. Use **Fetch EIA data & retrain models** in the sidebar "
            "(requires `EIA_API_KEY` in `.env` and the Flask API running)."
        )
        st.stop()
    return load_raw_prices(RAW_GAS_CSV), "local CSV fallback"


st.set_page_config(page_title="U.S. Gasoline Forecast", layout="wide")
st.title("U.S. weekly retail gasoline — history & forecast")

default_api = os.environ.get("MODEL_API_URL", "http://127.0.0.1:8080")
api_url = st.sidebar.text_input("Model API base URL", value=default_api)

st.sidebar.markdown("### EIA data (click links)")
st.sidebar.markdown(
    f"- [Open Data portal]({EIA_LINKS['portal']})\n"
    f"- [Get API key]({EIA_LINKS['register']})\n"
    f"- [API documentation]({EIA_LINKS['documentation']})\n"
    f"- [Gasoline series browser]({EIA_LINKS['gasoline_series_browser']})"
)
# On macOS, gunicorn + numpy/xgboost can 500 unless OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES (see scripts/run_api.sh)
_default_api_pipeline = sys.platform != "darwin"
use_api_pipeline = st.sidebar.checkbox(
    "Run refresh through Flask API",
    value=_default_api_pipeline,
    help="Controls refresh/training buttons only. The chart always tries to read history from Flask API first.",
)

if st.sidebar.button("Fetch EIA data & retrain models", type="primary"):
    with st.spinner("Downloading from EIA and retraining the deployed XGBoost model…"):
        try:
            if use_api_pipeline:
                resp = requests.post(
                    f"{api_url.rstrip('/')}/pipeline/run",
                    json={"require_eia_key": True},
                    timeout=300,
                )
                resp.raise_for_status()
                payload = resp.json()
                if not payload.get("ok", True) and payload.get("error"):
                    st.sidebar.error(payload["error"])
                else:
                    st.sidebar.success(payload.get("message", "Pipeline finished."))
                    st.rerun()
            else:
                out = run_full_pipeline(require_eia_key=True)
                st.sidebar.success(out["message"])
                st.rerun()
        except requests.RequestException as exc:
            st.sidebar.error(
                f"API call failed: {exc}. "
                "On Mac: uncheck **Run refresh through Flask API**, or restart the API with "
                "`bash scripts/run_api.sh` (fixes gunicorn fork crashes). "
                "Training can take 1–2 minutes — keep the page open."
            )
        except Exception as exc:  # noqa: BLE001
            st.sidebar.error(str(exc))

col_p1, col_p2 = st.sidebar.columns(2)
with col_p1:
    if st.button("EIA only", help="Download CSV only"):
        try:
            if use_api_pipeline:
                r = requests.post(f"{api_url.rstrip('/')}/data/collect", timeout=120)
                r.raise_for_status()
                st.sidebar.success(r.json().get("message", "Done"))
            else:
                st.sidebar.success(collect_from_eia(require_key=True)["message"])
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.sidebar.error(str(exc))
with col_p2:
    if st.button("Train only", help="Retrain deployed XGBoost on the existing API CSV"):
        try:
            if use_api_pipeline:
                r = requests.post(f"{api_url.rstrip('/')}/models/train", timeout=300)
                r.raise_for_status()
                st.sidebar.success(r.json().get("message", "Done"))
            else:
                st.sidebar.success(train_models()["message"])
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.sidebar.error(str(exc))

st.sidebar.markdown("---")

forecast_method = st.sidebar.selectbox(
    "Forecast method",
    options=["XGBoost", "SARIMA"],
    index=0,
    help="XGBoost: lag + calendar features, recursive steps. SARIMA: univariate weekly time series.",
)
method_api = forecast_method.lower()
horizon = st.sidebar.slider("Forecast horizon (weeks)", 1, 26, 8)

st.sidebar.markdown("**Chart annotations**")
show_events = st.sidebar.checkbox("News & shocks (U.S. + global)", value=True)
show_peaks = st.sidebar.checkbox("Price peaks ▲", value=True)
show_troughs = st.sidebar.checkbox("Price lows ▼", value=True)

try:
    _meta = _load_api_metadata(api_url)
except Exception as exc:  # noqa: BLE001
    st.sidebar.warning(f"Could not load API metadata: {exc}")
    _meta = _load_local_metadata()

_mm = _meta.get("models", {}).get(method_api, {})
if _mm:
    st.sidebar.caption(
        f"Holdout MAE ({forecast_method}): **{_mm.get('validation_mae', 0):.4f}** $/gal  \n"
        f"Holdout RMSE: **{_mm.get('validation_rmse', 0):.4f}** $/gal"
    )
    if method_api == "sarima" and _mm.get("model_spec"):
        st.sidebar.caption(f"Fitted: `{_mm['model_spec']}`")

raw, data_source_label = _load_display_history(api_url)

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Latest observation", f"{raw['price'].iloc[-1]:.3f} $/gal")
with col_b:
    st.metric("As of", str(raw["period"].iloc[-1].date()))
st.caption(f"Historical data source: {data_source_label}")

st.subheader("Historical series")
st.plotly_chart(
    _build_history_figure(raw, show_events, show_peaks, show_troughs),
    use_container_width=True,
)

with st.expander("Annotation legend & sources"):
    st.markdown(
        """
| Symbol | Meaning |
|--------|---------|
| ◆ Orange | U.S.-focused supply or infrastructure (hurricanes, Colonial Pipeline) |
| ◆ Purple | Global oil / geopolitics / OPEC / pandemic / war |
| ▲ Red | Local **high** on the national weekly series (snapped to peak in ±12 weeks) |
| ▼ Green | Local **low** on the national weekly series |

Markers are **illustrative context** for presentations—not proof that one event alone caused a price move.
        """
    )

if st.sidebar.button("Get forecast"):
    try:
        r = requests.post(
            f"{api_url.rstrip('/')}/predict",
            json={"horizon": horizon, "method": method_api},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            st.error(data["error"])
        else:
            fc = pd.DataFrame(data["forecasts"])
            fc["period"] = pd.to_datetime(fc["period"])
            label = data.get("method_label", forecast_method)
            st.subheader(f"Forecast — {label}")
            if data.get("validation_mae") is not None:
                st.caption(
                    f"Holdout MAE: {data['validation_mae']:.4f} $/gal · "
                    f"RMSE: {data.get('validation_rmse', 0):.4f} $/gal"
                )
            ffig = go.Figure()
            ffig.add_trace(
                go.Scatter(
                    x=raw["period"],
                    y=raw["price"],
                    mode="lines",
                    name="History",
                    line=dict(color="#64748b", width=2),
                )
            )
            ffig.add_trace(
                go.Scatter(
                    x=fc["period"],
                    y=fc["forecast_price"],
                    mode="lines+markers",
                    name=f"Forecast ({forecast_method})",
                    line=dict(color="#16a34a", width=2, dash="dash"),
                    marker=dict(size=6),
                )
            )
            ffig.update_layout(
                yaxis_title="$/gal",
                xaxis_title="Week",
                height=420,
                legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
            )
            st.plotly_chart(ffig, use_container_width=True)
            st.dataframe(fc, use_container_width=True)
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")

st.sidebar.markdown("---")
st.sidebar.caption("Data: EIA Open Data when `EIA_API_KEY` is set.")
